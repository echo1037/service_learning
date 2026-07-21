import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # 1. 获取当前功能包的路径
    # 假设你的功能包名字叫 'first_robot_pkg'，请根据实际情况修改
    pkg_share = get_package_share_directory('my_robot')
    
    # 2. 定义 URDF 文件的绝对路径
    # 假设 urdf 文件存放在功能包下的 'urdf' 文件夹中
    urdf_file_path = os.path.join(pkg_share, 'urdf', 'first_robot.urdf')
    
    # 3. 定义 RViz 配置文件的路径 (可选)
    # 如果你还没有保存过 rviz 配置，可以注释掉下面这行，并在 Node 中移除该参数
    rviz_config_file = os.path.join(pkg_share, 'config', 'display_config.rviz')

    # 检查文件是否存在，防止启动时报错
    if not os.path.exists(urdf_file_path):
        print(f"[ERROR] URDF file not found: {urdf_file_path}")
        return LaunchDescription([])

    return LaunchDescription([
        # --- 节点 1: robot_state_publisher ---
        # 作用：读取 URDF 内容，解析连杆关系，并发布 tf 和 tf_static
        # 这是解决 "Frame [base_link] does not exist" 的关键节点
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': open(urdf_file_path).read() # 将 urdf 内容读入参数
            }]
        ),

        # --- 节点 2: joint_state_publisher ---
        # 作用：发布非固定关节的状态。
        # 如果没有这个节点，RViz 里的机械臂可能会报警告或者无法显示关节运动。
        # 它还会弹出一个 GUI 滑块让你手动拖动关节（如果不需要 GUI 可加 gui:=False）
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            output='screen',
        ),

        # --- 节点 3: rviz2 ---
        # 作用：启动可视化工具
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            # arguments=['-d', rviz_config_file], # 如果有配置文件，取消这行的注释
            arguments=['-d', os.path.join(pkg_share, 'rviz', 'default.rviz')] # 或者直接指定一个默认路径
        )
    ])