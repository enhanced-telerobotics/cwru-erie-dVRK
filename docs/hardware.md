# Classic hardware

[Back to quick start](../README.md).

## Start

Source the built 2.5 workspace in a fresh terminal, then:

```bash
source /home/erie_lab/dvrk_2.5.0_ws/install/setup.bash
cd ~/cwru-erie-dVRK
ros2 run dvrk_robot dvrk_system -j system/system-MTMR.json
# or the complete system:
ros2 run dvrk_robot dvrk_system -j system/system-SUJ-ECM-MTML-PSM2-MTMR-PSM1-Teleop.json
```

Launch interfaces matching the Si branch:

```bash
ros2 launch launch/dvrk_bringup.launch.py arm:=PSM1
ros2 launch launch/patient_cart.launch.py
ros2 launch launch/surgeon_console.launch.py
ros2 launch launch/dvrk_full.launch.py
```

Run one robot launch at a time. Generation defaults to Classic. All hardware
launches use real hardware and wall-clock time; simulation switches are removed.

## Panels and RViz

Robot launches accept `panel:=none|screen|web|both`, default `none`.
`screen` starts `dvrk_console/control_panel`; `web` starts
`dvrk_utils/control_panel` with `/home/erie_lab/Documents/envs/torch_stable/bin/python`.
Source the workspace containing `dvrk_utils` before selecting `web` or `both`.

```bash
ros2 launch launch/dvrk_full.launch.py panel:=web
ros2 launch launch/dvrk_bringup.launch.py arm:=PSM1 use_rviz:=true
```

`use_rviz` defaults to `false` in `dvrk_full`, `patient_cart`,
`surgeon_console`, `dvrk_bringup`, and `arm`. With it disabled, only the robot
and explicitly selected panels run, using the robot's default TF publishing.
With it enabled, model publishers and RViz run and robot TF publishing is disabled.
Classic visualization uses the calibrated fixed bases instead of moving SUJ joints.
