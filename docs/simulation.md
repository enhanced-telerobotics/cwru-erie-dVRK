# Simulation teleoperation

[Back to quick start](../README.md). Run commands from the repository root
after sourcing your ROS 2 and dVRK workspace.

## MTM teleoperation with PyBullet and HRSV

Use the local physical MTML (39494), MTMR (56216), pedals, and ISI head sensor
to teleoperate PyBullet patient arms and view the simulator in the HRSV:

```bash
ros2 launch launch/mtm_pybullet_hrsv.launch.py
```

Source the workspace containing `dvrk_pybullet`, `dvrk_arms_from_ros`,
`dvrk_robot`, and `dvrk_console` first. The default `/home/erie_lab/Documents/envs/sim/bin/python` must have the
PyBullet simulator requirements installed; select another interpreter with
`pybullet_python:=/path/to/venv/bin/python3` if needed.

The launch starts one `dvrk_system`, PyBullet, the control panel, and the HRSV
display after four seconds. MTMR controls PSM1; MTML controls PSM2 or PSM3;
both MTMs provide ECM teleoperation. Power, home, and enable teleoperation
using the normal console procedure. Do not run another hardware launch alongside it.

The system JSON is `system/system-MTML-MTMR-pybullet-Teleop.json`.
Simulator settings live in `sim/pybullet_patient_cart.yaml`, and the vision JSON
is `sim/stereo_display_hrsv_bullet.json`. PyBullet supplies stereo video directly
over its simulator socket. The HRSV config scales it to 1024 × 768 per eye and
uses your configured display offset of -46 pixels.

Override `exercise`, `headless`, `pybullet_config`, `system_config`, or
`display_config` as needed; `rqt:=true` enables the optional monitor.
List all arguments with:

```bash
ros2 launch launch/mtm_pybullet_hrsv.launch.py --show-args
```

## MTM teleoperation with Newton and HRSV

The Newton launch uses the same local MTMs, pedals, ISI head sensor, teleop
mappings, and HRSV display settings as the PyBullet setup:

```bash
ros2 launch launch/mtm_newton_hrsv.launch.py
```

Source the workspace containing `dvrk_newton` and the same robot and console
packages first. The default interpreter is
`/home/erie_lab/Documents/envs/sim/bin/python`; it must have the Newton
simulator requirements installed, including Newton and Warp. Select another
interpreter with `newton_python:=/path/to/venv/bin/python3` if needed.

Configuration files are `system/system-MTML-MTMR-newton-Teleop.json`,
`sim/newton_patient_cart.yaml`, and `sim/stereo_display_hrsv_newton.json`.
The runtime config follows the IROS Newton reference and defaults to `cuda:0`.
The launch starts Newton, one `dvrk_system`, the control panel, and the HRSV
video display after four seconds. Stop the PyBullet or other hardware launch
before starting this one.

Override `newton_config`, `newton_python`, `exercise`, `headless`,
`system_config`, or `display_config` as needed; `rqt:=true` enables monitoring.

```bash
ros2 launch launch/mtm_newton_hrsv.launch.py --show-args
```

## OpenXR teleoperation with PyBullet

Connect your Quest through WiVRn, select WiVRn as the active OpenXR runtime,
and launch from a regular desktop terminal with your dVRK workspace sourced:

```bash
ros2 launch launch/openxr_pybullet.launch.py
```

This starts PyBullet, the stereo video overlay, one `dvrk_system`, and the
control panel. The overlay starts after four seconds; the robot system starts
when the overlay reports its pipeline is running. If the simulator, overlay,
or robot system exits, the remaining processes shut down.

All patient arms are simulated; this system has no hardware IO or physical
MTMs. The right Quest controller controls PSM1; the left controls either PSM2
or PSM3, initially PSM2, with scale 0.2. Quickly press and release either
thumbstick button within 0.5 seconds to switch the left controller between
PSM2 and PSM3. Two PSMs can be controlled at a time; the unselected arm holds
its position. Push a controller's thumbstick up to release its PSM clutch.
Hold both thumbsticks down to control the ECM with both controllers; release
them to leave camera mode. Power, home, and enable teleoperation for the
simulated arms using the control panel.

The system config is `system/system-OpenXR-pybullet-Teleop.json`. Video configs
are `sim/sawOpenXR-pybullet-unixfd.json` and
`sim/stereo_display_openxr_bullet.json`; simulator settings reuse
`sim/pybullet_patient_cart.yaml`. The scene includes ECM and all three PSMs.

The default interpreter is `/home/erie_lab/Documents/envs/sim/bin/python`.
Override `pybullet_python`, `pybullet_config`, `exercise`, `headless`,
`system_config`, or `display_config` as needed; `rqt:=true` enables monitoring.

```bash
ros2 launch launch/openxr_pybullet.launch.py --show-args
```
