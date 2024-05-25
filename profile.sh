#!/bin/bash
set -eox pipefail
source env.sh

echo "APP_NAME: $APP_NAME"
echo "CARGO_PROFILE_FOR_PROFILING: $CARGO_PROFILE_FOR_PROFILING"

cargo install --locked samply

cargo build -p "$APP_NAME" --profile="$CARGO_PROFILE_FOR_PROFILING"

if [ "$CARGO_PROFILE_FOR_PROFILING" = "dev" ]; then
    CARGO_PROFILE_FOR_PROFILING="debug"
fi

samply record ./target/"$CARGO_PROFILE_FOR_PROFILING"/"$APP_NAME"
