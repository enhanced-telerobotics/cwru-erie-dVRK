# CWRU ERIE dVRK Launch Files

This repository provides ROS 2 launch files for visualizing and operating either
one dVRK arm or the complete patient cart. Real-hardware mode is the default.
The launch files start `dvrk_system`, the required state publishers, TF, and
RViz, so a separate `dvrk_system` command is not needed.

## Configuration layout

- `arm/`: arm configurations, MTM gravity compensation, and the local SUJ kinematic copy.
- `io/`: robot, gripper, and Si SUJ IO configurations and potentiometer lookup tables.
- `system/`: system configurations with explicit relative paths to arm and IO files.
- `cal/`: calibration source files.

Si SUJ system configurations include `io/` in `settings.path` because dVRK
locates SUJ IO files by name. The hardware launch files set the working directory
to this repository; run direct `dvrk_system` commands from here as well.
Potentiometer lookup-table paths use the `io/` prefix because the IO loader
resolves them from the working directory.
The SUJ arm configurations continue to use the upstream `kinematic/suj-si.json`.

## Prerequisites

The examples assume ROS 2 Humble and the dVRK 2.5.0 workspace are installed at
the paths used on the ERIE computer.

In every new terminal, run:

```bash
cd /home/erie_lab/cwru-erie-dVRK
```

Before using real hardware, confirm that the FireWire/UDP connection, emergency
stop, instrument installation, and workspace around the robot are safe. Power
and home the arms using the normal dVRK console procedure after `dvrk_system`
starts.

Do not start another `dvrk_system` process while one of these launch files is
running. Two processes must not attempt to access the same hardware.

## Full dVRK system

Use `launch/dvrk_full.launch.py` to start the complete real system for
teleoperation:

- SUJ, ECM, PSM1, and PSM2
- MTML and MTMR
- One `dvrk_system` process
- Patient-cart RViz window
- Surgeon-console RViz window

Run:

```bash
ros2 launch launch/dvrk_full.launch.py
```

The default hardware configuration is:

```text
system/system-SUJ-ECM-MTML-PSM2-MTMR-PSM1-Teleop.json
```

To override it:

```bash
ros2 launch launch/dvrk_full.launch.py \
  system_config:=/absolute/path/to/system.json
```

This launch is intended for the real combined system and does not provide a
simulation mode. Do not run the patient-cart, surgeon-console, or individual-arm
hardware launch at the same time, because each would start another
`dvrk_system` process for the same hardware.

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

## HRSV stereo video

Start the SDI source, stereo alignment, and separate HRSV eye windows with:

```bash
ros2 launch launch/stereo_video_pipeline_hrsv.launch.py
```

The default configuration directory is this repository's `sdi/`, resolved from
the launch file location. The source starts immediately, alignment after two
seconds, and display after four seconds. This launch starts video processes;
run the full dVRK system separately for robot operation and HUD status.

| Argument | Default | Purpose |
|---|---|---|
| `use_ros` | `false` | Start left and right `gscam_socket` raw image publishers after four seconds |
| `config_dir` | This repository's `sdi/` | Base directory for video JSON files when `system` is empty |
| `system` | Empty | Optional subdirectory name under `config_parent`; when set, overrides `config_dir` |
| `config_parent` | Empty | Parent directory for `system`; required when `system` is set |
| `source_config` | `stereo_source_hd.json` | Capture configuration; relative to the base directory, or an absolute path |
| `alignment_config` | `stereo_alignment_hd.json` | Camera alignment configuration; relative to the base directory, or an absolute path |
| `display_config` | `stereo_display_hrsv_hd.json` | HRSV rendering configuration; relative to the base directory, or an absolute path |

Here, `system` means a video configuration directory, not a robot system JSON.
The robot configuration belongs to `dvrk_full.launch.py`'s `system_config` argument.
An absolute configuration filename overrides the base directory for that file.

To also publish the raw left and right camera images to ROS 2:

```bash
ros2 launch launch/stereo_video_pipeline_hrsv.launch.py use_ros:=true
```

The bridges consume `@dvrk:stereo_source:left` and
`@dvrk:stereo_source:right`. The source sockets must be active when the bridges
start; the four-second delay is not a readiness check.

To select another video directory:

```bash
ros2 launch launch/stereo_video_pipeline_hrsv.launch.py config_dir:=/path/to/video
```

To inspect the arguments without starting the pipeline:

```bash
ros2 launch launch/stereo_video_pipeline_hrsv.launch.py --show-args
```

## Patient-cart bringup

Use `launch/patient_cart.launch.py` for the complete local patient-cart setup:

- SUJ
- ECM
- PSM1
- PSM2
- No PSM3 arm

The default real-hardware configuration is
`system/system-SUJ-ECM-PSM1-PSM2.json`.

```bash
ros2 launch launch/patient_cart.launch.py
```

The launch file starts one `dvrk_system` process for the entire cart, aggregates
the SUJ joint states, starts state publishers for ECM, PSM1, and PSM2, and opens
the patient-cart RViz configuration.

An explicit invocation is:

```bash
ros2 launch launch/patient_cart.launch.py \
  generation:=Si \
  simulated:=false \
  system_config:=/home/erie_lab/cwru-erie-dVRK/system/system-SUJ-ECM-PSM1-PSM2.json
```

To run the patient-cart kinematic simulation:

