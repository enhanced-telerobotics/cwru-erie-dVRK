# CWRU ERIE dVRK

ROS 2 launch files for the local Si robot, Quest/OpenXR teleoperation, PyBullet
and Newton simulation, and SDI endoscope video.

## Start here

Use a regular desktop terminal, source your ROS 2 and dVRK workspace, then:

```bash
cd /home/erie_lab/cwru-erie-dVRK
```

Choose a launch below. Each robot launch starts its own `dvrk_system`; run only
one at a time. Hardware modes are the default for the real-robot and RViz
launches. Check the emergency stop, connections, instruments, and robot
workspace before starting hardware. Power, home, and enable teleoperation
through the normal console procedure. Stop with `Ctrl+C`.

## Choose a launch

All filenames below are under `launch/`. Run them as
`ros2 launch launch/<filename>`.

| Setup | Launch file | Guide |
|---|---|---|
| Quest → real Si robot, SDI video | `openxr_dvrk_si.launch.py` | [OpenXR hardware](docs/openxr.md) |
| Quest → PyBullet, headset video | `openxr_pybullet.launch.py` | [Simulation](docs/simulation.md#openxr-teleoperation-with-pybullet) |
| Physical MTMs → PyBullet, HRSV | `mtm_pybullet_hrsv.launch.py` | [Simulation](docs/simulation.md#mtm-teleoperation-with-pybullet-and-hrsv) |
| Physical MTMs → Newton, HRSV | `mtm_newton_hrsv.launch.py` | [Simulation](docs/simulation.md#mtm-teleoperation-with-newton-and-hrsv) |
| Full real robot + MTMs, RViz | `dvrk_full.launch.py` | [Hardware](docs/hardware.md#full-dvrk-system) |
| Patient cart, RViz | `patient_cart.launch.py` | [Hardware](docs/hardware.md#patient-cart-bringup) |
| Surgeon console, RViz | `surgeon_console.launch.py` | [Hardware](docs/hardware.md#surgeon-console-bringup) |
| Single arm, RViz | `dvrk_bringup.launch.py` | [Hardware](docs/hardware.md#single-arm-bringup) |
| SDI → HRSV video only | `stereo_video_pipeline_hrsv.launch.py` | [Video](docs/video.md) |

The MTM simulator launches still use physical MTMs and hardware IO. The
OpenXR/PyBullet launch uses simulated patient arms only.

## Quest quick start

Connect the Quest through WiVRn and select WiVRn as the active OpenXR runtime.
For PyBullet:

```bash
ros2 launch launch/openxr_pybullet.launch.py
```

For the real Si robot with SDI video:

```bash
ros2 launch launch/openxr_dvrk_si.launch.py
```

| Control | Action |
|---|---|
| Right controller | PSM1 |
| Left controller | PSM2; PyBullet also supports PSM3 |
| Push a thumbstick up | Release that controller's PSM clutch |
| Click either thumbstick within 0.5 seconds | Switch PSM2 ↔ PSM3 in PyBullet |
| Hold both thumbsticks down | ECM camera mode; PSM teleoperation pauses |

## Options and reference

List options without starting processes:

```bash
ros2 launch launch/openxr_pybullet.launch.py --show-args
```

Pass overrides as `name:=value`, for example `exercise:=tray_cubes.yaml`.
See the linked guides for dependencies, configuration defaults, and examples.
[Configuration layout](docs/configuration.md) explains `arm/`, `io/`,
`system/`, `sdi/`, and `sim/`. See [troubleshooting](docs/troubleshooting.md)
for topic, TF, model, and configuration issues.

Robot launches accept `panel:=none|screen|web|both`. `screen` starts the desktop
panel from `dvrk_console`; `web` starts the browser panel from `dvrk_utils`.
All robot launches default to `none`. For example:

```bash
ros2 launch launch/openxr_dvrk_si.launch.py panel:=web
ros2 launch launch/dvrk_full.launch.py panel:=both
```

Source the workspace containing `dvrk_utils` before using `web` or `both`.
The web panel uses `/home/erie_lab/Documents/envs/torch/bin/python`.
