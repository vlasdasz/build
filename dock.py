#!/usr/bin/env python3

import subprocess
import sys
import tempfile

builder_name = "docker_builder"
insecure_registry = "192.168.0.201:30500"


def run(cmd, check=True, capture_output=False):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, check=check, shell=True, capture_output=capture_output, text=True)
    if capture_output:
        return result.stdout.strip()
    return None


# patch docker config to allow unsecure registry
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


def build_image():
    if len(sys.argv) != 4:
        print("Usage: dock.py <name> <dockerfile> <version>")
        sys.exit(1)

    name = sys.argv[1]
    dockerfile = sys.argv[2]
    version = sys.argv[3]

    print("Cross-building with docker buildx and config override...")

    run(f"docker buildx rm {builder_name}", check=False)

    config_path = write_buildkitd_config()

    run(
        f"docker buildx create --name {builder_name} --use --driver docker-container --config {config_path}"
    )

    run("docker buildx inspect --bootstrap")

    image_tag = f"{name}:{version}"
    image_name = f"{insecure_registry}/{image_tag}"

    run(
        f"docker buildx build --file {dockerfile} --platform linux/amd64 "
        f"--tag {image_name} --push ."
    )


try:
    build_image()
except subprocess.CalledProcessError as e:
    print(f"Error during execution: {e}")
    sys.exit(1)
finally:
    run(f"docker buildx rm {builder_name}", check=False)