```bash
ros2 launch launch/patient_cart.launch.py simulated:=true
```

Common patient-cart arguments:

| Argument | Default | Purpose |
|---|---|---|
| `generation` | `Si` | Robot generation: `Classic`, `Si`, or `Virtual` |
| `simulated` | `false` | Select kinematic simulation when `true` |
| `system_config` | `system/system-SUJ-ECM-PSM1-PSM2.json` | Real cart configuration |
| `rate` | `50.0` | State publication rate in Hz |
| `show_rcm` | `true` | Show remote centers of motion |

The standard Si SUJ model contains the physical PSM3 mounting branch because it
is part of the cart model. The launch file does not start a PSM3 arm publisher
or subscribe to PSM3 joint states.

## Surgeon-console bringup

Use `launch/surgeon_console.launch.py` to start the physical MTML and MTMR,
their state publishers, TF, and RViz with one command:

```bash
ros2 launch launch/surgeon_console.launch.py
```

Real-hardware mode is the default and uses
`system/system-MTML-MTMR.json`. An explicit invocation is:

```bash
ros2 launch launch/surgeon_console.launch.py \
  simulated:=false \
  system_config:=/home/erie_lab/cwru-erie-dVRK/system/system-MTML-MTMR.json
```

To run the surgeon-console kinematic simulation:

```bash
ros2 launch launch/surgeon_console.launch.py simulated:=true
```

The MTM visualization follows `/MTML/measured_js` and
`/MTMR/measured_js`. Gripper motion is read from
`/MTML/gripper/measured_js` and `/MTMR/gripper/measured_js`.

| Argument | Default | Purpose |
|---|---|---|
| `simulated` | `false` | Select kinematic simulation when `true` |
| `system_config` | `system/system-MTML-MTMR.json` | Real MTM configuration |
| `rate` | `50.0` | State publication rate in Hz |

## Single-arm bringup

Use `launch/dvrk_bringup.launch.py` to start one arm. Its defaults select the
real Si PSM1 and `/home/erie_lab/cwru-erie-dVRK/system/system-PSM1.json`.

```bash
ros2 launch launch/dvrk_bringup.launch.py
```

The command starts the equivalent of:

```bash
ros2 run dvrk_robot dvrk_system -j system/system-PSM1.json
```

It also starts the PSM1 joint-state publisher, robot-state publisher, TF, and
RViz. RViz follows the physical arm using `/PSM1/measured_js` and
`/PSM1/jaw/measured_js`.

To select another arm:

```bash
ros2 launch launch/dvrk_bringup.launch.py arm:=PSM2
```

By default, this selects `system/system-PSM2.json`. A configuration can also be passed
explicitly:

```bash
ros2 launch launch/dvrk_bringup.launch.py \
  arm:=PSM2 \
  generation:=Si \
  system_config:=/home/erie_lab/cwru-erie-dVRK/system/system-PSM2.json
```

To run the single-arm kinematic simulation instead of hardware:

```bash
ros2 launch launch/dvrk_bringup.launch.py simulated:=true
```

Common single-arm arguments:

| Argument | Default | Purpose |
|---|---|---|
| `arm` | `PSM1` | Arm name, such as `PSM1`, `PSM2`, or `ECM` |
| `generation` | `Si` | Robot generation: `Classic`, `Si`, or `Virtual` |
| `simulated` | `false` | Select kinematic simulation when `true` |
| `system_config` | `system/system-<arm>.json` | Real-hardware dVRK system configuration |
| `instrument` | generation default | PSM instrument model, such as `420006` |
| `endoscope` | empty | ECM endoscope model |
| `rate` | `50.0` | State publication rate in Hz |
| `show_rcm` | `true` | Show the remote center of motion in the model |

## Troubleshooting

### RViz opens but the robot does not move

Confirm that `dvrk_system` is running, the arm is powered and homed, and the
corresponding measured-joint-state topic has an active publication rate:

```bash
ros2 topic hz /PSM1/measured_js
```

### Repeated TF_OLD_DATA warnings at time zero

The full-system and patient-cart launches disable dVRK's Cartesian TF bridge
with `-P 0` and use the model state publishers for TF. The bridge can broadcast
invalid Cartesian measurements with zero timestamps, which RViz rejects after
receiving newer transforms. Measurement topics remain available.

Restart the launch after updating these files. When running `dvrk_system`
manually alongside the model state publishers, also pass `-P 0`. A standalone
`dvrk_system` without model publishers still needs its bridge to provide TF.

### RViz tool geometry does not match the installed tool

Pass the correct instrument model. For example, the Si Large Needle Driver is
`420006`:

```bash
ros2 launch launch/dvrk_bringup.launch.py instrument:=420006
```

### A configuration file cannot be found

Pass its absolute path:

```bash
ros2 launch launch/patient_cart.launch.py \
  system_config:=/home/erie_lab/cwru-erie-dVRK/system/system-SUJ-ECM-PSM1-PSM2.json
```

### Show all supported launch arguments

```bash
ros2 launch launch/dvrk_bringup.launch.py --show-args
ros2 launch launch/patient_cart.launch.py --show-args
ros2 launch launch/surgeon_console.launch.py --show-args
ros2 launch launch/dvrk_full.launch.py --show-args
```

Stop a launch and its child processes with `Ctrl+C` in the terminal that
started it.
