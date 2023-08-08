# My Minecraft Server

This is a Docker-based Minecraft server.

## Building

To build:

    docker build -t my-minecraft:1.20.1 .    

The image is based on Fedora 38 and uses the `java-latest-openjdk` (Java 20 at the time of writing).

It includes a [Spigot Minecraft server](https://spigotmc.org) compatible with Minecraft 1.20.1. The server is built using the latest [Spigot BuildTools](https://hub.spigotmc.org/jenkins/job/BuildTools/).

The default settings are in [`server.properties`](server.properties). 

Within the image, the `/opt/minecraft` directory contains the server settings, binary JAR, and launch script. Launching the server sets up the actual runtime at `/opt/minecraft-runtime`. I recommend configuring this directory as a volume or local mount (`-v`), or the entire server will get wiped when the container gets deleted.

## Usage

The commands below have been tested as working on Linux (using native Docker) and Windows (using Docker Desktop). It works based on the following assumptions:

  * You are using a Bash-like terminal (`bash` or `zsh` on Linux/Mac; Cygwin/Gitbash or similar on Windows).
  * The served port is the default of 25565.
  * The resulting container is ephemeral (can be created/destroyed with no data loss).
  * The container has the name `my-minecraft`.
  * Minecraft working files (JARs, configurations, plugins, and the world) are stored in `runtime` relative to the current directory, and mounted into the container. This protects them from deletion, and allows easy access from outside the container (for backups, changes to configuration, etc).
  * Java parameters are configured using the recommendations from [here](https://aikar.co/2018/07/02/tuning-the-jvm-g1gc-garbage-collector-flags-for-minecraft/). See [container_entrypoint.sh](container_entrypoint.sh) for more details.

The below commands are super detailed and could be bundled into some clever `docker run` or other commands. If you are comfortable with Docker, those should work too.

### Create the server container

Once you have the `my-minecraft:1.20.1` image, you can create a container based on it by using:

    docker create \
        --name my-minecraft \
        --interactive --tty \
        --mount 'type=bind,target=/opt/minecraft-runtime,source=/path/to/runtime/dir' \
        --restart unless-stopped \
        -p 25565:25565 \
        my-minecraft:1.20.1

Modify `/path/to/runtime/dir` to be the actual (absolute!) path to the local directory where to store the Minecraft runtime files (JARs, plugins, resource packs, world). On Windows, you should use the actual Windows path (`C:\foo\bar`) rather than the Cygwin path (`/c/foo/bar`).

> **Docker Desktop (Windows/Mac) Note:** If you are using Docker Desktop, using a local directory mount will result in poor disk performance for the Minecraft server, which may impact the experience of using it.
> Consider using a volume mount instead. To do so, replace the `--mount` line with:
>
>     --mount 'type=volume,source=my-minecraft-runtime,target=/opt/minecraft-runtime' \
>
> This will create and mount a Docker volume called `my-minecraft-runtime` to store the files, instead of using a slow VM-mounted local directory.
 
If you would like to expose the server on a different port, like 1234, you can change the port option accordingly `-p 1234:25565`. If you would like to not expose the port to the network, you can use `-p 127.0.0.1:1234:25565`.

Note that this command will fail if the `my-minecraft` container already exists. See below about how to manage an existing container. Changing any of the options requires deleting the container.


### Managing the container

Start as a background process:

    docker start my-minecraft

Stop:

    docker stop my-minecraft

You can also delete a stopped container entirely. This means deleting everything in it that is not volume-mounted (e.g. the `runtime/` folder). If you are not volume mounting somehow, your whole world will be lost. Use this command with care.

    docker rm my-minecraft

To run an interactive Linux shell within the container, use:

    docker exec -it my-minecraft bash

### Logs

Use `docker logs my-minecraft` to view the logs. Provide other options to the command to modify how you view them (see `docker logs --help` for details). Examples:

* View the last 20 lines of logs: `docker logs -n 20 my-minecraft`.
* Print all logs, and continue watching/following for more output: `docker logs -f my-minecraft`.

### Managing the server with the Minecraft CLI

Minecraft server being managed via the CLI, but this container runs in the "background". To access the CLI (and bring the container into the foreground), use:

    docker attach my-minecraft

**Do not exit this shell using Ctrl+D, Ctrl+C, or otherwise end the process**. Doing so affects the Minecraft process directly, and would shut down the server entirely. Instead, use the Docker detach sequence: `Ctrl+P`, `Ctrl+Q`.

If you do accidentally do so, it should restart by itself (thanks to the restart option in the  creation command).

## Managing the files of the server

Some command examples:

* Copy a file/dir into the container: `docker cp /path/to/local/source my-minecraft:/path/to/container/destination`
* Copy a file/dir out of the container: `docker cp my-minecraft:/path/to/container/source /path/to/local/destination`
* Back up the Minecraft server working directory, as a TGZ archive: `docker cp my-minecraft:/opt/minecraft-runtime - | gzip > backup.tar.gz`

If you are mounting a local directory into the container you can also manage the server files directly. For example, you could add a plugin such as _Dynmap_ directly to `runtime/plugins/` using your local file manager.

# Usage with Linux `systemd`

> TODO
