from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='agc_sensors',
            executable='gps_compass',
            name='gps_compass_node',
            output='screen',
            parameters=[{
                'gps_port': '/dev/ttyTHS1',
                'baudrate': 38400,
                'compass_address': 0x1E
            }]
        )
    ])
