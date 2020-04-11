VS-Handbrake
=========

VS-Handbrake is an extension of the handbrake docker container (https://github.com/jlesage/docker-handbrake) for renaming and relocating converted video files to perfectly match with Synology's VideoStation.

It is the second part of the VS-Toolchain to download, convert, rename and relocate video files for Synology's VideoStation.

Checkout the first part of the toolchain - called VS-Transmission (https://github.com/salsh/vs-handbrake) - which performs the downloading part.

## Overview of the VS-Components
```
             +---------------------------------------------------------------------------------+
             |                                  Synology DSM                                   |
             +---------------------------------------------------------------------------------+
             |                  +--------------------+  +-----------------+                    |
             |                  |       Docker       |  |      Docker     |                    |
             |                  |transmission.openVpn|  |     Handbrake   |                    |
             |                  +--------------------+  +-----------------+                    |
             | +------------+   | +---------------+  |  | +-------------+ |  +---------------+ |
             | |VS-SynoIndex|   | |VS-Transmission|  |  | | VS-Handbrake| |  |VS-Notification| |
             | |   (Task)   +---->+   (Script)    +------>+   (Script)  +--->+    (Task)     | |
             | +------------+   | +---------------+  |  | +-------------+ |  +---------------+ |
             |                  +--------------------+  +-----------------+                    |
             |                                                                                 |
             +---------------------------------------------------------------------------------+
```

Check out the other components:


VS-SynoIndex:      https://github.com/heimdall-syno/VS-SynoIndex

VS-Transmission:   https://github.com/heimdall-syno/VS-Transmission

VS-Notification:   https://github.com/heimdall-syno/VS-Notification

VS-Playlist-Share: https://github.com/heimdall-syno/VS-Playlist-Share

## Quick Start

1. Setup VS-Transmission and VS-SynoIndex as described in the corresponding README.

2. Clone the repository inside the root directory of the handbrake docker directory.

3. Create a docker container of the handbrake image with extended volumes
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

3. Make sure the Triggered Task (Control Panel > Task Scheduler) for the /dev/dri device is configured:
	```
    Task:       Docker-Handbrake
    User:       root
    Command:    bash /volume1/docker/handbrake/dri.sh
    ```

4. Make sure the container is up and running. If so install all dependencies:
    ```
    $ sudo ./autogen.sh
    ```

5. Edit the port number according to your VS-SynoIndex configuration in `post_conversion.sh`

6. Edit the config file to define which mounts belongs to which video file category (movies or series)