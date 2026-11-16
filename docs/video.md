# SDI video

[Back to quick start](../README.md). Run commands from the repository root
after sourcing your ROS 2 and dVRK workspace.

## HRSV stereo video

Start the SDI source, stereo alignment, and separate HRSV eye windows with:

```bash
ros2 launch launch/stereo_video_pipeline_hrsv.launch.py
```

The HRSV SDI and simulator display configurations set `"output_display": ":1.1"`.
Launch from your desktop terminal with `DISPLAY=:1.0` (or `DISPLAY=:1`):
the control widget stays on that desktop, and the image windows use `:1.1`.
The monitor dropdowns list the HRSV screen's monitors; select each eye's
monitor and enable Fullscreen. These choices are saved per viewer name.
Both X displays must be accessible to your user through the normal Xauthority
setup. An unavailable output display stops the viewer with an error.

`:1.0` and `:1.1` are screens 0 and 1 of X display `:1`; an independent X
server would use another display number, for example `:2.0`. Either form is
supported. Edit `output_display` for your setup, or override it when running
the viewer directly:

```bash
DISPLAY=:1.0 ros2 run dvrk_console stereo_display -c sdi/stereo_display_hrsv_hd.json --output-display :1.1
```

Omitting `output_display` or setting it to `""` keeps controls and images on
the launch display. After updating `dvrk_console`, rebuild and source the
workspace before using these configurations:

```bash
cd /home/erie_lab/dvrk_ws
colcon build --packages-select dvrk_console
source install/setup.bash
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
| `source_config` | `stereo_source_hd.json` | Capture configuration; relative to the base directory, or an absolute path |
| `alignment_config` | `stereo_alignment_hd.json` | Camera alignment configuration; relative to the base directory, or an absolute path |
| `display_config` | `stereo_display_hrsv_hd.json` | HRSV rendering configuration; relative to the base directory, or an absolute path |

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
