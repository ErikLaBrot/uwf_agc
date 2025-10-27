#!/bin/bash

# Name the image and container
IMAGE_NAME=ros2-dev:humble
CONTAINER_NAME=ros2_dev

# Figure out where the project root is (one level above this script)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"

HOST_USER=$(id -un)
HOST_UID=$(id -u)
HOST_GID=$(id -g)

# Build the image if it doesn't exist
if ! docker image inspect $IMAGE_NAME >/dev/null 2>&1; then
    echo "[build] Docker image $IMAGE_NAME not found, building it..."
    docker build \
        --build-arg UID=$HOST_UID \
        --build-arg GID=$HOST_GID \
        --build-arg USERNAME=$HOST_USER \
        -t $IMAGE_NAME "$PROJECT_ROOT/docker"
fi

# Run the container
docker run -it --rm \
    --name $CONTAINER_NAME \
    --network host \
    -u $HOST_UID:$HOST_GID \
    -v "$PROJECT_ROOT/ros_ws":/home/$HOST_USER/ros_ws \
    -w /home/$HOST_USER/ros_ws \
    $IMAGE_NAME \
    bash
