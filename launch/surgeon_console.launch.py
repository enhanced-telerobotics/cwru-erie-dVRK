from launch.actions import OpaqueFunction
from pathlib import Path
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
import os

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch import LaunchContext, LaunchDescription, Substitution
from typing import Text


from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
    TextSubstitution,
)

def generate_launch_description():
    system_config = LaunchConfiguration('system_config')
    use_sim_time = False
    rate = LaunchConfiguration('rate', default = 50.0)  # Hz, default is 10 so we're increasing that a bit.  Funny enough joint and robot state publishers don't have the same name for that parameter :-(

    repository_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir)
    )

    ld = LaunchDescription([
        DeclareLaunchArgument(
            'use_rviz', default_value='false', choices=['true', 'false'],
            description='Start RViz and model TF publishers instead of the robot TF tree.',
        ),
        DeclareLaunchArgument(
            'panel', default_value='none',
            choices=['none', 'screen', 'web', 'both'],
            description='Control panel: none, desktop screen, browser web, or both.',
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(
                Path(__file__).resolve().parent / 'control_panel.launch.py'
            )),
            launch_arguments={'panel': LaunchConfiguration('panel')}.items(),
        ),
        DeclareLaunchArgument(
            'system_config',
            default_value=TextSubstitution(text=os.path.join(
                repository_root,
                'system',
                'system-MTML-MTMR.json'
            )),
            description='dvrk_system JSON file for the real surgeon console'
        ),
        DeclareLaunchArgument('rate', default_value='50.0'),
    ])

    # dVRK system
    real_dvrk_node = OpaqueFunction(function=lambda context: [
        Node(
            package = 'dvrk_robot',
            executable = 'dvrk_system',
            arguments = ['-j', system_config] + (['-P', '0'] if IfCondition(LaunchConfiguration('use_rviz')).evaluate(context) else []),
            output = 'screen',
        )
    ])
    ld.add_action(real_dvrk_node)

    # Arm joint/robot state publishers
    for arm in ['MTML', 'MTMR']:
        model = [
            PathJoinSubstitution([FindPackageShare('dvrk_model'),
                                  'urdf/Classic/']),
            '/', arm, '.urdf.xacro'
        ]
        # Use xacro to process robot model at substitution time
        # Can't happen until substitution time when we know robot_model
        description = ParameterValue(
            Command(
                [FindExecutable(name = 'xacro'), ' ', *model]
            ),
            value_type = str,
        )
        joint_state_publisher_node = Node(
            condition=IfCondition(LaunchConfiguration('use_rviz')),
            package = 'joint_state_publisher',
            namespace = arm,
            executable = 'joint_state_publisher',
            name = arm + '_joint_state_publisher',
            parameters = [{'use_sim_time': use_sim_time,
                           'source_list': ['measured_js', 'gripper/measured_js'],
                           'rate': rate}],
            output = 'both',
        )
        robot_state_publisher_node = Node(
            condition=IfCondition(LaunchConfiguration('use_rviz')),
            package = 'robot_state_publisher',
            namespace = arm,
            executable = 'robot_state_publisher',
            name = arm + '_robot_state_publisher',
            parameters = [{'use_sim_time': use_sim_time,
                           'robot_description': description,
                           'publish_frequency': rate}],
            output = 'both',
        )
        ld.add_action(joint_state_publisher_node)
        ld.add_action(robot_state_publisher_node)

    # RViz
    rviz_config_file = [
        PathJoinSubstitution([FindPackageShare('dvrk_model'),
                              'rviz/Classic/surgeon-console.rviz'])
    ]
    rviz_node = Node(
        condition=IfCondition(LaunchConfiguration('use_rviz')),
        package = 'rviz2',
        executable = 'rviz2',
        name = 'rviz2_surgeon_console',
        arguments = ['-d', rviz_config_file],
        output = 'both',
    )
    ld.add_action(rviz_node)

    return ld
