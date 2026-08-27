//! What the desktop release scripts need, the package name and version from
//! Cargo.toml and the `[release]` table of hilen.toml.

use anyhow::{Context, Result};

pub struct Release {
    /// cargo package name, the artifact file name prefix
    pub name: String,
    pub version: String,
    pub bundle_id: String,
    /// where the binaries are served, no trailing slash
    pub download_url: String,
    /// the beekeeper deployment whose data/download/ holds the binaries
    pub host_deployment: String,
    /// subdirectory under that data/download/
    pub target_subdir: String,
}

impl Release {
    /// `kukareker-0.2.0-mac-universal.dmg` style names.
    pub fn artifact(&self, suffix: &str) -> String {
        format!("{}-{}-{suffix}", self.name, self.version)
    }
}

/// Read from the repo root, before any chdir.
pub fn read() -> Result<Release> {
    let cargo = std::fs::read_to_string("Cargo.toml").context("Cargo.toml not found")?;
    let cargo: serde_json::Value = toml::from_str(&cargo)?;
    let package = cargo.get("package").context("[package] missing in Cargo.toml")?;
    let name = string(package, "name")?;
    let version = string(package, "version")?;

    let hilen = std::fs::read_to_string("hilen.toml").context("hilen.toml not found")?;
    let hilen: serde_json::Value = toml::from_str(&hilen)?;
    let bundle_id = string(&hilen, "bundle_id")?;
    let release = hilen.get("release").context("[release] missing in hilen.toml")?;

    Ok(Release {
        name,
        version,
        bundle_id,
        download_url: string(release, "download_url")?.trim_end_matches('/').to_string(),
        host_deployment: string(release, "host_deployment")?,
        target_subdir: string(release, "target_subdir")?,
    })
}

fn string(value: &serde_json::Value, key: &str) -> Result<String> {
    Ok(value
        .get(key)
        .and_then(|v| v.as_str())
        .with_context(|| format!("{key} missing"))?
        .to_string())
}
