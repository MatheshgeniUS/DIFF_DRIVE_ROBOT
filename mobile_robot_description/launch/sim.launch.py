import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import Command
from launch.actions import IncludeLaunchDescription, ExecuteProcess, RegisterEventHandler

def generate_launch_description():
    pkg_name = 'mobile_robot_description'
    pkg_share = get_package_share_directory(pkg_name)

    # 1. Robot State Publisher
    urdf_file = os.path.join(pkg_share, 'urdf', 'mobile_robot.urdf.xacro')
    robot_description = Command(['xacro ', urdf_file])
    
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description, 'use_sim_time': True}]
    )

    # 2. Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
        launch_arguments={'gz_args': '-r empty.sdf'}.items(),
    )

    # 3. Spawn Robot in Gazebo
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'jazzy_bot', '-z', '0.1'],
        output='screen',
    )

    # 4. Controllers (Broadcaster and Diff Drive)
    load_joint_state_broadcaster = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 'joint_state_broadcaster'],
        output='screen'
    )

    load_diff_drive_controller = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 'diff_drive_controller'],
        output='screen'
    )

    # Path to the bridge config
    bridge_params = os.path.join(pkg_share, 'config', 'bridge.yaml')

    # Start the ROS-GZ Bridge
    start_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['--ros-args', '-p', f'config_file:={bridge_params}'],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        node_robot_state_publisher,
        spawn_robot,
        start_bridge,

        # Wait for robot to spawn before loading controllers
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=spawn_robot,
                on_exit=[load_joint_state_broadcaster],
            )
        ),
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=load_joint_state_broadcaster,
                on_exit=[load_diff_drive_controller],
            )
        ),
    ])