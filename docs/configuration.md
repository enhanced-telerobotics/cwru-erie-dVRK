# Configuration layout

[Back to quick start](../README.md). Run commands from the repository root
after sourcing your ROS 2 and dVRK workspace.

## Configuration layout

- `arm/`: arm configurations, MTM gravity compensation, and the local SUJ kinematic copy.
- `io/`: robot, gripper, and Si SUJ IO configurations and potentiometer lookup tables.
- `system/`: system configurations with explicit relative paths to arm and IO files.
- `cal/`: calibration source files.
- `sdi/`: SDI capture, stereo alignment, and HRSV/OpenXR video configurations.
- `sim/`: simulator runtime and video configurations.
- `launch/`: ROS 2 launch files run directly by path.

Si SUJ system configurations include `io/` in `settings.path` because dVRK
locates SUJ IO files by name. The hardware launch files set the working directory
to this repository; run direct `dvrk_system` commands from here as well.
Potentiometer lookup-table paths use the `io/` prefix because the IO loader
resolves them from the working directory.
The SUJ arm configurations continue to use the upstream `kinematic/suj-si.json`.
