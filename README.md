VS-Handbrake
=========

VS-Handbrake is an extension of the handbrake docker container (https://github.com/jlesage/docker-handbrake) for renaming and relocating converted video files to perfectly match with Synology's VideoStation.

It is the second part of the VS-Toolchain to download, convert, rename and relocate video files for Synology's VideoStation.

Checkout the first part of the toolchain - called VS-Transmission (https://github.com/salsh/vs-handbrake) - which performs the downloading part.

## Quick Start

1. Create a docker container of the handbrake image with extended volumes
```
$ sudo docker run -d \
    --name=Handbrake \
    --device /dev/dri \
    -p 5800:5800 \
    -v /volume1/docker/handbrake/config:/config:rw \
    -v /volume1/docker/handbrake/storage:/storage:ro \
    -v /volume1/docker/handbrake/watch:/watch:rw \
    -v /volume1/docker/handbrake/output:/output:rw \
    -v /volume1/docker/handbrake/convert:/convert:rw \
    -v /volume1/docker/handbrake:/data:rw \
    jlesage/handbrake
```

2. Make sure the task (task planer) for the /dev/dri device is configured:
	```
    Task:       Docker-Handbrake
    User:       root
    Command:    bash /volume1/docker/handbrake/dri.sh
    ```

3. Make sure the container is up and running. If so install all dependencies:
    ```
    $ sudo ./autogen.sh
    ```

4. Edit the config file to define which mounts belongs to which video file category (movies or series)