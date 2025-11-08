from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace

def generate_launch_description():
    ns   = LaunchConfiguration('namespace')
    port = LaunchConfiguration('port')
    baud = LaunchConfiguration('baud')
    woc  = LaunchConfiguration('write_on_change')
    rate = LaunchConfiguration('rate_hz')

    return LaunchDescription([
        DeclareLaunchArgument('namespace', default_value='',
                              description='Optional ROS namespace'),
        DeclareLaunchArgument('port', default_value='/dev/ttyUSB0',
                              description='Serial device for C2000'),
        DeclareLaunchArgument('baud', default_value='115200',
                              description='Baud rate'),
        DeclareLaunchArgument('write_on_change', default_value='true',
                              description='Send only when msg updates'),
        DeclareLaunchArgument('rate_hz', default_value='50',
                              description='TX rate if write_on_change=false'),

        GroupAction([
            PushRosNamespace(ns),
            Node(
                package='agc_c2000_interface',
                executable='c2000_tx',
                name='c2000_tx',
                parameters=[{
                    'port': port,
                    'baud': baud,
                    'write_on_change': woc,
                    'rate_hz': rate,
                }],
                output='screen',
            ),
        ])
    ])
