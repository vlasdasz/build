#!/bin/bash

echo Installing rustup:
curl https://sh.rustup.rs -sSf | sh -s -- -y

echo Adding rustup to path
source "$HOME/.cargo/env"

which cargo

export ANDROID_LIB_NAME=test_game
export IOS_PROJECT_NAME=TestEngine

dir=$(dirname "$0")
python3 "$dir"/build.py "${1:-}"
