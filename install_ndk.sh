#!/bin/bash

# Function to log messages
log() {
    echo "[INFO] $1"
}

# Ensure script exits on any error
set -e

rm -rf ~/Android/Sdk/cmdline-tools/tools/cmdline-tools

# Set up Android SDK root if not set
if [ -z "$ANDROID_HOME" ]; then
    export ANDROID_HOME="$HOME/Android/Sdk"
    log "ANDROID_HOME not set, defaulting to $ANDROID_HOME"
fi

# Create Android SDK directory if it doesn't exist
mkdir -p "$ANDROID_HOME"

# Check if sdkmanager is available, if not, download and install it
if ! command -v sdkmanager &> /dev/null; then
    log "sdkmanager not found, downloading command-line tools..."

    SDK_TOOLS_URL="https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip"

    # Download the command-line tools
    mkdir -p "$ANDROID_HOME/cmdline-tools"
    curl -o cmdline-tools.zip $SDK_TOOLS_URL
    unzip cmdline-tools.zip -d "$ANDROID_HOME/cmdline-tools"
    mv "$ANDROID_HOME/cmdline-tools/cmdline-tools" "$ANDROID_HOME/cmdline-tools/tools"
    rm cmdline-tools.zip

    export PATH="$ANDROID_HOME/cmdline-tools/tools/bin:$PATH"
    log "sdkmanager installed and added to PATH"
else
    log "sdkmanager found in PATH"
fi

# Accept licenses before installation
yes | sdkmanager --licenses

# Install NDK using sdkmanager
NDK_VERSION="27.0.11718014"  # You can change this to the desired NDK version
log "Installing NDK version $NDK_VERSION..."

yes | sdkmanager "ndk;$NDK_VERSION" --sdk_root="$ANDROID_HOME"

if [ $? -ne 0 ]; then
    log "Failed to install NDK version $NDK_VERSION"
    exit 1
fi

log "NDK installed successfully"

# Set environment variables for NDK
export ANDROID_NDK_HOME="$ANDROID_HOME/ndk/$NDK_VERSION"
export PATH="$PATH:$ANDROID_NDK_HOME"

log "ANDROID_NDK_HOME set to $ANDROID_NDK_HOME"

# Verify NDK installation
if [ ! -d "$ANDROID_NDK_HOME" ]; then
    log "NDK installation directory does not exist: $ANDROID_NDK_HOME"
    exit 1
fi

log "NDK is installed at $ANDROID_NDK_HOME"
