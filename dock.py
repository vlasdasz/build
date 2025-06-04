#!/usr/bin/env python3

import subprocess
import platform
import sys
from pathlib import Path
import os

builder_name = "petuh_builder"


def run(cmd, check=True):
    print(f"Running: {cmd}")
    subprocess.run(cmd, check=check, shell=True)


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

    return env.get("CARGO_PACKAGE"), env.get("IMAGE_TAG"), env.get("DOCKERFILE_DIR", ".")


def main():
    try:
        package, image_tag, dockerfile_dir = load_env()

        dockerfile_path = Path(dockerfile_dir)
        if not dockerfile_path.exists() or not dockerfile_path.is_dir():
            print(f"Invalid DOCKERFILE_DIR: {dockerfile_dir}, falling back to current directory.")
            dockerfile_dir = "."

        run("cargo install cross --git https://github.com/cross-rs/cross")
        run(f"cross build -p {package} --release")

        local_registry = "192.168.0.201:30500"
        image_name = f"{local_registry}/{image_tag}"

        arch = platform.machine()
        os_name = platform.system()

        if os_name == "Linux" and arch == "x86_64":
            print("Building directly with docker (native x86_64 Linux)...")
            run(f"docker build -t {image_name} {dockerfile_dir}")
            run(f"docker push {image_name}")
        else:
            print("Cross-building with docker buildx...")
            run(f"docker buildx create --name {builder_name} --use")
            run("docker buildx inspect --bootstrap")
            run(f"docker buildx build --platform linux/amd64 -t {image_name} --push {dockerfile_dir}")
            run(f"docker buildx rm {builder_name}")

    except subprocess.CalledProcessError as e:
        run(f"docker buildx rm {builder_name}")
        print(f"Error during execution: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
