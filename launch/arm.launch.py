from launch.actions import OpaqueFunction
from pathlib import Path
import os
import yaml
from ament_index_python.packages import get_package_share_directory

from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.actions import SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch.conditions import IfCondition
from launch import LaunchContext, LaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch.actions import DeclareLaunchArgument

def psm_instruments():
    yaml_file = os.path.join(
        get_package_share_directory('dvrk_model'),
        'urdf', 'common', 'instruments', 'instruments.yaml')
    with open(yaml_file, 'r') as stream:
        return yaml.safe_load(stream)['instruments']

def supported_psm_instruments_message():
    instruments = psm_instruments()
    return ', '.join(
        '{} ({})'.format(model, instruments[model]['name'])
        for model in sorted(instruments.keys()))

def generate_launch_description():
    arm = LaunchConfiguration('arm')
    generation = LaunchConfiguration('generation')
    instrument = LaunchConfiguration('instrument', default='')
    endoscope = LaunchConfiguration('endoscope', default='')
    rate = LaunchConfiguration('rate', default = 50.0)  # Hz, default is 10 so we're increasing that a bit.

    system_config = LaunchConfiguration('system_config')

    rviz_config_file = [
        PathJoinSubstitution([FindPackageShare('dvrk_model'), 'rviz', generation, '']),
        '/', arm, '.rviz',
    ]

    # Declare nodes
    dvrk_node = OpaqueFunction(function=lambda context: [
        Node(
            package = 'dvrk_robot',
            executable = 'dvrk_system',
            arguments = ['-j', system_config] + (['-P', '0'] if IfCondition(LaunchConfiguration('use_rviz')).evaluate(context) else []),
            cwd=str(Path(__file__).resolve().parent.parent),
            output = 'screen',
        )
    ])

    publisher_nodes = IncludeLaunchDescription(
        condition=IfCondition(LaunchConfiguration('use_rviz')),
        launch_description_source=PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('dvrk_model'),
                'launch',
                'arm_state_publishers.launch.py')),
        launch_arguments = {
            'arm': arm,
            'generation': generation,
            'instrument': instrument,
            'endoscope': endoscope,
            'use_sim_time': 'false',
            'rate': rate,
            'suj': 'false',
            'show_rcm': LaunchConfiguration('show_rcm')
        }.items()
    )

    rviz_node = Node(
        condition=IfCondition(LaunchConfiguration('use_rviz')),
        package = 'rviz2',
        executable = 'rviz2',
        name = 'rviz2',
        arguments = ['-d', rviz_config_file],
        output = 'log',
    )

    ld = LaunchDescription([
        SetEnvironmentVariable('RMW_FASTRTPS_USE_SHM', '0'),
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
            default_value=[str(Path(__file__).resolve().parent.parent / 'system/system-'),
                           arm, '.json'],
            description='Real-hardware dVRK system JSON file.',
        ),
        DeclareLaunchArgument('arm'),
        DeclareLaunchArgument(
            'generation',
            choices=['Classic', 'Si', 'Virtual'],
            description='dVRK system generation'
        ),
        DeclareLaunchArgument(
            'instrument',
            default_value='',
            description='PSM instrument model. Supported: {}'.format(
                supported_psm_instruments_message())),
        DeclareLaunchArgument('endoscope', default_value=''),
        DeclareLaunchArgument('rate', default_value='50.0'),
        DeclareLaunchArgument('show_rcm', default_value='true'),
        dvrk_node,
        publisher_nodes,
        rviz_node,
    ])

    return ld
