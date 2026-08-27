#!/usr/bin/env rust

// The Windows release, cross built in docker with cargo-xwin and packed by
// NSIS. `--arch x64|arm64`, default both. Outputs in dist/:
//   <name>-<v>-windows-<arch>-setup.exe   first install
//   <name>-<v>-windows-<arch>.exe         the bare exe the updater swaps in

mod docker;

use anyhow::{Result, bail};
use shared::release;
use shared::run::run;

const TARGETS: [(&str, &str); 2] = [
    ("x64", "x86_64-pc-windows-msvc"),
    ("arm64", "aarch64-pc-windows-msvc"),
];

fn main() -> Result<()> {
    let r = release::read()?;
    let only = std::env::args()
        .skip(1)
        .find_map(|a| a.strip_prefix("--arch=").map(str::to_string));
    let targets: Vec<(&str, &str)> = TARGETS
        .iter()
        .copied()
        .filter(|(arch, _)| only.as_deref().is_none_or(|o| o == *arch))
        .collect();
    if targets.is_empty() {
        bail!("unknown arch, use x64 or arm64");
    }
    std::fs::create_dir_all("dist")?;

    let image = format!("{}-win-builder", r.name);
    let platform = "linux/amd64";
    docker::build_image(&image, "Dockerfile.windows", platform)?;
    let mut script = String::from("set -euo pipefail\nrustup component add rust-src\n");
    for (arch, triple) in &targets {
        script.push_str(&format!(
            r#"rustup target add {triple}
cargo xwin build --release --target {triple}
makensis -DNAME={name} -DVERSION={version} -DEXE=target/release-win/{triple}/release/{name}.exe -DICON=assets/icon.ico -DOUT=target/release-win/{name}-{arch}-setup.exe build/release/installer.nsi
"#,
            name = r.name,
            version = r.version
        ));
    }
    docker::run_in(&image, platform, "release-win", &script)?;

    for (arch, triple) in &targets {
        let setup = format!("dist/{}", r.artifact(&format!("windows-{arch}-setup.exe")));
        let bare = format!("dist/{}", r.artifact(&format!("windows-{arch}.exe")));
        std::fs::copy(format!("target/release-win/{}-{arch}-setup.exe", r.name), &setup)?;
        std::fs::copy(format!("target/release-win/{triple}/release/{}.exe", r.name), &bare)?;
        run(&format!("rust build/release/sign.rs {bare}"))?;
        println!("built {setup}");
        println!("built {bare}");
    }
    Ok(())
}
