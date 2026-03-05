import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node


def generate_launch_description():
    world = os.path.join(
        os.path.expanduser('~'),
        'ros2_ws', 'install', 'weed_detector',
        'share', 'weed_detector', 'worlds', 'farm_world.world'
    )

    gzserver = ExecuteProcess(
        cmd=[
            'gzserver', '--verbose', world,
            '-s', 'libgazebo_ros_init.so',
            '-s', 'libgazebo_ros_factory.so'
        ],
        output='screen'
    )

    gzclient = ExecuteProcess(
        cmd=['gzclient'],
        output='screen'
    )

    yolo_node = Node(
        package='weed_detector',
        executable='yolo_detector_node',
        name='yolo_detector',
        output='screen'
    )

    sprayer_node = Node(
        package='weed_detector',
        executable='sprayer_node',
        name='sprayer',
        output='screen'
    )

    return LaunchDescription([
        gzserver,
        TimerAction(period=5.0, actions=[gzclient]),
        TimerAction(period=6.0, actions=[yolo_node]),
        TimerAction(period=6.0, actions=[sprayer_node]),
    ])
