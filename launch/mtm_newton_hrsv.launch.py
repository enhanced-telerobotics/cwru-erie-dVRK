"""Run physical MTMs and pedals with the Newton virtual patient cart and HRSV."""

import os
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument, EmitEvent, ExecuteProcess, RegisterEventHandler, TimerAction,
)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    repository_root = Path(__file__).resolve().parent.parent
    newton_share = Path(get_package_share_directory("dvrk_newton"))
    default_config = repository_root / "sim" / "newton_patient_cart.yaml"
    system_config = repository_root / "system" / "system-MTML-MTMR-newton-Teleop.json"
    display_config = repository_root / "sim" / "stereo_display_hrsv_newton.json"

    simulator = ExecuteProcess(
        cmd=[
            LaunchConfiguration("newton_python"),
            str(newton_share / "scripts" / "simulator.py"),
            "--config", LaunchConfiguration("newton_config"),
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
            on_exit=[EmitEvent(event=Shutdown(reason="Newton simulator exited"))],
        )
    )
    stop_with_system = RegisterEventHandler(
        OnProcessExit(
            target_action=dvrk_system,
            on_exit=[EmitEvent(event=Shutdown(reason="dvrk_system exited"))],
        )
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            "system_config", default_value=str(system_config),
            description="dVRK system JSON for local physical MTMs and simulated patient arms.",
        ),
        DeclareLaunchArgument(
            "display_config", default_value=str(display_config),
            description="HRSV stereo display JSON for the Newton video socket.",
        ),
        DeclareLaunchArgument(
            "exercise", default_value="tray_cubes.yaml",
            description="Exercise scene YAML path or installed exercise filename.",
        ),
        DeclareLaunchArgument(
            "headless", default_value="true",
            description="Run Newton without its desktop viewer window.",
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
            "newton_config", default_value=str(default_config),
            description="Newton runtime YAML configuration.",
        ),
        DeclareLaunchArgument(
            "newton_python",
            default_value="/home/erie_lab/Documents/envs/sim/bin/python",
            description="Python interpreter with Newton requirements installed.",
        ),
        stop_with_simulator,
        stop_with_system,
        simulator,
        TimerAction(period=4.0, actions=[stereo_display]),
        control_panel,
        dvrk_system,
        rqt_monitor,
    ])
