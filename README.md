VS-Handbrake
=========

VS-Handbrake is an extension of the handbrake docker container (https://github.com/jlesage/docker-handbrake) for renaming and relocating converted video files to perfectly match with Synology's VideoStation.

It is the second part of the VS-Toolchain to download, convert, rename and relocate video files for Synology's VideoStation.

Checkout the first part of the toolchain - called VS-Transmission (https://github.com/salsh/vs-handbrake) - which performs the downloading part.

## Overview of the VS-Toolchain
```
+---------------------------------------------------------------------------------------------------------+
|                                             Synology DSM                                                |
+---------------------------------------------------------------------------------------------------------+
|                                                                                    +-----------------+  |
|                                                                                    |      DSM        |  |
|  +--------------------+                                                            |VS-Playlist-Share|  |
|  |       Docker       +-------+                                                    |   (Optional)    |  |
|  |transmission openVpn|       |                                                    +-----------------+  |
|  +--------------------+       v                                                                         |
|            or            +----+------------+   +------------+   +--------------+    +---------------+   |
|  +--------------------+  |    DSM/Docker   +-->+   Docker   +-->+    Docker    +--->+     DSM       |   |
|  |        DSM         +--+ VS-Transmission |   |  Handbrake |   | VS-Handbrake |    |VS-Notification|   |
|  |    Transmission    |  |    (Required)   +-+ | (Optional) |   |  (Optional)  +--+ |  (Optional)   |   |
|  +--------------------+  +----+------------+ | +------------+   +--------------+  | +---------------+   |
|            or                 |              |                                    |                     |
|  +--------------------+       |              |                                    |                     |
|  |        DSM         +-------+              |                                    |                     |
|  |  Download-Station  |                      v                                    v                     |
|  +--------------------+    +-----------------+------------------------------------+------------------+  |
|                            |                                DSM Task                                 |  |
|                            |                              VS-SynoIndex                               |  |
|                            |                               (Required)                                |  |
|                            +-------------------------------------------------------------------------+  |
+---------------------------------------------------------------------------------------------------------+
```


Check out the other components:


VS-SynoIndex:      https://github.com/heimdall-syno/VS-SynoIndex

VS-Transmission:   https://github.com/heimdall-syno/VS-Transmission

VS-Notification:   https://github.com/heimdall-syno/VS-Notification

VS-Playlist-Share: https://github.com/heimdall-syno/VS-Playlist-Share

## Result

**Movie-based formats**
- Index original until converted file exists then keep the original,
- Extract archive, index files until converted ones exist then delete them

```
/volume1/Movies/
  Joker.2019.AC3.1080p.BluRay.h264-xX/
    Joker.AC3.1080p.BluRay.x264-xX.mkv       (Original, Indexed until converted version exists -> ignored)
    Joker.mkv                                (Result, Renamed/Indexed by VS-Handbrake - e.g. x265)

  Bloodshot.2020.DL.1080p.BluRay.x264-xX/
    xx-hd-bloodshot-1080p.rar                (Original, Extracted)
    xx-hd-bloodshot-1080p.r00                (Original, Extracted)
    Bloodshot.2020.AC3.1080p.x264-xX.mkv     (Temporary, Indexed until converted file exists -> deleted)
    Bloodshot.mkv                            (Result, Renamed/Indexed by VS-Handbrake - e.g. x265)
```

**Season-based formats (TV shows, documentation etc.)**
- Index original episodes until converted file exists then keep the original,
- Extract whole season archives, index files until converted ones exist then delete extracted files

```
/volume1/Series/
  Game of Thrones/
    Season 01/
      Game of Thrones.S01.1080p.x264-xX/
          got-s01e01.1080.mkv              (Original, Indexed until converted file exists -> ignored)
          got-s01e02.1080.mkv              (Original, Indexed until converted file exists -> ignored)
      Game-of-Thrones.S01E01.1080p.mkv     (Result, Renamed/Indexed by VS-Handbrake - e.g. x265)
      Game-of-Thrones.S01E02.1080p.mkv     (Result, Renamed/Indexed by VS-Handbrake - e.g. x265)

  Carnival Row/
    Season 01/
      Carnival.Row.S01.DL.1080p.x264-xX/
          carival-row-hd-1080p.rar         (Original, Extracted)
          carnival-row.s01e01.mkv          (Temporary, Indexed until converted file exists -> ignored/deleted)
      Carnival-Row.S01E01.1080p.mkv        (Result, Renamed/Indexed by VS-Handbrake)
      Carnival-Row.S01E02.1080p.mkv        (Result, Renamed/Indexed by VS-Handbrake)
```

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
    -v /volume1/docker/logs:/logs:rw \
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