# Hardware and RViz

[Back to quick start](../README.md). Run commands from the repository root
after sourcing your ROS 2 and dVRK workspace.

These launches always start real hardware with wall-clock time. RViz and model
state publishers are disabled by default; add `use_rviz:=true` to enable them.
Without RViz, `dvrk_robot` publishes its default TF tree.

## Full dVRK system

Use `launch/dvrk_full.launch.py` to start the complete real system for
teleoperation:

- SUJ, ECM, PSM1, and PSM2
- MTML and MTMR
- One `dvrk_system` process
- Optional patient-cart RViz window (`use_rviz:=true`)
- Optional surgeon-console RViz window (`use_rviz:=true`)

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

The launch file starts one `dvrk_system` process for the entire cart. With
`use_rviz:=true`, it also starts the SUJ and arm state publishers and opens
the patient-cart RViz configuration.

An explicit invocation is:

```bash
ros2 launch launch/patient_cart.launch.py \
  generation:=Si \
  system_config:=/home/erie_lab/cwru-erie-dVRK/system/system-SUJ-ECM-PSM1-PSM2.json
```


Common patient-cart arguments:

| Argument | Default | Purpose |
|---|---|---|
| `generation` | `Si` | Robot generation: `Classic`, `Si`, or `Virtual` |
| `system_config` | `system/system-SUJ-ECM-PSM1-PSM2.json` | Real cart configuration |
| `rate` | `50.0` | State publication rate in Hz |
| `show_rcm` | `true` | Show remote centers of motion |

The standard Si SUJ model contains the physical PSM3 mounting branch because it
is part of the cart model. The launch file does not start a PSM3 arm publisher
or subscribe to PSM3 joint states.

## Surgeon-console bringup

Use `launch/surgeon_console.launch.py` to start the physical MTML and MTMR,
with optional state publishers and RViz:

```bash
ros2 launch launch/surgeon_console.launch.py
```

The launch uses
`system/system-MTML-MTMR.json`. An explicit invocation is:

```bash
ros2 launch launch/surgeon_console.launch.py \
  system_config:=/home/erie_lab/cwru-erie-dVRK/system/system-MTML-MTMR.json
```


The MTM visualization follows `/MTML/measured_js` and
`/MTMR/measured_js`. Gripper motion is read from
`/MTML/gripper/measured_js` and `/MTMR/gripper/measured_js`.

| Argument | Default | Purpose |
|---|---|---|
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

With `use_rviz:=true`, it also starts the PSM1 joint-state publisher,
robot-state publisher, and RViz. RViz follows the physical arm using `/PSM1/measured_js` and
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


Common single-arm arguments:

| Argument | Default | Purpose |
|---|---|---|
| `arm` | `PSM1` | Arm name, such as `PSM1`, `PSM2`, or `ECM` |
| `generation` | `Si` | Robot generation: `Classic`, `Si`, or `Virtual` |
| `system_config` | `system/system-<arm>.json` | Real-hardware dVRK system configuration |
| `instrument` | generation default | PSM instrument model, such as `420006` |
| `endoscope` | empty | ECM endoscope model |
| `rate` | `50.0` | State publication rate in Hz |
| `show_rcm` | `true` | Show the remote center of motion in the model |

## Local MTMs with remote ROS arms and HRSV video

After sourcing the dVRK and `dvrk_magewell` workspaces, run:

```bash
ros2 launch launch/dvrk_ros.launch.py
```

This starts local MTML/MTMR hardware, head sensor, and pedals using
`system/system-MTML-MTMR-ECM-PSM1-PSM2-from-ROS-Teleop.json`. MTMR controls
remote PSM1, MTML controls remote PSM2, and the camera pedal selects ECM control.
The remote patient cart must already be running in the same ROS domain, with
no other active teleoperation controller commanding those arms.

HRSV displays `/stereo_source/left/camera/image_raw/compressed` and
`/stereo_source/right/camera/image_raw/compressed` through
`dvrk_magewell/display_video`, using the HD display geometry from its
`show_hrsv.launch.py`. The display subscribes to images only; camera-info topics
are not required. No local video capture is started.

Override `left_image_topic` and `right_image_topic` with base image topics
(without `/compressed`), or use `image_transport:=raw` for raw images.
Use `ros2 launch launch/dvrk_ros.launch.py --show-args` for all options.
