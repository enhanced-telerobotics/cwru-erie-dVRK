# HRSV stereo video

[Back to quick start](../README.md).

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
