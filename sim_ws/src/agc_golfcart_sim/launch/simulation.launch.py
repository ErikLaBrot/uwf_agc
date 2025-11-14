import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution
from launch.actions import OpaqueFunction
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    # Get package directories
    pkg_ros_ign_gazebo = get_package_share_directory('ros_ign_gazebo')
    pkg_agc_sim = get_package_share_directory('agc_golfcart_sim')
    
    # Paths to world and model
    world_file = os.path.join(pkg_agc_sim, 'worlds', 'uwf_empty.world')
    model_path = os.path.join(pkg_agc_sim, 'models')
    model_sdf = os.path.join(model_path, 'golfcart', 'model.xacro.urdf')
    controller_config = os.path.join(pkg_agc_sim, 'config', 'ros2_controllers.yaml')

    # Launch Gazebo with the world file
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_ign_gazebo, 'launch', 'ign_gazebo.launch.py')
        ),
        launch_arguments={
            'ign_args': f'{world_file}',
        }.items(),
    )
    

    robot_description_content = ParameterValue(
        Command([
            PathJoinSubstitution([FindExecutable(name='xacro')]),
            ' ',
            PathJoinSubstitution([
                FindPackageShare('agc_golfcart_sim'),
                'models',
                'golfcart',
                'model.xacro.urdf'
            ])
        ]),
        value_type=str
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_content}]
    )

    # Spawn the golf cart model using processed SDF
    spawn_entity = Node(
        package='ros_ign_gazebo',
        executable='create',
        arguments=[
            '-topic', 'robot_description',  # Changed from -file
            '-name', 'uwf_golfcart',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '1.0',
            '-Y', '0.0'
        ],
        output='screen'
    )


    # Bridge to connect Gazebo topics to ROS2 topics
    bridge = Node(
        package='ros_ign_bridge',
        executable='parameter_bridge',
        arguments=[
            '/lidar@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan',
            '/cmd_vel@geometry_msgs/msg/Twist@ignition.msgs.Twist',
            '/imu@sensor_msgs/msg/Imu[ignition.msgs.IMU',
            '/gps@sensor_msgs/msg/NavSatFix[ignition.msgs.NavSat',
            '/joint_states@sensor_msgs/msg/JointState[ignition.msgs.Model',
        ],
        output='screen'
    )

    # Include controller spawner launch file
    spawn_controllers = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_agc_sim, 'launch', 'spawn_controllers.launch.py')
        )
    )

    # Include C2000 bridge launch file
    c2000_bridge = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_agc_sim, 'launch', 'c2000_sim_bridge.launch.py')
        )
    )

    return LaunchDescription([
        # Set environment variables for Gazebo plugins and resources
        SetEnvironmentVariable('IGN_GAZEBO_RESOURCE_PATH', model_path),
        SetEnvironmentVariable('AGC_CONFIG_PATH', os.path.join(pkg_agc_sim, 'config')),
        SetEnvironmentVariable('IGN_GAZEBO_SYSTEM_PLUGIN_PATH',
                              os.path.join(pkg_agc_sim, 'lib') + ':' +
                              os.environ.get('IGN_GAZEBO_SYSTEM_PLUGIN_PATH', '')),

        # Start Gazebo and robot state publisher immediately
        gazebo,
        robot_state_publisher,

        # Spawn robot entity after Gazebo loads (10 second delay)
        TimerAction(
            period=10.0,
            actions=[spawn_entity]
        ),

        # Start ros_ign_bridge after robot spawns (12 second delay)
        TimerAction(
            period=12.0,
            actions=[bridge]
        ),

        # Spawn controllers after robot and bridge are ready (15 second delay)
        TimerAction(
            period=15.0,
            actions=[spawn_controllers]
        ),

        # Start C2000 bridge after controllers are spawned (20 second delay)
        TimerAction(
            period=20.0,
            actions=[c2000_bridge]
        ),
    ])