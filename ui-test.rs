#!/usr/bin/env rust

// Runs the UI suite on every lane and prints one summary at the end.
//
// Desktop debug and desktop release share the default cargo target, so they run
// one after another. The iOS simulator lane uses its own target dir and runs
// alongside them on its own task. Each lane streams its own output, the iOS lane
// deliberately quiet, and the counts are gathered into a single table at the end.
//
// Every lane's full output also lands in target/ui-test/<lane>.log, and each
// failure report in target/ui-test/failures/<lane>/<test>.txt, so a failed run
// can be read back without running it again.

use std::fs::{File, create_dir_all, remove_dir_all, write};
use std::io::{BufRead, BufReader, Write};
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};

use anyhow::Result;
use regex::Regex;

const LOG_DIR: &str = "target/ui-test";

struct Lane {
    name: String,
    passed: i64,
    failed: i64,
    ok: bool,
    log: PathBuf,
    /// Failed test names with the path of the saved report.
    failures: Vec<(String, PathBuf)>,
}

fn slug(name: &str) -> String {
    name.trim().replace(' ', "_")
}

/// Streams a command's output live, writes it to `log` and captures it, so a
/// lane stays watchable, survives on disk and its result line can still be
/// parsed afterwards.
fn tee(command: &str, log: &Path) -> Result<(String, bool)> {
    let mut file = File::create(log)?;
    let mut child = Command::new("sh")
        .arg("-c")
        .arg(format!("{command} 2>&1"))
        .stdout(Stdio::piped())
        .spawn()?;
    let stdout = child.stdout.take().unwrap();
    let mut output = String::new();
    for line in BufReader::new(stdout).lines() {
        let line = line?;
        println!("{line}");
        writeln!(file, "{line}")?;
        output.push_str(&line);
        output.push('\n');
    }
    let status = child.wait()?;
    Ok((output, status.success()))
}

/// A failed test's report starts with a header line, "===== Name =====" from
/// the desktop runner and "TEST FAILED: Name" from an app on a device.
fn failure_header(line: &str) -> Option<&str> {
    line.strip_prefix("===== ")
        .and_then(|rest| rest.strip_suffix(" ====="))
        .or_else(|| line.strip_prefix("TEST FAILED: "))
}

/// The runner prints one report block per failed test. Each block is saved
/// on its own so a failure is one file away.
fn save_failures(lane: &str, output: &str) -> Result<Vec<(String, PathBuf)>> {
    let dir = Path::new(LOG_DIR).join("failures").join(slug(lane));
    let mut saved = Vec::new();
    let mut current: Option<(String, String)> = None;
    for line in output.lines() {
        if let Some(name) = failure_header(line) {
            if let Some((name, body)) = current.take() {
                saved.push(save_failure(&dir, &name, &body)?);
            }
            current = Some((name.to_string(), String::new()));
        } else if let Some((_, body)) = current.as_mut() {
            body.push_str(line);
            body.push('\n');
        }
    }
    if let Some((name, body)) = current.take() {
        saved.push(save_failure(&dir, &name, &body)?);
    }
    Ok(saved)
}

fn save_failure(dir: &Path, name: &str, body: &str) -> Result<(String, PathBuf)> {
    create_dir_all(dir)?;
    let path = dir.join(format!("{}.txt", slug(name)));
    write(&path, body)?;
    Ok((name.to_string(), path))
}

/// The desktop runner prints "N UI tests passed" on success and
/// "M of N UI test(s) failed" otherwise.
fn desktop_lane(name: &str, output: &str, ok: bool, log: PathBuf) -> Result<Lane> {
    let failures = save_failures(name, output)?;
    let passed = Regex::new(r"(\d+) UI tests passed")?;
    if let Some(caps) = passed.captures(output) {
        return Ok(Lane {
            name: name.to_string(),
            passed: caps[1].parse()?,
            failed: 0,
            ok: true,
            log,
            failures,
        });
    }
    let failed = Regex::new(r"(\d+) of (\d+) UI test\(s\) failed")?;
    if let Some(caps) = failed.captures(output) {
        let bad: i64 = caps[1].parse()?;
        let total: i64 = caps[2].parse()?;
        return Ok(Lane {
            name: name.to_string(),
            passed: total - bad,
            failed: bad,
            ok: false,
            log,
            failures,
        });
    }
    Ok(Lane {
        name: name.to_string(),
        passed: 0,
        failed: 0,
        ok,
        log,
        failures,
    })
}

