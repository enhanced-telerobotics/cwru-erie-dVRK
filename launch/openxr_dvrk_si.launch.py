"""Run physical PSM1/PSM2 from sawOpenXR with SDI endoscope stereo video."""

from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from pathlib import Path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, EmitEvent, RegisterEventHandler
from launch.event_handlers import OnProcessExit, OnProcessIO
from launch.events import Shutdown
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    repository_root = Path(__file__).resolve().parent.parent
    system_config = repository_root / "system" / "system-OpenXR-SUJ-ECM-PSM1-PSM2-Teleop.json"
    source_config = repository_root / "sdi" / "stereo_source_hd.json"
    alignment_config = repository_root / "sdi" / "stereo_alignment_hd.json"
    display_config = repository_root / "sdi" / "stereo_display_openxr_hd.json"

    stereo_source = Node(
        package="dvrk_data",
        executable="stereo_source",
        name="stereo_source",
        output="screen",
        arguments=["-c", LaunchConfiguration("source_config")],
    )
    stereo_alignment = Node(
        package="dvrk_data",
        executable="stereo_alignment",
        name="stereo_alignment",
        output="screen",
        arguments=["-c", LaunchConfiguration("alignment_config")],
    )
    stereo_display = Node(
        package="dvrk_console",
        executable="stereo_display",
        name="openxr_stereo_display",
        output="screen",
        arguments=["-c", LaunchConfiguration("display_config")],
    )
    dvrk_system = Node(
        package="dvrk_robot",
        executable="dvrk_system",
        name="dvrk_system",
        output="screen",
        cwd=str(repository_root),
        arguments=["-j", LaunchConfiguration("system_config")],
    )
    control_panel = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(
            Path(__file__).resolve().parent / 'control_panel.launch.py'
        )),
        launch_arguments={'panel': LaunchConfiguration('panel')}.items(),
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

    return LaunchDescription([
        DeclareLaunchArgument(
            'panel', default_value='none',
            choices=['none', 'screen', 'web', 'both'],
            description='Control panel: none, desktop screen, browser web, or both.',
        ),
        DeclareLaunchArgument("system_config", default_value=str(system_config),
                              description="Local OpenXR and physical patient-cart system JSON."),
        DeclareLaunchArgument("source_config", default_value=str(source_config),
                              description="SDI stereo capture JSON."),
        DeclareLaunchArgument("alignment_config", default_value=str(alignment_config),
                              description="SDI stereo alignment JSON."),
        DeclareLaunchArgument("display_config", default_value=str(display_config),
                              description="OpenXR stereo overlay JSON."),
        *stop_on_exit,
        # Register handlers before stereo_source can emit readiness output.
        start_stereo_alignment,
        start_stereo_display,
        launch_dvrk_system,
        stereo_source,
    ])
