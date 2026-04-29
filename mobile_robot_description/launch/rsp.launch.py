import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue   # ← THIS is the fix
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    pkg_share = get_package_share_directory('mobile_robot_description')

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    use_sim_arg = DeclareLaunchArgument(
        'use_sim',
        default_value='true',
        description='Use simulated hardware if true'
    )

    use_sim_time = LaunchConfiguration('use_sim_time')
    use_sim      = LaunchConfiguration('use_sim')

    urdf_file = os.path.join(pkg_share, 'urdf', 'mobile_robot.urdf.xacro')

    # ← Wrap in ParameterValue with value_type=str
    robot_description = ParameterValue(
        Command(['xacro ', urdf_file, ' use_sim:=', use_sim]),
        value_type=str
    )

    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': use_sim_time
        }]
    )

    return LaunchDescription([
        use_sim_time_arg,
        use_sim_arg,
        rsp_node,
    ])