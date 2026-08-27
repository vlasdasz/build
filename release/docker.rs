//! Shared by linux.rs and win.rs. Builds the tool image and runs one shell
//! string inside it with the repo mounted, plus named volumes for the cargo
//! caches so a second run does not start from zero. On a dev box the engine
//! checkout next to the apps dir is mounted too, so a path dependency on it
//! resolves inside the container the same way it does outside.

use anyhow::Result;
use shared::run::run;

pub fn build_image(name: &str, dockerfile: &str, platform: &str) -> Result<()> {
    run(&format!(
        "docker build --platform {platform} -f build/release/{dockerfile} -t {name} build/release"
    ))
}

pub fn run_in(image: &str, platform: &str, lane: &str, script: &str) -> Result<()> {
    let cwd = std::env::current_dir()?;
    let cwd = cwd.display();
    let engine = std::path::Path::new("../../hilen");
    let engine_mount = if engine.is_dir() {
        format!("-v {}:/work/hilen", std::fs::canonicalize(engine)?.display())
    } else {
        String::new()
    };
    let arch = platform.replace('/', "-");
    run(&format!(
        r#"docker run --rm --platform {platform} \
  -v {cwd}:/work/apps/app \
  {engine_mount} \
  -v {lane}-{arch}-target:/work/apps/app/target/{lane} \
  -v {lane}-{arch}-cargo-registry:/usr/local/cargo/registry \
  -v {lane}-{arch}-cargo-git:/usr/local/cargo/git \
  -v {lane}-{arch}-rustup:/usr/local/rustup \
  -e CARGO_TARGET_DIR=/work/apps/app/target/{lane} \
  {image} bash -c '{script}'"#
    ))
}
