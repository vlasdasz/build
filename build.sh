#!/bin/bash
set -eox pipefail
. ./env.sh

echo "ANDROID_LIB_NAME: $ANDROID_LIB_NAME"
echo "IOS_PROJECT_NAME: $IOS_PROJECT_NAME"

OS_NAME=$(uname)

echo "OS_NAME: $OS_NAME"

if [[ "$CI" == "true" && "$1" == "android" ]]; then
    echo "Building android inside GitHub Actions "
    ./build/in_docker_android.sh
    exit 0
fi

if [ "$OS_NAME" != "Darwin" ]; then
    cat /etc/os-release

    if grep -qEi "(debian|ubuntu)" /etc/os-release; then
        echo Debian
        export DEBIAN_FRONTEND=noninteractive
        apt update
        apt install curl python3 sudo -yq
    elif grep -qEi "Arch Linux|Manjaro" /etc/os-release; then
        echo Arch
        pacman -Sy python-pip sudo --noconfirm
    elif grep -qEi "Amazon Linux" /etc/os-release; then
        yum install -y sudo python3
    elif grep -qEi "Fedora" /etc/os-release; then
        dnf install -y sudo python3
    elif grep -qEi "openSUSE" /etc/os-release; then
        zypper install -y python3 sudo
    else
        echo "This is not Debian or Ubuntu. Command will not run."
    fi
else
    echo "This script is running on macOS."
fi

echo Installing rustup:
curl https://sh.rustup.rs -sSf | sh -s -- -y

echo Adding rustup to path
source "$HOME/.cargo/env"

dir=$(dirname "$0")
python3 "$dir"/build.py "${1:-}"
