"""Select the desktop and browser control panels for a robot launch."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def generate_launch_description():
    panel = LaunchConfiguration('panel')
    console = LaunchConfiguration('console', default='console')
    return LaunchDescription([
        DeclareLaunchArgument(
            'panel', default_value='none', choices=['none', 'screen', 'web', 'both'],
            description='Control panel: none, desktop screen, browser web, or both.',
        ),
        Node(
            package='dvrk_console', executable='control_panel',
            name='screen_control_panel', output='screen',
            arguments=['-C', console],
            condition=IfCondition(PythonExpression(["'", panel, "' in ('screen', 'both')"])),
        ),
        Node(
            package='dvrk_utils', executable='control_panel',
            name='web_control_panel', output='screen',
            prefix='/home/erie_lab/Documents/envs/torch/bin/python',
            arguments=['-C', console],
            condition=IfCondition(PythonExpression(["'", panel, "' in ('web', 'both')"])),
        ),
    ])
