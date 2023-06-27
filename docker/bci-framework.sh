#!/usr/bin/bash

current_datetime=$(date +"%Y%m%d_%H%M%S")
mkdir "/home/$USER/.bciframework_docker_$current_datetime"
sudo chmod -R 777 "/home/$USER/.bciframework_docker_$current_datetime"
xhost +local:docker
docker pull dunderlab/bci_framework:latest
docker run --name=bciframework --network=host --privileged -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v /dev/dri:/dev/dri -v "/home/$USER/.bciframework_docker_$current_datetime":/home/user/.bciframework dunderlab/bci_framework
