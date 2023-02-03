
import os
import sys
import glob
import shutil
import platform
import urllib.request
from pathlib import Path
from enum import Enum


is_windows = platform.system() == "Windows"
is_mac     = platform.system() == "Darwin"
is_linux   = platform.system() == "Linux"

is_unix = is_mac or is_linux


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

    def cargo_target(self) -> str:
        if self == Arch.arm64:
            return "aarch64-linux-android"
        elif self == Arch.arm32:
            return "armv7-linux-androideabi"
        elif self == Arch.x86:
            return "i686-linux-android"
        
    def jni_folder(self) -> str:
        if self == Arch.arm64:
            return "arm64-v8a"
        elif self == Arch.arm32:
            return "armeabi-v7a"
        elif self == Arch.x86:
            return "x86"
        
    def ar(self) -> str:
        if self == Arch.arm64:
            return "aarch64-linux-android-ar"
        elif self == Arch.arm32:
            return "arm-linux-androideabi-ar"
        elif self == Arch.x86:
            return "i686-linux-android-ar"
        

def setup():
    if is_mac:
        run("brew install p7zip")


def python_exe() -> str:
    if is_windows:
        return "py"
    else:
        return "python3"


def download_link():
    link = "https://dl.google.com/android/repository/android-ndk-r25c-darwin.dmg"

    if is_windows:
        link = "https://dl.google.com/android/repository/android-ndk-r25c-windows.zip"

    if is_linux:
        link = "https://dl.google.com/android/repository/android-ndk-r25c-linux.zip"

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
    root = os.path.abspath(root)
    ndk_bin = root + "/bin"

    os.environ["PATH"] += os.pathsep + ndk_bin
    os.environ["NDK_HOME"] = root

    if Path(root).exists():
        print(f"{root} already exists")
        return

    run(f"{python_exe()} {make_tool} --api {api_level} --arch {arch} --install-dir {root}")

    if is_windows:
        shutil.copyfile(f"{ndk_bin}/llvm-ar.exe", f"{ndk_bin}/{arch.ar()}.exe")
    else:
        shutil.copyfile(f"{ndk_bin}/llvm-ar", f"{ndk_bin}/{arch.ar()}")

    if is_unix:
        for file in glob.glob(ndk_bin + "/*"):
            run("chmod +x " + file)

    clang = f"{ndk_bin}/{arch.clang()}"

    print(f"Clang path:")
    print(clang)

    # if is_windows:
    #     os.remove(clang)
    #     shutil.copyfile(f"{clang}.cmd", clang)


def unpack(ndk: str):
    if is_mac:
        run("7z -aos x -ondk " + ndk)
        run("mkdir ndk/android-ndk-r25c")
        run("mv -f ndk/Android\ NDK\ r25c/AndroidNDK9519653.app/Contents/NDK/* ndk/android-ndk-r25c/")
        run("rm -rf ndk/Android\ NDK\ r25c")
    elif is_windows or is_linux:
        shutil.unpack_archive(ndk, "ndk")


def install_toolchains():
    print("Add rust targets")
    run("rustup target add aarch64-linux-android armv7-linux-androideabi i686-linux-android")

    make_toolchain("ndk/android-ndk-r25c/build/tools/make_standalone_toolchain.py", Arch.arm64)
    make_toolchain("ndk/android-ndk-r25c/build/tools/make_standalone_toolchain.py", Arch.arm32)
    make_toolchain("ndk/android-ndk-r25c/build/tools/make_standalone_toolchain.py", Arch.x86)


def install_ndk():
    setup()

    if Path("ndk").exists():
        print("NDK exists")
    else:
        unpack(download())

    install_toolchains()
