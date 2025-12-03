from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import TimerAction

def generate_launch_description():
    
    # Spawn joint state broadcaster immediately
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
        output='screen'
    )
    
    # Spawn steering controller with small delay
    steering_controller_spawner = TimerAction(
        period=2.0,
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=['steering_controller', '--controller-manager', '/controller_manager'],
                output='screen'
            )
        ]
    )
    
    # Spawn rear drive controller with small delay
    rear_drive_controller_spawner = TimerAction(
        period=4.0,
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=['rear_drive_controller', '--controller-manager', '/controller_manager'],
                output='screen'
            )
        ]
    )
    
    return LaunchDescription([
        joint_state_broadcaster_spawner,
        steering_controller_spawner,
        rear_drive_controller_spawner,
    ])