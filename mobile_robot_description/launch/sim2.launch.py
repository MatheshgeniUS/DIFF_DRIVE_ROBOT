import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    pkg_name = 'mobile_robot_description'
    
    # Launch Arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default=True)

    # 1. Robot State Publisher
    # Fixed to point exactly to your 'urdf/mobile_robot.urdf.xacro' file
    robot_description_content = Command([
        PathJoinSubstitution([FindExecutable(name='xacro')]),
        ' ',
        PathJoinSubstitution([
            FindPackageShare(pkg_name),
            'urdf',
            'mobile_robot.urdf.xacro'
        ])
    ])
    
    robot_description = {'robot_description': robot_description_content, 'use_sim_time': use_sim_time}
    
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description]
    )

    # 2. Gazebo Sim
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [PathJoinSubstitution([FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py'])]
        ),
        launch_arguments=[('gz_args', [' -r -v 1 empty.sdf'])]
    )

    # 3. Spawn Robot in Gazebo
    gz_spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=['-topic', 'robot_description', '-name', 'jazzy_bot', '-z', '0.1', '-allow_renaming', 'true'],
    )

    # 4. Controller Spawners (Using the robust Node method instead of ExecuteProcess)
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
    )

    diff_drive_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        # Assuming your controller is named 'diff_drive_controller' based on your old file
        arguments=['diff_drive_controller'], 
    )

    # 5. Bridge
    bridge_params = PathJoinSubstitution([FindPackageShare(pkg_name), 'config', 'bridge.yaml'])
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['--ros-args', '-p', ['config_file:=', bridge_params]],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true', description='Use simulated clock'),
        gazebo,
        node_robot_state_publisher,
        gz_spawn_entity,
        bridge,
        
        # Sequence the controller loading AFTER the robot spawns
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=gz_spawn_entity,
                on_exit=[joint_state_broadcaster_spawner],
            )
        ),
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=joint_state_broadcaster_spawner,
                on_exit=[diff_drive_controller_spawner],
            )
        ),
    ])