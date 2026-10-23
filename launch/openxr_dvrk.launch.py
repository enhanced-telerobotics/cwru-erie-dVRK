"""Show SD or HD stereo video in OpenXR alongside the Classic patient cart, without teleoperation."""

from pathlib import Path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, EmitEvent, OpaqueFunction, RegisterEventHandler
from launch.event_handlers import OnProcessExit, OnProcessIO
from launch.events import Shutdown
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def launch_setup(context):
    repository_root = Path(__file__).resolve().parent.parent
    device = LaunchConfiguration("device").perform(context).lower()
    config_dir = Path(LaunchConfiguration("config_dir").perform(context)).expanduser().resolve()
    configs = {}
    for name, default in (
        ("source_config", f"stereo_source_{device}.json"),
        ("alignment_config", f"stereo_alignment_{device}.json"),
        ("display_config", f"stereo_display_openxr_{device}.json"),
    ):
        value = LaunchConfiguration(name).perform(context).strip() or default
        path = Path(value).expanduser()
        configs[name] = path if path.is_absolute() else config_dir / path
    system_config = Path(LaunchConfiguration("system_config").perform(context)).expanduser().resolve()
    missing = [str(path) for path in [system_config, *configs.values()] if not path.is_file()]
    if missing:
        raise RuntimeError("Missing configuration file(s): " + ", ".join(missing))

    stereo_source = Node(
        package="dvrk_data",
        executable="stereo_source",
        name="stereo_source",
        output="screen",
        arguments=["-c", str(configs["source_config"])],
    )
    stereo_alignment = Node(
        package="dvrk_data",
        executable="stereo_alignment",
        name="stereo_alignment",
        output="screen",
        arguments=["-c", str(configs["alignment_config"])],
    )
    display_arguments = ["-c", str(configs["display_config"])]
    if LaunchConfiguration("grid").perform(context).lower() == "true":
        display_arguments.append("--grid")
    stereo_display = Node(
        package="dvrk_console",
        executable="stereo_display",
        name="openxr_stereo_display",
        output="screen",
        arguments=display_arguments,
    )
    dvrk_system = Node(
        package="dvrk_robot",
        executable="dvrk_system",
        name="dvrk_system",
        output="screen",
        cwd=str(repository_root),
        arguments=["-j", str(system_config)],
    )
    control_panel = Node(
        package="dvrk_console",
        executable="control_panel",
        name="control_panel",
        output="screen",
    )

    started = {
        "stereo_alignment": False,
        "stereo_display": False,
        "dvrk_system": False,
    }

    def on_stereo_source_output(event):
        if started["stereo_alignment"]:
            return None
        text = event.text.decode(errors="replace")
        if "Stereo source background pipeline started" in text:
            started["stereo_alignment"] = True
            return [stereo_alignment]
        return None

    start_stereo_alignment = RegisterEventHandler(
        OnProcessIO(
            target_action=stereo_source,
            on_stdout=on_stereo_source_output,
            on_stderr=on_stereo_source_output,
        )
    )

    def on_stereo_alignment_output(event):
        if started["stereo_display"]:
            return None
        text = event.text.decode(errors="replace")
        if "Stereo alignment background pipeline started" in text:
            started["stereo_display"] = True
            return [stereo_display]
        return None

    start_stereo_display = RegisterEventHandler(
        OnProcessIO(
            target_action=stereo_alignment,
            on_stdout=on_stereo_alignment_output,
            on_stderr=on_stereo_alignment_output,
        )
    )

    def on_stereo_display_output(event):
        if started["dvrk_system"]:
            return None
        text = event.text.decode(errors="replace")
        if "Stereo display pipeline started" in text:
            started["dvrk_system"] = True
            return [dvrk_system, control_panel]
        return None

    launch_dvrk_system = RegisterEventHandler(
        OnProcessIO(
            target_action=stereo_display,
            on_stdout=on_stereo_display_output,
            on_stderr=on_stereo_display_output,
        )
    )

    stop_on_exit = [
        RegisterEventHandler(OnProcessExit(
            target_action=process,
            on_exit=[EmitEvent(event=Shutdown(reason=reason))],
        ))
        for process, reason in (
            (stereo_source, "SDI source exited"),
            (stereo_alignment, "Stereo alignment exited"),
            (stereo_display, "OpenXR video overlay exited"),
            (dvrk_system, "dVRK system exited"),
        )
    ]

    return [
        *stop_on_exit,
        # Register handlers before stereo_source can emit readiness output.
        start_stereo_alignment,
        start_stereo_display,
        launch_dvrk_system,
        stereo_source,
    ]


def generate_launch_description():
    repository_root = Path(__file__).resolve().parent.parent
    return LaunchDescription([
        DeclareLaunchArgument(
            "device", default_value="HD", choices=["SD", "HD"],
            description="Select SD (640x480) or HD (1920x1080) USB capture configs.",
        ),
        DeclareLaunchArgument(
            "grid", default_value="false", choices=["true", "false"],
            description="Show the display calibration grid in the OpenXR headset.",
        ),
        DeclareLaunchArgument(
            "system_config",
            default_value=str(repository_root / "system" / "system-OpenXR-SUJ-ECM-PSM1-PSM2.json"),
            description="OpenXR and physical Classic patient-cart system JSON.",
        ),
        DeclareLaunchArgument(
            "config_dir", default_value=str(repository_root / "sdi"),
            description="Directory containing video JSON files.",
        ),
        *[
            DeclareLaunchArgument(
                name, default_value="",
                description="Video config filename relative to config_dir, or absolute path; empty selects the device default.",
            )
            for name in ("source_config", "alignment_config", "display_config")
        ],
        OpaqueFunction(function=launch_setup),
    ])
