import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node

def generate_launch_description():
    # 1. EXACT name of your package
    pkg_name = 'mobile_robot_description' 
    
    # 2. Path to the file (assuming it's in the 'urdf' subfolder)
    pkg_share = get_package_share_directory(pkg_name)
    
    # CHANGE THIS to your actual filename: robot.urdf.xacro OR mobile_robot.urdf.xacro
    urdf_model_path = os.path.join(pkg_share, 'urdf', 'mobile_robot.urdf.xacro')

    print(f"DEBUG: Looking for URDF at: {urdf_model_path}")

    # Robot State Publisher
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': Command(['xacro ', urdf_model_path])
        }]
    )

    # Joint State Publisher GUI
    node_joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui'
    )

    # RViz2
    node_rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )

    return LaunchDescription([
        node_robot_state_publisher,
        node_joint_state_publisher_gui,
        node_rviz
    ])