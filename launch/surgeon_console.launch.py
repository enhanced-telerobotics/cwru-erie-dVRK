import os

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
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
    simulated = LaunchConfiguration('simulated', default = 'false')
    system_config = LaunchConfiguration('system_config')
    use_sim_time = LaunchConfiguration('use_sim_time', default = 'false')
    rate = LaunchConfiguration('rate', default = 50.0)  # Hz, default is 10 so we're increasing that a bit.  Funny enough joint and robot state publishers don't have the same name for that parameter :-(

    repository_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir)
    )

    ld = LaunchDescription([
        DeclareLaunchArgument(
            'simulated',
            default_value='false',
            description='Use kinematic simulation instead of real hardware'
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
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('rate', default_value='50.0'),
    ])

    # dVRK system
    system_json = [
        PathJoinSubstitution([FindPackageShare('dvrk_config'),
                              '/system/system-surgeon-console-simulated.json'])
    ]
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
        package = 'rviz2',
        executable = 'rviz2',
        name = 'rviz2_surgeon_console',
        arguments = ['-d', rviz_config_file],
        output = 'both',
    )
    ld.add_action(rviz_node)

    return ld
