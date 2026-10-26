# Hardware and RViz

[Back to quick start](../README.md). Run commands from the repository root
after sourcing your ROS 2 and dVRK workspace.

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
