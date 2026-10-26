"""Bring up the complete real dVRK system and both RViz views."""

from launch.actions import OpaqueFunction
from launch.conditions import IfCondition
from pathlib import Path
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
    TextSubstitution,
)
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    system_config = LaunchConfiguration('system_config')
    use_sim_time = False
    rate = LaunchConfiguration('rate')
    show_rcm = LaunchConfiguration('show_rcm')

    repository_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir)
    )
    model_launch = os.path.join(
        get_package_share_directory('dvrk_model'),
        'launch',
        'arm_state_publishers.launch.py',
    )

    actions = [
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
                'system-SUJ-ECM-MTML-PSM2-MTMR-PSM1-Teleop.json',
            )),
            description='Combined real-hardware dVRK system JSON file',
        ),
        DeclareLaunchArgument('rate', default_value='50.0'),
        DeclareLaunchArgument('show_rcm', default_value='true'),
        OpaqueFunction(function=lambda context: [
            Node(
                package='dvrk_robot',
                executable='dvrk_system',
                arguments=['-j', system_config] + (['-P', '0'] if IfCondition(LaunchConfiguration('use_rviz')).evaluate(context) else []),
                output='screen',
            )
        ]),
    ]

    # Classic has no SUJ read boards: publish calibrated fixed mounting frames.
    actions.append(IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(os.path.dirname(__file__), 'fixed_base_frames.launch.py')),
        condition=IfCondition(LaunchConfiguration('use_rviz')),
    ))

    # Patient-side arms use Classic models attached to the calibrated bases.
    for arm in ['ECM', 'PSM1', 'PSM2']:
        actions.append(IncludeLaunchDescription(
            condition=IfCondition(LaunchConfiguration('use_rviz')),
            launch_description_source=PythonLaunchDescriptionSource(model_launch),
            launch_arguments={
                'arm': arm,
                'generation': 'Classic',
                'instrument': '',
                'endoscope': '',
                'use_sim_time': 'false',
                'rate': rate,
                'suj': 'true',
                'show_rcm': show_rcm,
            }.items(),
        ))

    # Surgeon-side arms are Classic MTMs and are not attached to the SUJ.
    for arm in ['MTML', 'MTMR']:
        actions.append(IncludeLaunchDescription(
            condition=IfCondition(LaunchConfiguration('use_rviz')),
            launch_description_source=PythonLaunchDescriptionSource(model_launch),
            launch_arguments={
                'arm': arm,
                'generation': 'Classic',
                'instrument': '',
                'endoscope': '',
                'use_sim_time': 'false',
                'rate': rate,
                'suj': 'false',
                'show_rcm': show_rcm,
            }.items(),
        ))

    actions.extend([
        Node(
            condition=IfCondition(LaunchConfiguration('use_rviz')),
            package='rviz2',
            executable='rviz2',
            name='rviz2_patient_cart',
            arguments=['-d', PathJoinSubstitution([
                FindPackageShare('dvrk_model'),
                'rviz',
                'Classic',
                'patient_cart.rviz',
            ])],
            output='log',
        ),
        Node(
            condition=IfCondition(LaunchConfiguration('use_rviz')),
            package='rviz2',
            executable='rviz2',
            name='rviz2_surgeon_console',
            arguments=['-d', PathJoinSubstitution([
                FindPackageShare('dvrk_model'),
                'rviz',
                'Classic',
                'surgeon-console.rviz',
            ])],
            output='log',
        ),
    ])

    return LaunchDescription(actions)
