import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
from launch_ros.parameter_descriptions import ParameterValue  # 1. 导入 ParameterValue
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    package_name = 'my_robot'  # 请替换为你实际的功能包名称
    xacro_file = os.path.join(get_package_share_directory(package_name), 'urdf', 'robot2.xacro')

    return LaunchDescription([
        # 2. 使用 ParameterValue 包装，并显式声明 value_type=str
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{
                'robot_description': ParameterValue(
                    Command(['xacro ', xacro_file]), 
                    value_type=str
                )
            }]
        ),

        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher'
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2'
        )
    ])