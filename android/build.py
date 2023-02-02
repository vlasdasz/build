
import os
import glob
import platform

is_windows = platform.system() == "Windows"
is_mac     = platform.system() == "Darwin"
is_linux   = platform.system() == "Linux"

lib_name = os.environ['ANDROID_LIB_NAME']

print("Building lib: " + lib_name)

def run(string):
    print(string)
    if os.system(string):
        raise Exception("Shell script has failed")


for file in glob.glob("ndk/toolchains/llvm/prebuilt/darwin-x86_64/bin" + "/*"):
    run("chmod +x " + file)

os.environ["PATH"] += ":" + "ndk/toolchains/llvm/prebuilt/darwin-x86_64/bin"

run("aarch64-linux-android-clang --version")

run(f"cargo build -p {lib_name} --target aarch64-linux-android --release --lib")
# run(f"cargo build -p {lib_name} --target armv7-linux-androideabi --release --lib")
