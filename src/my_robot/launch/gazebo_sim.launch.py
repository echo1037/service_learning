import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import Command
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_share = get_package_share_directory('my_robot')
    xacro_file = os.path.join(pkg_share, 'urdf', 'robot2.xacro')
    gazebo_launch_file = os.path.join(
        get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py'
    )

    # 1. 启动 Gazebo（gazebo_ros2_control 插件会在内部创建 controller_manager）
    gazebo = IncludeLaunchDescription(PythonLaunchDescriptionSource(gazebo_launch_file))

    # 2. 启动 robot_state_publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': Command(['xacro ', xacro_file]),
            'use_sim_time': True,
        }]
    )

    # 3. 生成机器人到 Gazebo（略抬高，避免生成时轮子穿地）
    spawn_entity_node = Node(
        package='gazebo_ros', executable='spawn_entity.py',
        arguments=[
            '-topic', '/robot_description',
            '-entity', 'my_robot',
            '-x', '0', '-y', '0', '-z', '0.05',
        ],
        output='screen'
    )

    # 4. 激活关节状态广播器（等 spawn 完成后再加载，避免 controller_manager 尚未就绪）
    joint_state_broadcaster_spawner = Node(
        package='controller_manager', executable='spawner',
        arguments=['joint_state_broadcaster', '-c', '/controller_manager'],
    )

    # 5. 激活差速驱动控制器
    diff_drive_spawner = Node(
        package='controller_manager', executable='spawner',
        arguments=['diff_drive_base_controller', '-c', '/controller_manager'],
    )

    # spawn 结束后再加载关节状态广播器；广播器起来后再加载差速控制器
    load_joint_state_broadcaster = RegisterEventHandler(
        OnProcessExit(
            target_action=spawn_entity_node,
            on_exit=[joint_state_broadcaster_spawner],
        )
    )
    load_diff_drive = RegisterEventHandler(
        OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[diff_drive_spawner],
        )
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher_node,
        spawn_entity_node,
        load_joint_state_broadcaster,
        load_diff_drive,
    ])
