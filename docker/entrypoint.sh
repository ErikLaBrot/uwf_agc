#!/bin/bash
set -e

# Source base ROS installation
if [ -f "/opt/ros/humble/setup.bash" ]; then
    source /opt/ros/humble/setup.bash
fi

# If we've already built this workspace before, also source its overlay
if [ -f "/home/${USER}/ros_ws/install/setup.bash" ]; then
    source /home/${USER}/ros_ws/install/setup.bash
fi

# Enable colcon tab completion if available
if command -v register-python-argcomplete3 >/dev/null 2>&1; then
    eval "$(register-python-argcomplete3 colcon)" || true
fi

exec "$@"
