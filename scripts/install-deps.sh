
if [ "$OS_NAME" != "Darwin" ]; then
    cat /etc/os-release

    if grep -qEi "(debian|ubuntu)" /etc/os-release; then
        echo Debian
        export DEBIAN_FRONTEND=noninteractive
        sudo apt update
        sudo apt install cmake mesa-common-dev libgl1-mesa-dev libglu1-mesa-dev xorg-dev libasound2-dev pkg-config libssl-dev -yq
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
        echo "Unknown Linux. Command will not run."
    fi
else
    echo "This script is running on macOS."
fi
