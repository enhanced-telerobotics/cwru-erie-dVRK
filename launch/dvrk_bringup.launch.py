"""Bring up a real dVRK arm with optional RViz visualization."""

from pathlib import Path
import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, TextSubstitution


def generate_launch_description():
    arm = LaunchConfiguration('arm')
    generation = LaunchConfiguration('generation')
    instrument = LaunchConfiguration('instrument')
    endoscope = LaunchConfiguration('endoscope')
    system_config = LaunchConfiguration('system_config')
    rate = LaunchConfiguration('rate')
    show_rcm = LaunchConfiguration('show_rcm')

    repository_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir)
    )


    # The local arm launch owns the robot, panels, and optional visualization.
    model_and_rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                str(Path(__file__).resolve().parent),
                'arm.launch.py',
            )
        ),
        launch_arguments={
            'arm': arm,
            'system_config': system_config,
            'generation': generation,
            'instrument': instrument,
            'endoscope': endoscope,
            'rate': rate,
            'show_rcm': show_rcm,
            'use_rviz': LaunchConfiguration('use_rviz'),
            'panel': LaunchConfiguration('panel'),
        }.items(),
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_rviz', default_value='false', choices=['true', 'false'],
            description='Start RViz and model TF publishers instead of the robot TF tree.',
        ),
        DeclareLaunchArgument(
            'panel', default_value='none',
            choices=['none', 'screen', 'web', 'both'],
            description='Control panel: none, desktop screen, browser web, or both.',
        ),
        DeclareLaunchArgument(
            'arm',
            default_value='PSM1',
            description='dVRK arm name',
        ),
        DeclareLaunchArgument(
            'generation',
            default_value='Classic',
            choices=['Classic', 'Si', 'Virtual'],
            description='dVRK system generation',
        ),
        DeclareLaunchArgument(
            'system_config',
            default_value=[
                TextSubstitution(text=repository_root + '/system/system-'),
                arm,
                TextSubstitution(text='.json'),
            ],
            description='dvrk_system JSON file for real hardware',
        ),
        DeclareLaunchArgument(
            'instrument',
            default_value='',
            description='PSM instrument model; empty uses the generation default',
        ),
        DeclareLaunchArgument('endoscope', default_value=''),
        DeclareLaunchArgument('rate', default_value='50.0'),
        DeclareLaunchArgument('show_rcm', default_value='true'),
        model_and_rviz,
    ])