/// The iOS lane prints "N tests, M failed" in its ok and failed lines.
fn ios_lane(output: &str, ok: bool, log: PathBuf) -> Result<Lane> {
    let name = "iOS simulator";
    let failures = save_failures(name, output)?;
    let marker = Regex::new(r"(\d+) tests, (\d+) failed")?;
    if let Some(caps) = marker.captures(output) {
        let total: i64 = caps[1].parse()?;
        let bad: i64 = caps[2].parse()?;
        return Ok(Lane {
            name: name.to_string(),
            passed: total - bad,
            failed: bad,
            ok: ok && bad == 0,
            log,
            failures,
        });
    }
    Ok(Lane {
        name: name.to_string(),
        passed: 0,
        failed: 0,
        ok,
        log,
        failures,
    })
}

fn log_path(lane: &str) -> PathBuf {
    Path::new(LOG_DIR).join(format!("{}.log", slug(lane)))
}

#[tokio::main(flavor = "multi_thread")]
async fn main() -> Result<()> {
    let is_mac = cfg!(target_os = "macos");

    // A fresh log dir per run, so a stale failure file never reads as current.
    if Path::new(LOG_DIR).exists() {
        remove_dir_all(LOG_DIR)?;
    }
    create_dir_all(LOG_DIR)?;

    let ios_log = log_path("iOS simulator");
    let debug_log = log_path("desktop debug");
    let release_log = log_path("desktop release");

    // Start the iOS lane first so it builds and runs while the desktop lanes go.
    let ios = if is_mac {
        let log = ios_log.clone();
        Some(tokio::spawn(async move {
            tee("HILEN_IOS_QUIET=1 rust ./build/ios/sim-test.rs", &log)
        }))
    } else {
        None
    };

    let debug = tee("cargo run -p ui-test", &debug_log)?;
    let release = tee("cargo run -p ui-test --release", &release_log)?;

    let mut lanes = vec![
        desktop_lane("desktop debug", &debug.0, debug.1, debug_log)?,
        desktop_lane("desktop release", &release.0, release.1, release_log)?,
    ];

    match ios {
        Some(handle) => {
            let (output, ok) = handle.await??;
            lanes.push(ios_lane(&output, ok, ios_log)?);
        }
        None => lanes.push(Lane {
            name: "iOS simulator".to_string(),
            passed: 0,
            failed: 0,
            ok: true,
            log: ios_log,
            failures: Vec::new(),
        }),
    }

    let width = lanes.iter().map(|l| l.name.len()).max().unwrap_or(0);
    let bar = "=".repeat(width + 26);

    println!("\n{bar}");
    println!("  UI tests");
    println!("{bar}");
    for lane in &lanes {
        let status = if !is_mac && lane.name == "iOS simulator" {
            "skipped (not macOS)".to_string()
        } else {
            format!("{} passed   {} failed", lane.passed, lane.failed)
        };
        println!("  {:width$}   {status}", lane.name);
    }
    println!("{bar}");
    for lane in &lanes {
        println!("  {:width$}   {}", lane.name, lane.log.display());
    }

    let failed: Vec<&Lane> = lanes.iter().filter(|lane| !lane.failures.is_empty()).collect();
    if !failed.is_empty() {
        println!("\n  Failures");
        for lane in failed {
            for (name, path) in &lane.failures {
                println!("  {:width$}   {name} -> {}", lane.name, path.display());
            }
        }
    }
    println!("{bar}");

    if lanes.iter().any(|lane| !lane.ok) {
        std::process::exit(1);
    }
    Ok(())
}
