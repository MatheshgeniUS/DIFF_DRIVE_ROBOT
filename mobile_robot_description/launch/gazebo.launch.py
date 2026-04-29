import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    pkg_share  = get_package_share_directory('mobile_robot_description')
    ros_gz_sim = get_package_share_directory('ros_gz_sim')

    world_file = os.path.join(pkg_share, 'worlds', 'empty.world')

    world_arg = DeclareLaunchArgument(
        'world',
        default_value=world_file,
        description='Path to Gazebo world file'
    )

    # Start Gazebo (Harmonic)
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': ['-r -v4 ', LaunchConfiguration('world')],
        }.items()
    )

    # Spawn robot from /robot_description topic
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', '/robot_description',
            '-name',  'jazzy_bot',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.05',
        ],
        output='screen'
    )

    # Bridge — connects Gazebo clock to ROS2
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen'
    )

    return LaunchDescription([
        world_arg,
        gazebo,
        spawn_robot,
        bridge,
    ])