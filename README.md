# CWRU ERIE dVRK Launch Files

This repository provides ROS 2 launch files for visualizing and operating either
one dVRK arm or the complete patient cart. Real-hardware mode is the default.
The launch files start `dvrk_system`, the required state publishers, TF, and
RViz, so a separate `dvrk_system` command is not needed.

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

## Verify real-robot state updates

After the robot is running, check that measured joint states are being
published:

```bash
ros2 topic hz /PSM1/measured_js
ros2 topic echo /PSM1/measured_js --once
ros2 topic hz /PSM1/jaw/measured_js
```

For the complete cart, useful checks include:

```bash
ros2 topic hz /PSM2/measured_js
ros2 topic hz /ECM/measured_js
ros2 topic hz /SUJ/PSM1/measured_js
ros2 topic hz /SUJ/PSM2/measured_js
ros2 topic hz /SUJ/ECM/measured_js
```

List the running dVRK and visualization nodes with:

```bash
ros2 node list
```

## Troubleshooting

### RViz opens but the robot does not move

Confirm that `dvrk_system` is running, the arm is powered and homed, and the
corresponding measured-joint-state topic has an active publication rate:

```bash
ros2 topic hz /PSM1/measured_js
```

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
