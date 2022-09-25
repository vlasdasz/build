#!/bin/bash

. ./env.sh

echo "ANDROID_LIB_NAME: $ANDROID_LIB_NAME"
echo "$IOS_PROJECT_NAME: $IOS_PROJECT_NAME"

echo Installing rustup:
curl https://sh.rustup.rs -sSf | sh -s -- -y

echo Adding rustup to path
source "$HOME/.cargo/env"

which cargo

dir=$(dirname "$0")
python3 "$dir"/build.py "${1:-}"
