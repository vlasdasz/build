
import os
import sys
import shutil
import platform
import urllib.request
from pathlib import Path
from enum import Enum

if Path("ndk").exists:
    print("NDK exists")

is_windows = platform.system() == "Windows"
is_mac     = platform.system() == "Darwin"
is_linux   = platform.system() == "Linux"


def run(command: str):
    print(command)
    if os.system(command):
        raise Exception("Shell script has failed")



class Arch(Enum):
    arm64 = "arm64"
    arm32 = "arm"
    x86 = "x86"

    def __str__(self):
        return str(self.value)

    def clang(self) -> str:
        return "aarch64-linux-android-clang"

    def check_clang_version(self):
        run(self.clang() + " --version")


def setup():
    shutil.rmtree("ndk")
    if is_mac:
        run("brew install p7zip")


def download_link():
    link = "https://dl.google.com/android/repository/android-ndk-r25c-darwin.dmg"

    if is_windows:
        link = "https://dl.google.com/android/repository/android-ndk-r25c-windows.zip"

    print("Download link: " + link)
    return link


def download() -> str:
    Path("ndk").mkdir(exist_ok=True)
    link = download_link()
    ext = Path(link).suffix
    print(ext)
    ndk = "ndk/ndk" + ext
    print("Downloading NDK from: " + link + " to: " + ndk)
    urllib.request.urlretrieve(link, ndk)
    return ndk


def make_toolchain(make_tool: str, arch: Arch, api_level: str = "21"):
    root = f"ndk/{arch}"
    run(f"py {make_tool} --api {api_level} --arch {arch} --install-dir {root}")
    ndk_bin = os.path.abspath(root) + "/bin"
    os.environ["PATH"] += os.pathsep + ndk_bin

    clang = f"{ndk_bin}/{arch.clang()}"

    print(f"Clang path:")
    print(clang)

    os.remove(clang)

    shutil.copyfile(f"{clang}.cmd", clang)

    arch.check_clang_version()

def unpack(ndk: str):
    if is_mac:
        run("7z -aos x -ondk " + ndk)
        run("mv -f ndk/Android\ NDK\ r25c/AndroidNDK9519653.app/Contents/NDK/* ndk/")
        run("rm -rf ndk/Android\ NDK\ r25c")
    elif is_windows:
        shutil.unpack_archive(ndk, "ndk")
        make_toolchain("ndk/android-ndk-r25c/build/tools/make_standalone_toolchain.py", Arch.arm64)


def install_toolchains():
    print("Add rust targets")
    run("rustup target add aarch64-linux-android armv7-linux-androideabi i686-linux-android")


setup()
unpack(download())
install_toolchains()
