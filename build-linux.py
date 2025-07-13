#!/usr/bin/env python3

import subprocess


def run(cmd, check=True, capture_output=False):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, check=check, shell=True, capture_output=capture_output, text=True)
    if capture_output:
        return result.stdout.strip()
    return None


run("cargo install cross --git https://github.com/cross-rs/cross")
run(f"cross build --all --release")
