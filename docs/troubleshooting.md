# Troubleshooting

[Back to quick start](../README.md).


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
ros2 launch launch/openxr_dvrk_si.launch.py --show-args
```

Stop a launch and its child processes with `Ctrl+C` in the terminal that
started it.
