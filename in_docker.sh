#!/bin/bash
set -eox pipefail

HOST_DIR="${HOST_DIR:-$(pwd)}"

docker run \
    --rm \
    --mount type=bind,source="$HOST_DIR",target=/host \
    --cap-add=SYS_PTRACE \
    --security-opt seccomp=unconfined \
#    --platform linux/amd64 \
    -t "$1" \
    \
    /bin/bash -c "cd /host && ./build/build.sh"