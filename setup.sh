#!/bin/sh
# Install the system build dependencies and Rust for a Linux or WSL build.
# This is plain sh, not a RustScript build script, because it runs before
# cargo and the rust interpreter exist on a fresh machine.
# It is idempotent: it probes for what is already there and installs only the
# rest, so a repeat run does not ask for the sudo password.
set -eu

have() { command -v "$1" >/dev/null 2>&1; }
pkg() { pkg-config --exists "$1" 2>/dev/null; }

deps_present() {
	have cc && have cmake && have git && have pkg-config && have zenity \
		&& pkg openssl && pkg alsa && pkg x11 \
		&& ldconfig -p | grep -q libxkbcommon-x11 \
		&& [ -n "$(ls -A /usr/share/vulkan/icd.d 2>/dev/null || true)" ]
}

install_system() {
	if deps_present; then
		echo "system deps already present"
		return 0
	fi
	if have sudo; then SUDO=sudo; else SUDO=; fi
	if have apt-get; then
		$SUDO apt-get update
		$SUDO apt-get install -y build-essential git cmake pkg-config \
			libssl-dev xorg-dev libasound2-dev libxkbcommon-x11-0 \
			mesa-vulkan-drivers zenity
	elif have dnf; then
		$SUDO dnf install -y gcc gcc-c++ make git cmake pkgconf-pkg-config \
			openssl-devel libX11-devel libXcursor-devel libXrandr-devel \
			libXi-devel libxkbcommon-devel libxkbcommon-x11 wayland-devel \
			alsa-lib-devel mesa-vulkan-drivers zenity
	elif have pacman; then
		$SUDO pacman -S --needed --noconfirm base-devel git cmake pkgconf \
			openssl libx11 libxcursor libxrandr libxi libxkbcommon \
			libxkbcommon-x11 wayland alsa-lib vulkan-icd-loader mesa zenity
	else
		echo "no supported package manager (apt-get, dnf, pacman)." >&2
		echo "install the build deps by hand, see docs/wsl.md in hilen" >&2
		exit 1
	fi
}

install_rust() {
	if have cargo; then
		return 0
	fi
	if ! have curl; then
		echo "curl is needed to install rustup, install it first" >&2
		exit 1
	fi
	curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
	echo "rustup installed"
}

install_system
install_rust
