"""Start the HRSV video pipeline using this repository's SDI configs."""

import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction, TimerAction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


DEFAULT_SOURCE_CONFIG = "stereo_source_hd.json"
DEFAULT_ALIGNMENT_CONFIG = "stereo_alignment_hd.json"
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
    alignment_config_path = resolve_config_path(
        base_dir,
        LaunchConfiguration("alignment_config").perform(context),
        DEFAULT_ALIGNMENT_CONFIG,
    )
    display_config_path = resolve_config_path(
        base_dir,
        LaunchConfiguration("display_config").perform(context),
        DEFAULT_DISPLAY_CONFIG,
    )

    missing = [
        path
        for path in (source_config_path, alignment_config_path, display_config_path)
        if not os.path.exists(path)
    ]
    if missing:
        raise RuntimeError("Missing configuration file(s): " + ", ".join(missing))

    source_node = Node(
        package="dvrk_data",
        executable="stereo_source",
        name="stereo_source",
        output="screen",
        arguments=["-c", source_config_path],
    )

    alignment_node = Node(
        package="dvrk_data",
        executable="stereo_alignment",
        name="stereo_alignment",
        output="screen",
        arguments=["-c", alignment_config_path],
    )

    display_node = Node(
        package="dvrk_console",
        executable="stereo_display",
        name="stereo_display",
        output="screen",
        # Snap VS Code exports GTK module paths linked against Snap's libc.
        # Use host GTK modules while retaining the ROS workspace library paths.
        additional_env={
            key: ""
            for key in (
                "GTK_PATH", "GTK_EXE_PREFIX", "GTK_MODULES",
                "GTK_IM_MODULE_FILE", "GDK_PIXBUF_MODULE_FILE",
                "GDK_PIXBUF_MODULEDIR", "GIO_MODULE_DIR",
            )
            if "snap/" in os.environ.get(key, "")
            or "/snap/" in os.environ.get("GTK_PATH", "")
        },
        arguments=["-c", display_config_path],
    )

    return [
        source_node,
        TimerAction(period=2.0, actions=[alignment_node]),
        TimerAction(period=4.0, actions=[display_node]),
        # gscam_socket checks for an active source socket before launching.
        TimerAction(
            period=4.0,
            condition=IfCondition(LaunchConfiguration("use_ros")),
            actions=[
                ExecuteProcess(
                    cmd=["ros2", "run", "dvrk_data", "gscam_socket",
                         "@dvrk:stereo_source:" + eye],
                    output="screen",
                )
                for eye in ("left", "right")
            ],
        ),
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            "use_ros",
            default_value="false",
            choices=["true", "false"],
            description="Publish both raw camera streams to ROS 2 using gscam_socket after four seconds.",
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
            "alignment_config",
            default_value=DEFAULT_ALIGNMENT_CONFIG,
            description="dvrk_data stereo_alignment config filename or absolute path.",
        ),
        DeclareLaunchArgument(
            "display_config",
            default_value=DEFAULT_DISPLAY_CONFIG,
            description="dvrk_console stereo_display config filename or absolute path.",
        ),
        OpaqueFunction(function=launch_setup),
    ])
