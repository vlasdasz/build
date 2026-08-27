#!/usr/bin/env rust

// Tags and pushes a release, CI builds from the tag. `patch` or `minor` bumps
// the newest `v*` tag, writes the version into Cargo.toml and Cargo.lock,
// commits, tags and pushes.

use anyhow::{Context, Result, bail};
use regex::Regex;
use shared::release;
use shared::run::{capture, probe, run};

fn main() -> Result<()> {
    let kind = std::env::args().nth(1).unwrap_or_default();
    if kind != "patch" && kind != "minor" {
        bail!("usage: tag.rs patch|minor");
    }
    // A version bump commit must not sweep up unrelated changes.
    if !capture("git status --porcelain")?.trim().is_empty() {
        bail!("working tree has uncommitted changes, commit or stash first");
    }
    let r = release::read()?;
    let (major, minor, patch) = latest_tag()?;
    let version = if kind == "patch" {
        format!("{major}.{minor}.{}", patch + 1)
    } else {
        format!("{major}.{}.0", minor + 1)
    };
    write_version(&r.name, &version)?;
    let tag = format!("v{version}");
    run("git add Cargo.toml Cargo.lock")?;
    run(&format!(r#"git commit -m "release {tag}""#))?;
    run(&format!("git tag {tag}"))?;
    run(&format!("git push origin HEAD {tag}"))?;
    println!("released {tag}");
    Ok(())
}

fn latest_tag() -> Result<(u64, u64, u64)> {
    let out = probe("git describe --tags --abbrev=0 --match=v*");
    let re = Regex::new(r"^v(\d+)\.(\d+)\.(\d+)")?;
    let Some(caps) = re.captures(out.trim()) else {
        return Ok((0, 0, 0));
    };
    Ok((caps[1].parse()?, caps[2].parse()?, caps[3].parse()?))
}

fn write_version(name: &str, version: &str) -> Result<()> {
    let cargo = std::fs::read_to_string("Cargo.toml")?;
    let re = Regex::new(r#"(?m)^version\s*=\s*"[^"]+""#)?;
    if !re.is_match(&cargo) {
        bail!("no version line in Cargo.toml");
    }
    let cargo = re.replacen(&cargo, 1, format!(r#"version     = "{version}""#).as_str());
    std::fs::write("Cargo.toml", cargo.as_ref())?;

    // Cargo.lock carries the package version too, without this the next
    // cargo run rewrites it and leaves the tree dirty after a release.
    let lock = std::fs::read_to_string("Cargo.lock")?;
    let re = Regex::new(&format!(
        r#"(?m)(\[\[package\]\]\nname = "{}"\nversion = ")[^"]+(")"#,
        regex::escape(name)
    ))?;
    if !re.is_match(&lock) {
        bail!("no {name} package entry in Cargo.lock");
    }
    let lock = re.replacen(&lock, 1, format!("${{1}}{version}${{2}}").as_str());
    std::fs::write("Cargo.lock", lock.as_ref()).context("write Cargo.lock")?;
    Ok(())
}
