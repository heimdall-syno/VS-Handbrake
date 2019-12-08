VS-Transmission
=========

VS-Handbrake is a simple python tool for renaming and relocating converted files.

----

#### Installation

Setup:
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
    -v /volume1/docker:/docker:rw \
    -v /volume1/docker/handbrake/vs-handbrake:/data:rw \
    jlesage/handbrake

$ sudo docker exec -it Handbrake apk add python
$ sudo docker exec -it Handbrake apk add mediainfo
```
#### Container configuration

Port settings:
```
Local port    | Container port
--------------+---------------
5800          | 5800
```

Volume settings:
```
Folder                                            | Mount-Path            | Type
--------------------------------------------------+-----------------------+-----
/volume1/docker/handbrake/config                  | /config               | rw
/volume1/docker/handbrake/storage                 | /storage              | rw
/volume1/docker/handbrake/watch                   | /watch                | rw
/volume1/docker/handbrake/output                  | /output               | rw
/volume1/docker/handbrake/convert                 | /convert              | rw
/volume1/docker                                   | /docker               | rw
/volume1/docker/handbrake/vs-handbrake            | /data                 | rw
```

Network settings:
```
Name     | Driver
---------+---------
bridge   | bridge
```