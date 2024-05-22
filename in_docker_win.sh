#!/bin/bash
set -eox pipefail

HOST_DIR="${HOST_DIR:-$(pwd)}"

docker run \
    --rm \
    -p 8006:8006 \
    --device=/dev/kvm \
    --cap-add NET_ADMIN \
    --stop-timeout 120 \
    -t "$1" \
    \
    cmd -c "cd /host && py build/build.py"

# --platform linux/amd64 \
