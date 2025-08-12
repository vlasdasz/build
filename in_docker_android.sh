#!/bin/bash
set -eox pipefail

HOST_DIR="${HOST_DIR:-$(pwd)}"

docker run \
    --rm \
    --mount type=bind,source="$HOST_DIR",target=/host \
    --cap-add=SYS_PTRACE \
    --security-opt seccomp=unconfined \
    -t mobiledevops/android-sdk-image \
    \
    /bin/bash -c "cd /host && export TEST_ENGINE_ANDROID_DOCKER_BUILD=true && ./build/build.sh android"
