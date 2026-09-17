"""Bring up the complete real dVRK system and both RViz views."""

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
    use_sim_time = LaunchConfiguration('use_sim_time')
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
            'system_config',
            default_value=TextSubstitution(text=os.path.join(
                repository_root,
                'system',
                'system-SUJ-ECM-MTML-PSM2-MTMR-PSM1-Teleop.json',
            )),
            description='Combined real-hardware dVRK system JSON file',
        ),
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('rate', default_value='50.0'),
        DeclareLaunchArgument('show_rcm', default_value='true'),
        Node(
            package='dvrk_robot',
            executable='dvrk_system',
            arguments=['-j', system_config],
            output='screen',
        ),
    ]

    # Classic has no SUJ read boards: publish calibrated fixed mounting frames.
    actions.append(IncludeLaunchDescription(PythonLaunchDescriptionSource(
        os.path.join(os.path.dirname(__file__), 'fixed_base_frames.launch.py'))))

    # Patient-side arms use Si models attached to the SUJ.
    for arm in ['ECM', 'PSM1', 'PSM2']:
        actions.append(IncludeLaunchDescription(
            PythonLaunchDescriptionSource(model_launch),
            launch_arguments={
                'arm': arm,
                'generation': 'Classic',
                'instrument': '',
                'endoscope': '',
                'use_sim_time': use_sim_time,
                'rate': rate,
                'suj': 'true',
                'show_rcm': show_rcm,
            }.items(),
        ))

    # Surgeon-side arms are Classic MTMs and are not attached to the SUJ.
    for arm in ['MTML', 'MTMR']:
        actions.append(IncludeLaunchDescription(
            PythonLaunchDescriptionSource(model_launch),
            launch_arguments={
                'arm': arm,
                'generation': 'Classic',
                'instrument': '',
                'endoscope': '',
                'use_sim_time': use_sim_time,
                'rate': rate,
                'suj': 'false',
                'show_rcm': show_rcm,
            }.items(),
        ))

    actions.extend([
        Node(
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
            package='rviz2',
            executable='rviz2',
            name='rviz2_surgeon_console',
            arguments=['-d', PathJoinSubstitution([
                FindPackageShare('dvrk_model'),
                'rviz',
                'Classic',
                'surgeon_console.rviz',
            ])],
            output='log',
        ),
    ])

    return LaunchDescription(actions)
