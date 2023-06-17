#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

set -xe 

cd "$SCRIPT_DIR"

docker build -t my-minecraft .

RUNTIME_DIR=$(cygpath -aw ./runtime || realpath ./runtime)

docker run -d -it --rm \
    -v "$RUNTIME_DIR:/opt/minecraft-runtime" \
    -p 25565 \
    minecraft