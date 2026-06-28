from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch.actions import DeclareLaunchArgument
from launch.actions import ExecuteProcess

def generate_launch_description():

    return LaunchDescription([
        Node(
            package='amp_sm',
            executable='repeater_lifecycle_node.py',
            name='repeater_node',
            output='screen'
        )
    ])