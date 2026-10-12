"""Teleoperate the PyBullet patient cart with OpenXR controllers and stereo video."""

from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument, EmitEvent, ExecuteProcess, RegisterEventHandler, TimerAction,
)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit, OnProcessIO
from launch.events import Shutdown
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    repository_root = Path(__file__).resolve().parent.parent
    pybullet_share = Path(get_package_share_directory("dvrk_pybullet"))
    default_config = repository_root / "sim" / "pybullet_patient_cart.yaml"
    system_config = repository_root / "system" / "system-OpenXR-pybullet-Teleop.json"
    display_config = repository_root / "sim" / "stereo_display_openxr_bullet.json"

    simulator = ExecuteProcess(
        cmd=[
            LaunchConfiguration("pybullet_python"),
            "-u",
            str(pybullet_share / "scripts" / "simulator.py"),
            "--config", LaunchConfiguration("pybullet_config"),
            "--scene", "ECM_PSM1_PSM2_PSM3.yaml",
            "--scene", LaunchConfiguration("exercise"),
            "--headless", LaunchConfiguration("headless"),
        ],
        output="screen",
    )
    dvrk_system = Node(
        package="dvrk_robot",
        executable="dvrk_system",
        name="dvrk_system",
        output="screen",
        cwd=str(repository_root),
        arguments=["-j", LaunchConfiguration("system_config")],
    )
    stereo_display = Node(
        package="dvrk_console",
        executable="stereo_display",
        name="stereo_display",
        output="screen",
        arguments=["-c", LaunchConfiguration("display_config")],
    )
    control_panel = Node(
        package="dvrk_console",
        executable="control_panel",
        name="control_panel",
        output="screen",
    )
    rqt_monitor = ExecuteProcess(
        cmd=["rqt"],
        additional_env={
            "DVRK_RQT_ARMS": "ECM,PSM1,PSM2,PSM3",
            "DVRK_RQT_CONSOLE": LaunchConfiguration("console"),
        },
        condition=IfCondition(LaunchConfiguration("rqt")),
        output="screen",
    )

    stop_with_simulator = RegisterEventHandler(
        OnProcessExit(
            target_action=simulator,
            on_exit=[EmitEvent(event=Shutdown(reason="PyBullet simulator exited"))],
        )
    )
    stop_with_system = RegisterEventHandler(
        OnProcessExit(
            target_action=dvrk_system,
            on_exit=[EmitEvent(event=Shutdown(reason="dvrk_system exited"))],
        )
    )

    started = False
    output_buffer = ""

    def on_display_output(event):
        nonlocal started, output_buffer
        if started:
            return None
        output_buffer = (output_buffer + event.text.decode(errors="replace"))[-4096:]
        if "Stereo display pipeline started" in output_buffer:
            started = True
            return [dvrk_system, control_panel, rqt_monitor]
        return None

    start_system = RegisterEventHandler(OnProcessIO(
        target_action=stereo_display,
        on_stdout=on_display_output,
        on_stderr=on_display_output,
    ))
    stop_with_display = RegisterEventHandler(OnProcessExit(
        target_action=stereo_display,
        on_exit=[EmitEvent(event=Shutdown(reason="OpenXR video overlay exited"))],
    ))

    return LaunchDescription([
        DeclareLaunchArgument(
            "system_config", default_value=str(system_config),
            description="dVRK system JSON for OpenXR controllers and simulated patient arms.",
        ),
        DeclareLaunchArgument(
            "display_config", default_value=str(display_config),
            description="OpenXR stereo overlay JSON for the PyBullet video socket.",
        ),
        DeclareLaunchArgument(
            "exercise", default_value="tray_cubes.yaml",
            description="Exercise scene YAML path or installed exercise filename.",
        ),
        DeclareLaunchArgument(
            "headless", default_value="true",
            description="Run PyBullet without its desktop viewer window.",
        ),
        DeclareLaunchArgument(
            "console", default_value="console",
            description="dVRK console ROS namespace for the optional rqt monitor.",
        ),
        DeclareLaunchArgument(
            "rqt", default_value="false",
            description="Start rqt for console and arm monitoring.",
        ),
        DeclareLaunchArgument(
            "pybullet_config", default_value=str(default_config),
            description="PyBullet runtime YAML configuration.",
        ),
        DeclareLaunchArgument(
            "pybullet_python",
            default_value="/home/erie_lab/Documents/envs/sim/bin/python",
            description="Python interpreter with PyBullet requirements installed.",
        ),
        start_system,
        stop_with_display,
        stop_with_simulator,
        stop_with_system,
        simulator,
        TimerAction(period=4.0, actions=[stereo_display]),
    ])
