"""Bring up one dVRK arm and its RViz model.

Real hardware is the default. In real mode this launch file starts dvrk_system
with a local system/system-<arm>.json file. In simulated mode the included upstream
dvrk_model launch file starts the appropriate kinematic simulation instead.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, TextSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    arm = LaunchConfiguration('arm')
    generation = LaunchConfiguration('generation')
    instrument = LaunchConfiguration('instrument')
    endoscope = LaunchConfiguration('endoscope')
    simulated = LaunchConfiguration('simulated')
    system_config = LaunchConfiguration('system_config')
    use_sim_time = LaunchConfiguration('use_sim_time')
    rate = LaunchConfiguration('rate')
    show_rcm = LaunchConfiguration('show_rcm')

    repository_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir)
    )

    # For a physical arm. The included arm launch starts a simulated
    # dvrk_system itself when simulated:=true.
    real_dvrk_system = Node(
        package='dvrk_robot',
        executable='dvrk_system',
        condition=UnlessCondition(simulated),
        arguments=['-j', system_config],
        output='screen',
    )

    # Use the supported model launch for joint-state aggregation, TF, and RViz.
    model_and_rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('dvrk_model'),
                'launch',
                'arm.launch.py',
            )
        ),
        launch_arguments={
            'arm': arm,
            'generation': generation,
            'instrument': instrument,
            'endoscope': endoscope,
            'simulated': simulated,
            'use_sim_time': use_sim_time,
            'rate': rate,
            'show_rcm': show_rcm,
        }.items(),
    )

    return LaunchDescription([
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
            'simulated',
            default_value='false',
            description='Use kinematic simulation instead of real hardware',
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
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('rate', default_value='50.0'),
        DeclareLaunchArgument('show_rcm', default_value='true'),
        real_dvrk_system,
        model_and_rviz,
    ])
