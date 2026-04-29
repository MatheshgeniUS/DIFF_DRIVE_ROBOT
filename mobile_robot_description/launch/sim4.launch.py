import os
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    pkg_share = get_package_share_directory('mobile_robot_description')

    # ---- 1. Robot State Publisher ----
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, 'launch', 'rsp.launch.py')
        ),
        launch_arguments={
            'use_sim_time': 'true',
            'use_sim':      'true'
        }.items()
    )

    # ---- 2. Gazebo + Spawn ----
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, 'launch', 'gazebo.launch.py')
        )
    )

    # ---- 3. Joint State Broadcaster (reads joint states from Gazebo) ----
    # Delay slightly so Gazebo is ready
    jsb_spawner = TimerAction(
        period=4.0,
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=[
                    'joint_state_broadcaster',
                    '--controller-manager', '/controller_manager'
                ],
                output='screen'
            )
        ]
    )

    # ---- 4. Diff Drive Controller ----
    diff_drive_spawner = TimerAction(
        period=4.0,
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=[
                    'diff_drive_controller',
                    '--controller-manager', '/controller_manager'
                ],
                output='screen'
            )
        ]
    )

    return LaunchDescription([
        rsp,
        gazebo,
        jsb_spawner,
        diff_drive_spawner,
    ])