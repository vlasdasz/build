#!/bin/bash
set -eox pipefail
source env.sh

echo "APP_NAME: $APP_NAME"

cargo build -p "$APP_NAME" --profile=release-debug

samply record ./target/release-debug/$APP_NAME
