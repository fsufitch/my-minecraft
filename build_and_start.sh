#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

set -xe 

cd "$SCRIPT_DIR"

docker build -t my-minecraft .

RUNTIME_DIR=$(cygpath -aw ./runtime || realpath ./runtime)
SUDO=$(which sudo || echo '')

echo "eula=true" | $SUDO tee "${RUNTIME_DIR}/eula.txt"

docker run -d -it \
    --name my-minecraft \
    -v "$RUNTIME_DIR:/opt/minecraft-runtime" \
    -p '25565:25565' \
    -p '8123:8123' \
    my-minecraft
