# CWRU ERIE dVRK — Classic

ROS 2 launch files for the Classic robot, calibrated fixed bases, USB stereo
capture, HRSV displays, and Quest/OpenXR headset video.

## Start here

Source your ROS 2, dVRK, and utility workspaces in a desktop terminal, then:

```bash
cd /home/erie_lab/cwru-erie-dVRK
```

Each robot launch starts its own `dvrk_system`; run one at a time. Hardware
launches always use real hardware and wall-clock time. Power and home through
the normal console procedure. Stop with `Ctrl+C`.

## Choose a launch

All filenames below are under `launch/`. Run them as
`ros2 launch launch/<filename>`.

| Setup | Launch file | Guide |
|---|---|---|
| Full Classic robot and MTMs | `dvrk_full.launch.py` | [Hardware](docs/hardware.md) |
| Patient cart | `patient_cart.launch.py` | [Hardware](docs/hardware.md) |
| Surgeon console | `surgeon_console.launch.py` | [Hardware](docs/hardware.md) |
| Single arm | `dvrk_bringup.launch.py` | [Hardware](docs/hardware.md) |
| USB stereo → HRSV video only | `stereo_video_pipeline_hrsv.launch.py` | [Video](docs/video.md) |
| Quest headset video + Classic patient cart | `openxr_dvrk.launch.py` | [OpenXR](docs/openxr.md) |

The OpenXR launch provides video without teleoperation. Its patient-cart
configuration still starts physical arms.

## Quest quick start

Connect through WiVRn and select it as the active OpenXR runtime, then:

```bash
ros2 launch launch/openxr_dvrk.launch.py device:=HD panel:=web
```

Use `device:=SD` for the SD cameras. See the [OpenXR guide](docs/openxr.md)
for display geometry and calibration grid options.

## Options and reference

List arguments without starting hardware:

```bash
ros2 launch launch/dvrk_full.launch.py --show-args
```

Robot launches accept `panel:=none|screen|web|both`, default `none`.
The web panel uses `/home/erie_lab/Documents/envs/torch_stable/bin/python`;
source the workspace containing `dvrk_utils` first.

Hardware/RViz launches default to `use_rviz:=false`, using the robot's own
TF tree. Add `use_rviz:=true` to start model state publishers and RViz instead.
The `simulated` and `use_sim_time` switches have been removed.

```bash
ros2 launch launch/dvrk_full.launch.py panel:=both
ros2 launch launch/dvrk_bringup.launch.py arm:=PSM1 use_rviz:=true
```

See [configuration and calibration](docs/configuration.md) for Classic hardware
identities, fixed SUJ calibration, MTMR feedback settings, and migration details.
The ignored `suj-fixed.json` must be backed up separately before switching branches.
