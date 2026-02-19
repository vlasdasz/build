#!/bin/bash

set -euox pipefail

unset CFLAGS
unset CXXFLAGS

source env.sh

rustup target add aarch64-apple-ios x86_64-apple-ios
cargo install cargo-lipo

cargo lipo -p $APP_NAME --release
