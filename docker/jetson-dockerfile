# Base = the same image you use in compose
ARG BASE=nvcr.io/nvidia/isaac/ros:aarch64-ros2_humble_adc428c7077de4984a00b63c55903b0a
FROM ${BASE} AS build

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-lc"]

# 1) OS/ROS tools & deps (add other ROS pkgs you want, now they're baked-in)
RUN apt-get update && apt-get install -y \
    git build-essential cmake pkg-config python3-colcon-common-extensions \
    libusb-1.0-0-dev libssl-dev libgtk-3-dev libglfw3-dev \
    libgl1-mesa-dev libglu1-mesa-dev \
    ros-humble-image-transport ros-humble-image-transport-plugins \
    ros-humble-camera-info-manager ros-humble-cv-bridge ros-humble-vision-opencv \
    ros-humble-serial-driver ros-humble-tf2-ros ros-humble-robot-state-publisher \
    ros-humble-ros2bag ros-humble-rosbag2-storage-default-plugins \
 && rm -rf /var/lib/apt/lists/*

# 2) Build & install librealsense (SDK) with RSUSB backend and CLI tools
WORKDIR /opt
RUN git clone --depth=1 https://github.com/IntelRealSense/librealsense.git
WORKDIR /opt/librealsense
RUN mkdir build && cd build && \
    cmake .. \
      -DCMAKE_BUILD_TYPE=Release \
      -DFORCE_RSUSB_BACKEND=ON \
      -DBUILD_EXAMPLES=OFF \
      -DBUILD_GRAPHICAL_EXAMPLES=OFF \
      -DBUILD_TOOLS=ON && \
    make -j"$(nproc)" && make install && ldconfig

# Optional: udev rules (not strictly needed with privileged containers)
RUN cp config/99-realsense-libusb.rules /etc/udev/rules.d/ || true

# 3) Build realsense-ros in an internal workspace
ENV ROS_DISTRO=humble
RUN mkdir -p /opt/ros_ws/src
WORKDIR /opt/ros_ws/src
RUN git clone --depth=1 -b ros2-master https://github.com/IntelRealSense/realsense-ros.git

WORKDIR /opt/ros_ws
# Try both since some Isaac images don’t provide /opt/ros/humble
RUN (source /opt/ros/${ROS_DISTRO}/setup.bash 2>/dev/null || source /opt/ros/setup.bash 2>/dev/null || true) \
    && colcon build --symlink-install

# 4) Lightweight entrypoint that sources both ROS and the overlay if present
RUN printf '%s\n' \
'#!/bin/bash' \
'set -e' \
'if [ -f /opt/ros/humble/setup.bash ]; then source /opt/ros/humble/setup.bash; fi' \
'if [ -f /opt/ros/setup.bash ]; then source /opt/ros/setup.bash; fi' \
'if [ -f /opt/ros_ws/install/setup.bash ]; then source /opt/ros_ws/install/setup.bash; fi' \
'exec "$@"' > /usr/local/bin/ros_entrypoint.sh \
 && chmod +x /usr/local/bin/ros_entrypoint.sh

FROM ${BASE} AS final
COPY --from=build /usr/local/ /usr/local/
COPY --from=build /etc/udev/rules.d/ /etc/udev/rules.d/
COPY --from=build /opt/ros_ws /opt/ros_ws
COPY --from=build /usr/local/bin/ros_entrypoint.sh /usr/local/bin/ros_entrypoint.sh
ENTRYPOINT ["/usr/local/bin/ros_entrypoint.sh"]
CMD ["bash"]
