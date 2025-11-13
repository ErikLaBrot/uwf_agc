from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # Get package directory
    pkg_dir = get_package_share_directory('agc_golfcart_sim')
    
    # Path to controller config
    controller_config = os.path.join(pkg_dir, 'config', 'ros2_controllers.yaml')
    
    return LaunchDescription([

        Node(
            package='ros2_control_node',
            executable='ros2_control_node',
            parameters=[controller_config],
            output='screen'
        ),
        # Spawn joint state broadcaster
        
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
            output='screen'
        ),
 
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['joint_state_broadcaster'],
            ),

        # Spawn steering controllers
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['front_left_steering_controller', '--controller-manager', '/controller_manager'],
            output='screen'
        ),
        
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['front_right_steering_controller', '--controller-manager', '/controller_manager'],
            output='screen'
        ),
        
        # Spawn wheel velocity controllers
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['front_left_wheel_controller', '--controller-manager', '/controller_manager'],
            output='screen'
        ),
        
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['front_right_wheel_controller', '--controller-manager', '/controller_manager'],
            output='screen'
        ),
        
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['rear_left_wheel_controller', '--controller-manager', '/controller_manager'],
            output='screen'
        ),
        
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['rear_right_wheel_controller', '--controller-manager', '/controller_manager'],
            output='screen'
        ),
    ])