#!/usr/bin/env python3

import os
import sys
import glob
import shutil
import platform
import subprocess
import urllib.request

sys.path.append("build/android")

from install_ndk import install_ndk
from install_ndk import Arch
from build_android import build_android

# import application.app.android.install_ndk
# import application.app.android.build

is_windows = platform.system() == "Windows"
is_mac     = platform.system() == "Darwin"
is_linux   = platform.system() == "Linux"

unix = is_mac or is_linux

ios = False
android = False


def get_uname():
    if unix:
        return str(subprocess.check_output(['uname', '-a']).lower())
    else:
        return ""


def run(string):
    print(string)
    if os.system(string):
        raise Exception("Shell script has failed")


uname = get_uname()

is_fedora = "fedora" in uname
is_freebsd = "freebsd" in uname
# is_arch = "arch" in uname

if len(sys.argv) > 1:
    if sys.argv[1] == "ios":
        ios = True
    if sys.argv[1] == "android":
        android = True

mobile = ios or android
desktop = not mobile


def get_home():
    if "HOME" in os.environ:
        return os.environ["HOME"]
    return os.path.expanduser("~")


home = get_home()

this_script_path = os.path.dirname(os.path.abspath(__file__))
engine_path = f"{this_script_path}/.."


# def setup_android():

#     print("Add rust targets")
#     run("rustup target add aarch64-linux-android armv7-linux-androideabi i686-linux-android")

#     host_platform = "linux" if is_linux else "darwin"
#     arch_platform = host_platform + "-x86_64"
#     ndk_bin = engine_path + "/ndk/bin"
#     version = "r22b"
#     api_level = "21"

#     toolchains = "/ndk/android-ndk-" + version + "/toolchains/"

#     os.environ["NDK_INCLUDE_DIR"] = engine_path + toolchains + "llvm/prebuilt/" + arch_platform + "/sysroot/usr/include"
#     os.environ["PATH"] += ":" + ndk_bin

#     print("NDK bin path:")
#     print(ndk_bin)

#     if os.path.isdir("ndk"):
#         print("NDK directory already exists")
#         return

#     run("mkdir ndk")

#     print("Downloading NDK")

#     urllib.request.urlretrieve("https://dl.google.com/android/repository/android-ndk-" + version + "-" + arch_platform + ".zip", "ndk/ndk.zip")
#     shutil.unpack_archive("ndk/ndk.zip", "ndk")

#     print("Symlink NDK bin")

#     os.symlink(engine_path + toolchains + "llvm/prebuilt/" + arch_platform + "/bin", ndk_bin)

#     print("Symlink clang")
#     shutil.copyfile(ndk_bin + "/aarch64-linux-android" + api_level + "-clang",
#                     ndk_bin + "/aarch64-linux-android-clang")
#     shutil.copyfile(ndk_bin + "/aarch64-linux-android" + api_level + "-clang++",
#                     ndk_bin + "/aarch64-linux-android-clang++")
#     shutil.copyfile(ndk_bin + "/llvm-ar",
#                     ndk_bin + "/aarch64-linux-android-ar")

#     shutil.copyfile(ndk_bin + "/armv7a-linux-androideabi" + api_level + "-clang",
#                     ndk_bin + "/arm-linux-androideabi-clang")
#     shutil.copyfile(ndk_bin + "/armv7a-linux-androideabi" + api_level + "-clang++",
#                     ndk_bin + "/arm-linux-androideabi-clang++")

#     for file in glob.glob(ndk_bin + "/*"):
#         run("chmod +x " + file)


# def build_android():
#     android_lib_name = os.environ['ANDROID_LIB_NAME']

#     run(f"cargo build -p {android_lib_name} --target aarch64-linux-android --release --lib")
#     run(f"cargo build -p {android_lib_name} --target armv7-linux-androideabi --release --lib")

#     jni_libs_dir = f"{engine_path}/mobile/android/app/src/main/jniLibs"

#     run(f"mkdir -p {jni_libs_dir}")
#     run(f"mkdir -p {jni_libs_dir}/arm64-v8a")
#     run(f"mkdir -p {jni_libs_dir}/armeabi-v7a")

#     try:
#         os.symlink(f"{engine_path}/target/aarch64-linux-android/release/lib{android_lib_name}.so",
#                    f"{jni_libs_dir}/arm64-v8a/lib{android_lib_name}.so")

#         os.symlink(f"{engine_path}/target/armv7-linux-androideabi/release/lib{android_lib_name}.so",
#                    f"{jni_libs_dir}/armeabi-v7a/lib{android_lib_name}.so")
#     except FileExistsError:
#         print("exists")


def build_ios():
    run("rustup target add aarch64-apple-ios x86_64-apple-ios")
    run("cargo install cargo-lipo")
    run("cargo lipo --release")
    os.chdir("mobile/iOS")
    run("xcodebuild -showsdks")

    ios_project_name = os.environ['IOS_PROJECT_NAME']

    run(f"xcodebuild -sdk iphonesimulator -scheme {ios_project_name} build")


print("Arch:")
print(platform.uname())


if is_linux and desktop:
    print("Lin setup")

    if is_fedora:
        print("Fedora")
        run("sudo dnf update")
        run("sudo dnf install libXcursor-devel libXi-devel libXinerama-devel libXrandr-devel "
            "alsa-lib-devel-1.2.6.1-3.fc34.aarch64")
    elif is_freebsd:
        print("Freebsd")
        run("sudo pkg update")
        run("sudo pkg install cmake xorg pkgconf alsa-utils")
    else:
        print("Debian")

        deps = "cmake mesa-common-dev libgl1-mesa-dev libglu1-mesa-dev xorg-dev libasound2-dev"

        if platform.processor() != "aarch64":
            deps += " build-essential"

        run("sudo apt update")
        run("sudo apt -y install " + deps)

    run("curl https://sh.rustup.rs -sSf | sh -s -- -y")
    os.environ["PATH"] += os.pathsep + "$HOME/.cargo/bin"


if ios:
    build_ios()
elif android:
    print("Ondroed")
    install_ndk()
    build_android(Arch.arm64)
    build_android(Arch.arm32)
    build_android(Arch.x86)
else:
    run("cargo build --all")
