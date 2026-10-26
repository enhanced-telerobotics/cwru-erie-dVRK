# OpenXR with the real Si robot

[Back to quick start](../README.md). Run commands from the repository root
after sourcing your ROS 2 and dVRK workspace.

## OpenXR teleoperation with SDI endoscope video

Connect the Quest to WiVRn and select WiVRn as the active OpenXR runtime, then
run the local real patient cart with OpenXR controllers and SDI stereo video:

```bash
ros2 launch launch/openxr_dvrk_si.launch.py
```

Source the workspace containing `saw_openxr`, `dvrk_robot`, `dvrk_data`, and
`dvrk_console` first. This starts SDI capture, stereo alignment, the OpenXR
video overlay, then one `dvrk_system` and the control panel, using pipeline
readiness messages to order startup. If capture, alignment, the video overlay,
or `dvrk_system` exits, the launch shuts down its remaining processes.

The system uses the local SUJ, ECM (344539), PSM1 (276682), and PSM2 (360087)
configurations over FireWire. The OpenXR right controller (MTMR) controls PSM1;
the left controller (MTML) controls PSM2, with individual controller clutch
inputs and PSM teleoperation scale 0.2. Both controllers also control the ECM.
Hold both thumbsticks down (toward you) to engage camera teleoperation; release
them to leave camera mode. Camera mode suspends PSM teleoperation. ECM teleop
disables haptic feedback and physical MTM workspace checks for Quest controllers.

The robot system and OpenXR video configs are in `system/system-OpenXR-SUJ-ECM-PSM1-PSM2-Teleop.json` and
`sdi/sawOpenXR-sdi-unixfd.json`. Video uses the existing
`sdi/stereo_source_hd.json` and `sdi/stereo_alignment_hd.json`, plus
`sdi/stereo_display_openxr_hd.json`. Capture defaults to DeckLink inputs 0/1
at 1080i59.94. The aligned stereo overlay is sent to OpenXR through
`@dvrk:console:stereo_overlay`.

Override `system_config`, `source_config`, `alignment_config`, or
`display_config` with an absolute JSON path as needed. Power, home, and enable
teleoperation through the normal console procedure. Stop other hardware or SDI
launches before running this one.
