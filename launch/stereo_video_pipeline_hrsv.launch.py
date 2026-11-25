"""Start the HRSV video pipeline using this repository's SDI configs."""

import json
import os
import re

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    GroupAction,
    IncludeLaunchDescription,
    OpaqueFunction,
    RegisterEventHandler,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessStart
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.logging import get_logger
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node, SetParameter
from launch_ros.substitutions import FindPackageShare


DEFAULT_SOURCE_CONFIG = "stereo_source_hd.json"
DEFAULT_RECTIFY_CONFIG = "stereo_rectify_hd.json"
DEFAULT_DISPLAY_CONFIG = "stereo_display_hrsv_hd.json"
DEFAULT_CONFIG_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, "sdi")
)
SOCKET_POLL_PERIOD = 0.25
SOCKET_WAIT_ATTEMPTS = 60


def resolve_config_path(base_dir, value, default_name):
    value = value.strip() or default_name
    value = os.path.expanduser(value)
    if os.path.isabs(value):
        return value
    return os.path.join(base_dir, value)


def display_input_socket(gst_input):
    if gst_input.startswith("@dvrk:"):
        return gst_input

    source = gst_input.partition("!")[0]
    if re.match(r"^\s*unixfdsrc\s", source) and re.search(
        r"""\bsocket-type\s*=\s*(?:abstract|"abstract"|'abstract')(?:\s|$)""", source
    ):
        path = re.search(r"""\bsocket-path\s*=\s*['"]?(dvrk:[^\s'"]+)""", source)
        if path:
            return "@" + path.group(1)
    return ""


def wait_for_sockets(_context, consumers, retries=SOCKET_WAIT_ATTEMPTS):
    from dvrk_data import dvrk_gst_socket

    actions = []
    pending = {}
    available = set(dvrk_gst_socket.list_sockets())
    for socket, on_ready in consumers.items():
        if socket in available:
            actions.extend(on_ready)
        else:
            pending[socket] = on_ready

    if pending and retries:
        actions.append(TimerAction(period=SOCKET_POLL_PERIOD, actions=[
            OpaqueFunction(function=wait_for_sockets, args=[pending, retries - 1]),
        ]))
    elif pending:
        get_logger(__name__).error("Timed out waiting for image sockets: " + ", ".join(pending))
    return actions


def ros_bridge(socket):
    gscam_launch = PathJoinSubstitution([
        FindPackageShare("dvrk_data"), "launch", "gscam.launch.py",
    ])
    return GroupAction(actions=[
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
    ])


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
        source_config = json.load(config)
    source_socket = source_config.get("gst_output", "@dvrk:stereo_source:stereo")
    with open(display_config_path, encoding="utf-8") as config:
        display_config = json.load(config)
    display_socket = display_input_socket(display_config.get("gst_input", ""))

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

    source_consumers = {}
    rectify_consumers = {}
    display_consumers = {}
    after_rectify_start = []
    if display_socket:
        rectify_consumers[display_socket] = [display_node]
    else:
        after_rectify_start.append(display_node)

    if IfCondition(LaunchConfiguration("use_ros")).evaluate(context):
        with open(rectify_config_path, encoding="utf-8") as config:
            rectify_socket = json.load(config).get("gst_output", "@dvrk:stereo_rectify:stereo")
        overlay_socket = display_config.get("gst_output", "@dvrk:stereo_display:overlay")

        camera = source_config.get("camera", {})
        source_sockets = (
            camera.get("left", {}).get("gst_output"),
            camera.get("right", {}).get("gst_output"),
            source_socket,
        )
        for socket in dict.fromkeys(filter(None, source_sockets)):
            source_consumers[socket] = [ros_bridge(socket)]
        if rectify_socket:
            rectify_consumers.setdefault(rectify_socket, []).insert(0, ros_bridge(rectify_socket))
        if overlay_socket:
            display_consumers[overlay_socket] = [ros_bridge(overlay_socket)]

    source_consumers.setdefault(source_socket, []).append(rectify_node)
    handlers = []
    for node, consumers, on_start in (
        (source_node, source_consumers, []),
        (rectify_node, rectify_consumers, after_rectify_start),
        (display_node, display_consumers, []),
    ):
        if consumers:
            on_start.append(OpaqueFunction(function=wait_for_sockets, args=[consumers]))
        if on_start:
            handlers.append(RegisterEventHandler(OnProcessStart(target_action=node, on_start=on_start)))
    return [*handlers, source_node]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            "use_ros",
            default_value="false",
            choices=["true", "false"],
            description="Publish the configured source, rectified, and overlaid image sockets to ROS.",
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
