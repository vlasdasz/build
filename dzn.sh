#!/bin/sh
# Build Mesa's Direct3D 12 Vulkan driver, dzn, and register it with the
# Vulkan loader for this user. WSL needs it: the distro Mesa ships no Vulkan
# driver for the Windows GPU, only the CPU lavapipe, so without dzn every
# frame is drawn in software on every core. Plain sh like setup.sh.
# Idempotent: a driver that is already installed is left alone.
set -eu

MESA_VERSION=25.2.8
PREFIX="$HOME/.local/lib/hilen/dzn"
ICD_DIR="$HOME/.local/share/vulkan/icd.d"
ICD="$ICD_DIR/dzn_icd.x86_64.json"
WORK="${TMPDIR:-/tmp}/hilen-dzn"

have() { command -v "$1" >/dev/null 2>&1; }

if [ -f "$ICD" ] && [ -f "$PREFIX/lib/libvulkan_dzn.so" ]; then
	echo "dzn driver already installed at $PREFIX"
	exit 0
fi

# Mesa wants meson 1.4 and Ubuntu 24.04 ships 1.3, pipx puts a newer one
# into ~/.local/bin.
meson_ok() {
	have meson && meson --version | awk -F. '{ exit !($1 > 1 || ($1 == 1 && $2 >= 4)) }'
}
if ! meson_ok; then
	pipx install meson
	export PATH="$HOME/.local/bin:$PATH"
fi
if ! meson_ok; then
	echo "meson 1.4 or newer is needed to build the dzn driver" >&2
	exit 1
fi

mkdir -p "$WORK"
cd "$WORK"
if [ ! -d "mesa-$MESA_VERSION" ]; then
	echo "downloading mesa $MESA_VERSION"
	curl -sfL -o mesa.tar.xz "https://archive.mesa3d.org/mesa-$MESA_VERSION.tar.xz"
	tar xf mesa.tar.xz
fi
cd "mesa-$MESA_VERSION"

echo "building the dzn driver, a few minutes"
rm -rf build
meson setup build -Dprefix="$PREFIX" -Dlibdir=lib -Dbuildtype=release \
	-Dplatforms=x11 -Dvulkan-drivers=microsoft-experimental -Dgallium-drivers= \
	-Dglx=disabled -Degl=disabled -Dgbm=disabled -Dllvm=disabled -Dopengl=false \
	-Dgles1=disabled -Dgles2=disabled -Dtools= -Dvulkan-layers= -Dvideo-codecs= \
	-Dlibunwind=disabled -Dvalgrind=disabled -Dzstd=disabled -Dlmsensors=disabled \
	> build-setup.log
ninja -C build install > build-install.log

# The installed manifest already names the library by its absolute path,
# the loader only has to find the manifest in the user icd folder.
mkdir -p "$ICD_DIR"
cp "$PREFIX/share/vulkan/icd.d/dzn_icd.x86_64.json" "$ICD"
echo "dzn driver installed, the Vulkan loader reads $ICD"
