# CWRU ERIE dVRK — Classic, dVRK 2.5

This branch uses the same organization and launch entry points as `dvrk-si`,
with Classic hardware identities, UDP/FireWire transport, fixed base calibration,
and the MTMR actuator-3 potentiometer fallback.

- Root: arm definitions, calibrated IO JSON, gravity compensation, `suj-fixed.json`.
- `system/`: single-arm, cart, surgeon console and combined teleoperation systems.
- `launch/`: bringup and visualization; one `dvrk_system` process per launch.
- `pid/`: MTMR-only feedback controller (D=0.07, 0.6-degree deadband, observer off on axis 3).
- `cal/`: original ISI files and calibration CSV history.
- `legacy/2.3/`: original XML, arm, console, launch and PID files, preserved for reference.
- `migration/`: provenance, audit and migration scripts.

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

Do not run these hardware launches concurrently. Generation defaults to Classic.
Patient-cart and surgeon-console launches accept `simulated:=true` and use local
kinematic simulation systems. Full launch is real hardware only.

## Calibration preservation

IO JSON is converted from the *current calibrated XML*, not regenerated from
original `.cal` files. Degree/millimetre values are converted to radians/metres.
Current conversion coefficients, limits, tolerances, brake currents/timing,
board/axis assignments and coupling are preserved. `has_encoder_preload: true`
is explicit because the new stack's default differs from the old XML parser.
GC coefficients and actual base-to-base calibration are copied byte-for-byte.
No recalibration was performed. Format conversion alone is not a reason to
repeat calibration, but these files still require startup and physical validation
on the new software. New default controller/kinematic behavior is not identical.

The patched new sawRobotIO1394 library is required for MTMR's encoder fields.
Do not use the old encoder-referenced potentiometer scale calibration procedure
on MTMR with the faulty encoder/fallback enabled.

## Fixed SUJ and branch differences

This Classic robot has no SUJ read boards. `SUJ_Fixed` reads the real
`suj-fixed.json` copied from the old `arm/suj-fixed.json`. This frequently updated
file remains Git-ignored, as does its legacy backup. Back it up separately before
switching branches; Git alone does not protect ignored files.

Unlike Si, visualization does not invent moving SUJ joints. It publishes fixed
mounting TFs from the same calibration and attaches Classic arm models there.
The default base reference is the calibrated cart/world frame. If overriding
system configuration with different base calibration, update the visualization's
`suj_config` as well. Launch changes were checked statically, not run on hardware.

Transport remains `udpfw`. Pedals and ISI head sensor remain wired to the MTML
controller (boards 0/1), with the same bits/polarities/debounce as before. PSM1
is paired with MTMR; PSM2 with MTML. Camera-relative teleoperation uses ECM.

`system-Grant.json` retains the original alternate PSM2 tool setting:
`LARGE_NEEDLE_DRIVER:420006[12]`, despite its historical arm file being named
`PSM2-CADIERE_FORCEPS.json`. The migration does not guess a replacement tool.

The original `udp` branch files are available in Git and in `legacy/2.3/`.
The `dvrk-si` branch has not been modified. See `migration/audit.md`.

## HRSV stereo video

Start the USB capture source, stereo alignment, and separate HRSV eye windows with:

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
| `device` | `HD` | Select SD or HD USB capture configurations |
| `source_config` | Empty (selected by `device`) | Capture configuration; relative to the base directory, or an absolute path |
| `alignment_config` | Empty (selected by `device`) | Camera alignment configuration; relative to the base directory, or an absolute path |
| `display_config` | Empty (selected by `device`) | HRSV rendering configuration; relative to the base directory, or an absolute path |

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

The default is `device:=HD`. For SD, use `device:=SD`, which selects `stereo_source_sd.json`,
`stereo_alignment_sd.json`, and `stereo_display_hrsv_sd.json`. SD uses left
`/dev/video4` and right `/dev/video5` at 640x480, 29.97 Hz. SD alignment offsets
and display offset start at zero, with a full-frame crop; calibrate later.
The SD display scales to the HRSV's 1024x768 per eye.

For HD USB capture (the default), use:

```bash
ros2 launch launch/stereo_video_pipeline_hrsv.launch.py device:=HD
```

HD uses left `/dev/video2` and right `/dev/video0`, matching
`dvrk_magewell/launch/publish_stereo.launch.py`. It selects
`stereo_source_hd.json`, `stereo_alignment_hd.json`, and
`stereo_display_hrsv_hd.json`. HD calibration values are inherited from the migrated
configs. Explicit configuration arguments override the selected device defaults.
USB capture pipelines request raw video; hardware format negotiation and device
numbering still need to be checked on the Classic computer.

## OpenXR Classic headset video

Launch the Classic patient cart (fixed SUJ, ECM, PSM1 and PSM2), OpenXR
headset, stereo video overlay, and control panel together, without teleoperation:

```bash
ros2 launch launch/openxr_dvrk.launch.py device:=HD
# SD cameras:
ros2 launch launch/openxr_dvrk.launch.py device:=SD
```

`device` defaults to `HD` and selects the existing source/alignment configs plus
`stereo_display_openxr_hd.json` or `stereo_display_openxr_sd.json`. Both OpenXR
display configs specify per-eye sizes of 1920x1080 (HD) and 960x540 (SD) and
send the HUD overlay to sawOpenXR through `@dvrk:console:stereo_overlay`.

The launch follows `si-sim-devel`'s `openxr_dvrk_si.launch.py`: source readiness
starts alignment, alignment readiness starts the overlay, and overlay readiness
starts the robot system and control panel. Exiting any pipeline process or the
robot system shuts down the launch. Requires installed `sawOpenXR`, `dvrk_data`,
`dvrk_console`, and `dvrk_robot` with the referenced video pipeline support.

The system uses this branch's Classic hardware identities and fixed SUJ config,
with all PSM and ECM teleoperation entries removed for headset video testing.
The default system file is `system/system-OpenXR-SUJ-ECM-PSM1-PSM2.json`;
the physical patient-cart arms remain configured.
Do not run it concurrently with another robot or stereo video launch.

Override `config_dir` (default: this repository's `sdi/`), `source_config`,
`alignment_config`, or `display_config` for custom video settings. Config
filenames are relative to `config_dir`; absolute paths are also accepted.
`system_config` overrides the Classic OpenXR robot system JSON.
Inspect arguments without starting hardware with:

```bash
ros2 launch launch/openxr_dvrk.launch.py --show-args
```

The installed sawOpenXR renderer uses a fixed 16:9 video plane. The SD OpenXR
display config pads each 640x480 eye image to 960x540 with black borders
(160 pixels on each side and 30 above/below), preserving the 4:3 picture
without stretching. HD is already 16:9 and needs no padding.

To view the display calibration grid inside the headset:

```bash
ros2 launch launch/openxr_dvrk.launch.py device:=SD grid:=true
```

Adjust `display_horizontal_offset_px` in the selected OpenXR display JSON,
then restart the launch to inspect the result. The installed display node has
no live offset control; `stereo_display_calibration` previews only on desktop.
Omit `grid:=true` for normal viewing.
