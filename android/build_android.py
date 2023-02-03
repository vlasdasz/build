
import os
import glob
import platform

from install_ndk import Arch

is_windows = platform.system() == "Windows"
is_mac     = platform.system() == "Darwin"
is_linux   = platform.system() == "Linux"


lib_name = os.path.basename(os.getcwd())

if os.environ.get("ANDROID_LIB_NAME") != None:
    lib_name = os.environ["ANDROID_LIB_NAME"]

print("Building lib: " + lib_name)


def run(string):
    print(string)
    if os.system(string):
        raise Exception("Shell script has failed")


def build_android(arch: Arch):

    run(f"cargo build -p {lib_name} --target {arch.cargo_target()} --release --lib")

    jni_libs_dir = "mobile/android/app/src/main/jniLibs"

    jni_folder = f"{jni_libs_dir}/{arch.jni_folder()}"

    run(f"mkdir -p {jni_libs_dir}")
    run(f"mkdir -p {jni_folder}")

    try:
        os.symlink(f"target/{arch.cargo_target()}/release/lib{lib_name}.so",
                   f"{jni_folder}/lib{lib_name}.so")

        # os.symlink(f"target/armv7-linux-androideabi/release/lib{lib_name}.so",
        #            f"{jni_libs_dir}/armeabi-v7a/lib{lib_name}.so")
    except FileExistsError:
        print("Symlink to libs exists")
