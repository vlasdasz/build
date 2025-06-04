#!/usr/bin/env python3

import subprocess
import platform
import sys
from pathlib import Path
import json
import tempfile

builder_name = "petuh_builder"
insecure_registry = "192.168.0.201:30500"


def run(cmd, check=True, capture_output=False):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, check=check, shell=True, capture_output=capture_output, text=True)
    if capture_output:
        return result.stdout.strip()
    return None


def load_env():
    env_path = Path(".env")
    if not env_path.exists():
        print(".env file not found.")
        sys.exit(1)

    env = {}
    with env_path.open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip()

    if "CARGO_PACKAGE" not in env or "IMAGE_TAG" not in env:
        print("CARGO_PACKAGE or IMAGE_TAG missing from .env")
        sys.exit(1)

    return env["CARGO_PACKAGE"], env["IMAGE_TAG"]


def write_buildkitd_config():
    config = f"""
[registry."{insecure_registry}"]
  http = true
  insecure = true
"""
    tmp = tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".toml")
    tmp.write(config)
    tmp.close()
    return tmp.name


def main():
    try:
        package, image_tag = load_env()
        run("cargo install cross --git https://github.com/cross-rs/cross")
        run(f"cross build -p {package} --release")

        image_name = f"{insecure_registry}/{image_tag}"

        arch = platform.machine()
        os_name = platform.system()

        if os_name == "Linux" and arch == "x86_64":
            print("Building directly with docker (native x86_64 Linux)...")
            run(f"docker build -t {image_name} .")
            run(f"docker push {image_name}")
        else:
            print("Cross-building with docker buildx and config override...")

            run(f"docker buildx rm {builder_name}", check=False)

            config_path = write_buildkitd_config()

            run(f"docker buildx create --name {builder_name} --use --driver docker-container --config {config_path}")
            run("docker buildx inspect --bootstrap")

            run(f"docker buildx build --platform linux/amd64 -t {image_name} --push .")

    except subprocess.CalledProcessError as e:
        print(f"Error during execution: {e}")
        sys.exit(1)
    finally:
        run(f"docker buildx rm {builder_name}", check=False)


if __name__ == "__main__":
    main()
