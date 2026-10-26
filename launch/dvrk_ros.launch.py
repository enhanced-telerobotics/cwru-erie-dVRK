"""Local MTM teleoperation of remote ROS arms, with remote stereo on HRSV."""

import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            "system_config",
            default_value=os.path.join(
                REPO_ROOT, "system",
                "system-MTML-MTMR-ECM-PSM1-PSM2-from-ROS-Teleop.json",
            ),
            description="Local MTM hardware and remote ECM/PSM system JSON.",
        ),
        DeclareLaunchArgument(
            "left_image_topic",
            default_value="/stereo_source/left/camera/image_raw",
            description="Left base image topic (without the transport suffix).",
        ),
        DeclareLaunchArgument(
            "right_image_topic",
            default_value="/stereo_source/right/camera/image_raw",
            description="Right base image topic (without the transport suffix).",
        ),
        DeclareLaunchArgument(
            "image_transport", default_value="compressed",
            description="Image transport used by the remote stereo publisher.",
        ),
        DeclareLaunchArgument(
            "profile", default_value="false", choices=["true", "false"],
            description="Log HRSV display latency and rendering timing.",
        ),
        DeclareLaunchArgument(
            "sync_queue_size", default_value="10",
            description="ApproximateTime stereo synchronization queue depth.",
        ),
        DeclareLaunchArgument(
            "sync_inter_message_lower_bound_ms", default_value="15.0",
            description="Minimum frame interval; 15 ms matches show_hrsv's 60 Hz setup.",
        ),
        Node(
            package="dvrk_robot",
            executable="dvrk_system",
            arguments=["-j", LaunchConfiguration("system_config")],
            cwd=REPO_ROOT,
            output="screen",
        ),
        Node(
            package="dvrk_magewell",
            executable="display_video",
            name="display_video",
            output="screen",
            # HD HRSV geometry from dvrk_magewell/show_hrsv.launch.py.
            arguments=[
                "-h", "768", "-w", "1024",
                "--left-offset", "5120", "--right-offset", "6144",
                "--ratio", "4:3", "--method", "crop",
            ],
            parameters=[{
                "use_sim_time": False,
                "image_transport": LaunchConfiguration("image_transport"),
                "profile": ParameterValue(LaunchConfiguration("profile"), value_type=bool),
                "sync_queue_size": ParameterValue(
                    LaunchConfiguration("sync_queue_size"), value_type=int,
                ),
                "sync_inter_message_lower_bound_ms": ParameterValue(
                    LaunchConfiguration("sync_inter_message_lower_bound_ms"),
                    value_type=float,
                ),
            }],
            remappings=[
                ("davinci_endo/left/image_raw", LaunchConfiguration("left_image_topic")),
                ("davinci_endo/right/image_raw", LaunchConfiguration("right_image_topic")),
            ],
        ),
    ])
