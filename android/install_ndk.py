
import os
import shutil
import platform
import urllib.request
from pathlib import Path

if Path("ndk").exists:
    print("NDK exists")

is_windows = platform.system() == "Windows"
is_mac     = platform.system() == "Darwin"
is_linux   = platform.system() == "Linux"

print("Platform:")
print(platform.uname())

def run(string):
    print(string)
    if os.system(string):
        raise Exception("Shell script has failed")


def setup():
    run("rm -rf ndk")
    run("brew install p7zip")


def download_link():
    link = "https://dl.google.com/android/repository/android-ndk-r25c-darwin.dmg"
    print("Download link: " + link)
    return link


def download():
    Path("ndk").mkdir(exist_ok=True)
    print("Downloading NDK")
    urllib.request.urlretrieve(download_link(), "ndk/ndk.dmg")


def unpack():
    run("7z -aos x -ondk ndk/ndk.dmg")
    run("mv -f ndk/Android\ NDK\ r25c/AndroidNDK9519653.app/Contents/NDK/* ndk/")
    run("rm -rf ndk/Android\ NDK\ r25c")
    #shutil.unpack_archive("ndk/ndk.dmg", "ndk")

def install_toolchains():
    print("Add rust targets")
    run("rustup target add aarch64-linux-android armv7-linux-androideabi i686-linux-android")


#setup()
#download()
#unpack()
install_toolchains()
