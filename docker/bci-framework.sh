#!/usr/bin/bash

sudo chmod -R 777 /home/$USER/.bciframework_docker
xhost +local:docker
docker run --network=host --privileged -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v /dev/dri:/dev/dri -v /home/$USER/.bciframework_docker:/home/user/.bciframework dunderlab/bci_framework
