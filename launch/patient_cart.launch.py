from launch.actions import OpaqueFunction
from pathlib import Path
import os
from ament_index_python.packages import get_package_share_directory

from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from launch.conditions import IfCondition
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
    system_config = LaunchConfiguration('system_config')
    use_sim_time = False
    show_rcm = LaunchConfiguration('show_rcm', default = 'true')
    rate = LaunchConfiguration('rate', default = 50.0)  # Hz, default is 10 so we're increasing that a bit.  Funny enough joint and robot state publishers don't have the same name for that parameter :-(

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
            'generation',
            default_value='Si',
            choices=['Classic', 'Si', 'Virtual'],
            description='dVRK system generation'
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
        DeclareLaunchArgument('show_rcm', default_value='true'),
        DeclareLaunchArgument('rate', default_value='50.0'),
    ])


    # dVRK system
    real_dvrk_node = OpaqueFunction(function=lambda context: [
        Node(
            package = 'dvrk_robot',
            executable = 'dvrk_system',
            arguments = ['-j', system_config] + (
                ['-P', '0']
                if IfCondition(LaunchConfiguration('use_rviz')).evaluate(context)
                else []
            ),
            cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)),
            output = 'screen',
        )
    ])
    ld.add_action(real_dvrk_node)


    # SUJ
    model = [
        PathJoinSubstitution([FindPackageShare('dvrk_model'),
                              'urdf', generation, ''])
        , '/SUJ.urdf.xacro'
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
        package = 'joint_state_publisher',
        namespace = 'SUJ',
        executable = 'joint_state_publisher',
        name = 'SUJ_joint_state_publisher',
        condition = IfCondition(PythonExpression(["'", LaunchConfiguration('use_rviz'), "' == 'true' and '", generation, "' != 'Virtual'"])),
        parameters = [{'use_sim_time': use_sim_time,
                       'source_list': ['/SUJ/PSM1/measured_js',
                                       '/SUJ/PSM2/measured_js',
                                       '/SUJ/ECM/measured_js'],
                       'rate': rate}],
        output = 'both',
    )
    robot_state_publisher_node = Node(
        package = 'robot_state_publisher',
        namespace = 'SUJ',
        executable = 'robot_state_publisher',
        name = 'SUJ_robot_state_publisher',
        condition = IfCondition(PythonExpression(["'", LaunchConfiguration('use_rviz'), "' == 'true' and '", generation, "' != 'Virtual'"])),
        parameters = [{'use_sim_time': use_sim_time,
                       'robot_description': description,
                       'publish_frequency': rate}],
        output = 'both',
    )
    ld.add_action(joint_state_publisher_node)
    ld.add_action(robot_state_publisher_node)


    # Arm joint/robot state publishers
    for arm in ['ECM', 'PSM1', 'PSM2']:
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
                'use_sim_time': 'false',
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
        condition=IfCondition(LaunchConfiguration('use_rviz')),
        package = 'rviz2',
        executable = 'rviz2',
        name = 'rviz2_patient_cart',
        arguments = ['-d', rviz_config_file],
        output = 'both',
    )
    ld.add_action(rviz_node)

    return ld
