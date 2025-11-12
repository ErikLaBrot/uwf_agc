#!/usr/bin/env python3
"""
Launch file for C2000 Simulation Bridge

Starts the bridge node with parameters loaded from config file.
"""

from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    # Get package directory
    pkg_dir = get_package_share_directory('agc_golfcart_sim')
    
    # Path to parameters file
    params_file = os.path.join(pkg_dir, 'config', 'c2000_bridge_params.yaml')
    
    # C2000 bridge node
    c2000_bridge_node = Node(
        package='agc_golfcart_sim',
        executable='c2000_sim_bridge.py',
        name='c2000_sim_bridge',
        output='screen',
        parameters=[params_file],
        emulate_tty=True,
    )
    
    return LaunchDescription([
        c2000_bridge_node,
    ])
