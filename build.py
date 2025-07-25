#!/usr/bin/env python3

import os
import sys
import platform
import subprocess

is_windows = platform.system() == "Windows"
is_mac = platform.system() == "Darwin"
is_linux = platform.system() == "Linux"

unix = is_mac or is_linux

ios = False
android = False
debug = False


def get_uname():
    if unix:
        return str(subprocess.check_output(['uname', '-a']).lower())
    else:
        return ""


def get_release():
    if is_linux:
        return str(subprocess.check_output(['cat', '/etc/os-release']).lower())
    else:
        return ""


def run(string):
    print(string)
    if os.system(string):
        raise Exception("Shell script has failed")


uname = get_uname()
release = get_release()

print("uname: " + uname)
print("distro: " + platform.version())
print("system: " + platform.system())
print("release: " + get_release())

is_fedora = "fedora" in release
is_freebsd = "freebsd" in uname
is_arch = os.path.isfile("/etc/arch-release")
is_ubuntu = "ubuntu" in release
is_debian = "debian" in release
is_amazon = "amazon" in release
is_opensuse = "opensuse" in release

if len(sys.argv) > 1:
    args = " ".join(sys.argv).lower()
    ios = "ios" in args
    android = "android" in args
    debug = "debug" in args

mobile = ios or android
desktop = not mobile


def get_home():
    if "HOME" in os.environ:
        return os.environ["HOME"]
    return os.path.expanduser("~")


home = get_home()

this_script_path = os.path.dirname(os.path.abspath(__file__))
engine_path = f"{this_script_path}/.."


def build_android():
    run("rustup target add armv7-linux-androideabi aarch64-linux-android i686-linux-android x86_64-linux-android")

    run("cargo install test-mobile")
    run("test-mobile")

    if "TEST_ENGINE_ANDROID_DOCKER_BUILD" in os.environ:
        run(". ./build/install_java.sh")
        run(". ./build/install_ndk.sh")

    os.chdir("mobile/android")
    if unix:
        run("chmod +x ./gradlew")
    run("./gradlew build")


def build_ios():
    run("rustup target add aarch64-apple-ios x86_64-apple-ios")
    run("cargo install cargo-lipo")

    project_name = os.environ['APP_NAME']

    if debug:
        run(f"cargo lipo -p {project_name}")
    else:
        run(f"cargo lipo -p {project_name} --release")

    run("cargo install test-mobile")
    run("test-mobile")

    os.chdir("mobile/iOS")
    run("xcodebuild -showsdks")

    ios_project_name = os.environ['PROJECT_NAME']

    run(f"xcodebuild -sdk iphonesimulator -scheme \"{ios_project_name}\" build")


print("Arch:")
print(platform.uname())

if is_linux:
    print("Lin setup")

    if is_amazon:
        print("Amazon")
        run("sudo yum install -y gcc gcc-c++ alsa-lib-devel")
    elif is_fedora:
        print("Fedora")
        run("sudo dnf install -y libXcursor-devel libXi-devel libXinerama-devel libXrandr-devel "
            "perl make cmake automake gcc gcc-c++ kernel-devel alsa-lib-devel-*")
    elif is_freebsd:
        print("Freebsd")
        run("sudo pkg update")
        run("sudo pkg install cmake xorg pkgconf alsa-utils")
    elif is_arch:
        print("Arch")
        run("sudo pacman -S gcc pkg-config cmake openssl make alsa-lib alsa-utils --noconfirm")
    elif is_ubuntu or is_debian:
        print("Debian")

        deps = "cmake mesa-common-dev libgl1-mesa-dev libglu1-mesa-dev xorg-dev libasound2-dev pkg-config libssl-dev"

        if platform.processor() != "aarch64":
            deps += " build-essential"

        run("sudo apt update")
        run("sudo apt -y install " + deps)
    elif is_opensuse:
        print("openSUSE")
        run("sudo zypper refresh")
        run("sudo zypper update")
        run("sudo zypper install -y --type pattern devel_basis")
        run("sudo zypper install -y --type pattern devel_C_C++")
        run("sudo zypper install -y alsa-lib llvm llvm-devel clang")
    else:
        print("Unknown distro")
        exit(1)

    run("curl https://sh.rustup.rs -sSf | sh -s -- -y")
    os.environ["PATH"] += os.pathsep + "$HOME/.cargo/bin"

if ios:
    build_ios()
elif android:
    print("Ondroed")
    build_android()
else:
    run("cargo build --all")
    run("cargo test --all")
