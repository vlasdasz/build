#!/usr/bin/env python3

import os
import subprocess

def main():
    # Set HOST_DIR to current working directory if not set
    host_dir = os.getenv("HOST_DIR", os.getcwd())

#     print(host_dir)
#
#     exit(0)

    # Define the Docker command
    docker_command = [
        "docker", "run", "--rm",
        "--mount", f"type=bind,source={host_dir},target=/host",
        "--cap-add=SYS_PTRACE",
        "--security-opt", "seccomp=unconfined",
        "-t", "ubuntu",
        "/bin/bash", "-c",
        "cd /host && pwd && ls -A && export TEST_ENGINE_ANDROID_DOCKER_BUILD=true && ./build/build.sh android"
    ]

    # Print the command for debugging
    print("Running command:", " ".join(docker_command))

    # Execute the command
    try:
        subprocess.run(docker_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: Command failed with exit code {e.returncode}")
        exit(e.returncode)

if __name__ == "__main__":
    main()
