import os
from ament_index_python.packages import get_package_share_directory

from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from launch.conditions import IfCondition
from launch.conditions import UnlessCondition
from launch import LaunchContext, LaunchDescription, Substitution
from typing import Text

from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
    PythonExpression,
    TextSubstitution,
)

def generate_launch_description():
    generation = LaunchConfiguration('generation')
    simulated = LaunchConfiguration('simulated', default = 'false')
    system_config = LaunchConfiguration('system_config')
    use_sim_time = LaunchConfiguration('use_sim_time', default = 'false')
    show_rcm = LaunchConfiguration('show_rcm', default = 'true')
    rate = LaunchConfiguration('rate', default = 50.0)  # Hz, default is 10 so we're increasing that a bit.  Funny enough joint and robot state publishers don't have the same name for that parameter :-(
    virtual_generation = PythonExpression(["'", generation, "' == 'Virtual'"])

    ld = LaunchDescription([
        DeclareLaunchArgument(
            'generation',
            default_value='Classic',
            choices=['Classic', 'Si', 'Virtual'],
            description='dVRK system generation'
        ),
        DeclareLaunchArgument(
            'simulated',
            default_value='false',
            description='Use kinematic simulation instead of real hardware'
        ),
        DeclareLaunchArgument(
            'system_config',
            default_value=TextSubstitution(text=os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    os.pardir,
                    'system',
                    'system-SUJ-ECM-PSM1-PSM2.json'
                )
            )),
            description='dvrk_system JSON file for the real patient cart'
        ),
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('show_rcm', default_value='true'),
        DeclareLaunchArgument('rate', default_value='50.0'),
    ])


    # dVRK system
    system_json = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'system', 'system-SUJ-ECM-PSM1-PSM2-simulated.json'))
    simulated_dvrk_node = Node(
        package = 'dvrk_robot',
        executable = 'dvrk_system',
        condition = IfCondition(simulated),
        arguments = ['-j', system_json],
        output = 'both',
    )
    real_dvrk_node = Node(
        package = 'dvrk_robot',
        executable = 'dvrk_system',
        condition = UnlessCondition(simulated),
        arguments = ['-j', system_config],
        output = 'screen',
    )
    ld.add_action(simulated_dvrk_node)
    ld.add_action(real_dvrk_node)


    # Fixed base calibration replaces SUJ read-board joint states in real mode.
    ld.add_action(IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(os.path.dirname(__file__),
                                                   'fixed_base_frames.launch.py'))))

    # Arm joint/robot state publishers
    for arm in ['ECM', 'PSM1', 'PSM2']:
        publisher_nodes = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    get_package_share_directory('dvrk_model'),
                    'launch',
                    'arm_state_publishers.launch.py')),
            launch_arguments = {
                'arm': arm,
                'generation': generation,
                'use_sim_time': use_sim_time,
                'rate': rate,
                'suj': 'true',
                'show_rcm': show_rcm
            }.items()
        )
        ld.add_action(publisher_nodes)

    # RViz
    rviz_config_file = [
        PathJoinSubstitution([FindPackageShare('dvrk_model'),
                              'rviz', generation, '']),
        '/patient_cart.rviz'
    ]
    rviz_node = Node(
        package = 'rviz2',
        executable = 'rviz2',
        name = 'rviz2_patient_cart',
        arguments = ['-d', rviz_config_file],
        output = 'both',
    )
    ld.add_action(rviz_node)

    return ld
