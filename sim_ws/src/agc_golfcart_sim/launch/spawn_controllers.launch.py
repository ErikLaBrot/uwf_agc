from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # Get package directory
    pkg_dir = get_package_share_directory('agc_golfcart_sim')

    # Path to controller config
    controller_config = os.path.join(pkg_dir, 'config', 'ros2_controllers.yaml')

    # Declare robot_description argument to be passed from parent launch
    robot_description_arg = DeclareLaunchArgument(
        'robot_description',
        default_value='',
        description='Robot description from URDF/xacro'
    )

    return LaunchDescription([
        robot_description_arg,

        # ROS2 Control Node
        Node(
            package='ros2_control_node',
            executable='ros2_control_node',
            parameters=[
                controller_config,
                {'robot_description': LaunchConfiguration('robot_description')}
            ],
            output='screen'
        ),

        # Spawn joint state broadcaster
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
            output='screen'
        ),

        # Spawn steering controller (single controller for steering input)
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['steering_controller', '--controller-manager', '/controller_manager'],
            output='screen'
        ),

        # Spawn rear drive controller (group controller for both rear wheels)
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['rear_drive_controller', '--controller-manager', '/controller_manager'],
            output='screen'
        ),
    ])