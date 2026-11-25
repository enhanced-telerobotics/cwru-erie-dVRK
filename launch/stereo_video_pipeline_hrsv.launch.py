"""Start the HRSV video pipeline using this repository's SDI configs."""

import json
import os

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    GroupAction,
    IncludeLaunchDescription,
    OpaqueFunction,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node, SetParameter
from launch_ros.substitutions import FindPackageShare


DEFAULT_SOURCE_CONFIG = "stereo_source_hd.json"
DEFAULT_RECTIFY_CONFIG = "stereo_rectify_hd.json"
DEFAULT_DISPLAY_CONFIG = "stereo_display_hrsv_hd.json"
DEFAULT_CONFIG_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, "sdi")
)


def resolve_config_path(base_dir, value, default_name):
    value = value.strip() or default_name
    value = os.path.expanduser(value)
    if os.path.isabs(value):
        return value
    return os.path.join(base_dir, value)


def launch_ros_bridges(_context):
    from dvrk_data import dvrk_gst_socket

    gscam_launch = PathJoinSubstitution([
        FindPackageShare("dvrk_data"), "launch", "gscam.launch.py",
    ])
    bridges = []
    for eye in ("left", "right"):
        socket = dvrk_gst_socket.make("stereo_source", eye)
        if not dvrk_gst_socket.check_socket(socket):
            continue

        bridges.append(GroupAction(actions=[
            SetParameter(name="camera.image_raw.ffmpeg.encoder", value="h264_nvenc"),
            SetParameter(name="camera.image_raw.ffmpeg.bit_rate", value=8_000_000),
            SetParameter(name="camera.image_raw.ffmpeg.max_b_frames", value=0),
            SetParameter(
                name="camera.image_raw.ffmpeg.encoder_av_options",
                value="preset:p1,tune:ull,zerolatency:1,rc-lookahead:0,delay:0",
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(gscam_launch),
                launch_arguments={"socket": socket}.items(),
            ),
        ]))
    return bridges


def launch_setup(context, *args, **kwargs):
    system = LaunchConfiguration("system").perform(context).strip()
    config_parent = LaunchConfiguration("config_parent").perform(context).strip()
    config_dir = LaunchConfiguration("config_dir").perform(context).strip()

    if system:
        if not config_parent:
            raise RuntimeError(
                'Launch argument "config_parent" is required when "system" is set.'
            )
        base_dir = os.path.join(os.path.expanduser(config_parent), system)
    else:
        base_dir = os.path.expanduser(config_dir) if config_dir else os.getcwd()

    base_dir = os.path.abspath(base_dir)
    source_config_path = resolve_config_path(
        base_dir,
        LaunchConfiguration("source_config").perform(context),
        DEFAULT_SOURCE_CONFIG,
    )
    rectify_config_path = os.path.join(base_dir, DEFAULT_RECTIFY_CONFIG)
    display_config_path = resolve_config_path(
        base_dir,
        LaunchConfiguration("display_config").perform(context),
        DEFAULT_DISPLAY_CONFIG,
    )

    missing = [
        path
        for path in (source_config_path, rectify_config_path, display_config_path)
        if not os.path.exists(path)
    ]
    if missing:
        raise RuntimeError("Missing configuration file(s): " + ", ".join(missing))

    with open(source_config_path, encoding="utf-8") as config:
        source_socket = json.load(config).get("gst_output", "@dvrk:stereo_source:stereo")

    source_node = Node(
        package="dvrk_data",
        executable="stereo_source",
        name="stereo_source",
        output="screen",
        arguments=["-c", source_config_path, "--stereo-output"],
    )

    rectify_node = Node(
        package="dvrk_data",
        executable="stereo_rectify",
        name="stereo_rectify",
        output="screen",
        arguments=["-c", rectify_config_path, "-i", source_socket],
    )

    display_node = Node(
        package="dvrk_console",
        executable="stereo_display",
        name="stereo_display",
        output="screen",
        arguments=["-c", display_config_path],
    )

    return [
        source_node,
        TimerAction(period=2.0, actions=[rectify_node]),
        TimerAction(period=4.0, actions=[display_node]),
        TimerAction(
            period=4.0,
            condition=IfCondition(LaunchConfiguration("use_ros")),
            actions=[OpaqueFunction(function=launch_ros_bridges)],
        ),
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            "use_ros",
            default_value="false",
            choices=["true", "false"],
            description="Start both gscam camera publishers after four seconds.",
        ),
        DeclareLaunchArgument(
            "config_dir",
            default_value=DEFAULT_CONFIG_DIR,
            description="Directory containing video JSON files; defaults to this repository's sdi/. Ignored when system is set.",
        ),
        DeclareLaunchArgument(
            "system",
            default_value="",
            description="Optional video configuration subdirectory under config_parent (not a robot system JSON). Overrides config_dir when set.",
        ),
        DeclareLaunchArgument(
            "config_parent",
            default_value="",
            description="Parent directory containing system config directories. Required when system is set.",
        ),
        DeclareLaunchArgument(
            "source_config",
            default_value=DEFAULT_SOURCE_CONFIG,
            description="dvrk_data stereo_source config filename or absolute path.",
        ),
        DeclareLaunchArgument(
            "display_config",
            default_value=DEFAULT_DISPLAY_CONFIG,
            description="dvrk_console stereo_display config filename or absolute path.",
        ),
        OpaqueFunction(function=launch_setup),
    ])
