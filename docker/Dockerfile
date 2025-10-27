# docker/Dockerfile
FROM ros:humble-ros-core

# Install typical ROS 2 dev tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-colcon-common-extensions \
    python3-argcomplete \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# We will pass in your host UID/GID so files written from inside the container
# don't show up owned by root on the host.
ARG USERNAME=dev
ARG UID=1000
ARG GID=1000

RUN groupadd -g ${GID} ${USERNAME} && \
    useradd -m -s /bin/bash -u ${UID} -g ${GID} ${USERNAME}

# Workspace location *inside* the container
ENV WS_DIR=/home/${USERNAME}/ros_ws
RUN mkdir -p ${WS_DIR}/src
WORKDIR ${WS_DIR}

# Copy in entrypoint that will source ROS for us
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
