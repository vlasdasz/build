#!/bin/bash

. ./env.sh

echo "ANDROID_LIB_NAME: $ANDROID_LIB_NAME"
echo "$IOS_PROJECT_NAME: $IOS_PROJECT_NAME"

cat /etc/os-release

if grep -qEi "(debian|ubuntu)" /etc/os-release; then
    apt update
    apt install curl python3 sudo -yq
elif grep -qEi "Arch Linux" /etc/os-release; then
    pacman -Sy python-pip sudo --noconfirm
else
    echo "This is not Debian or Ubuntu. Command will not run."
fi

echo Installing rustup:
curl https://sh.rustup.rs -sSf | sh -s -- -y

echo Adding rustup to path
source "$HOME/.cargo/env"

dir=$(dirname "$0")
python3 "$dir"/build.py "${1:-}"
