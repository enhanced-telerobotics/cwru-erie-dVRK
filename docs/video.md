# SDI video

[Back to quick start](../README.md). Run commands from the repository root
after sourcing your ROS 2 and dVRK workspace.

## HRSV stereo video

Start the SDI source, GPU stereo rectification, and separate HRSV eye windows with:

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
the launch file location. The source starts immediately. The rectifier starts
when the side-by-side source socket is available, and the HRSV display starts
when its rectified input socket is available. The rectifier uses
`stereo_rectify_hd.json` and follows `~/.ros/camera_info/stereo_source_left.yaml` and
`~/.ros/camera_info/stereo_source_right.yaml` at startup. Update both symlinks to a matched
calibration pair and restart this launch after recalibrating. This launch starts video processes;
run the full dVRK system separately for robot operation and HUD status.

The default `1080i5994` SDI source deinterlaces both fields into 59.94
progressive frames per second per eye. The HRSV display and ROS image publishers
use this capture rate.

| Argument | Default | Purpose |
|---|---|---|
| `use_ros` | `false` | Publish source, rectified, and overlaid image sockets to ROS 2 |
| `config_dir` | This repository's `sdi/` | Base directory for video JSON files when `system` is empty |
| `system` | Empty | Optional subdirectory name under `config_parent`; when set, overrides `config_dir` |
| `config_parent` | Empty | Parent directory for `system`; required when `system` is set |
| `source_config` | `stereo_source_hd.json` | Capture configuration; relative to the base directory, or an absolute path |
| `display_config` | `stereo_display_hrsv_hd.json` | HRSV rendering configuration; relative to the base directory, or an absolute path |

Here, `system` means a video configuration directory, not a robot system JSON.
The robot configuration belongs to `dvrk_full.launch.py`'s `system_config` argument.
An absolute configuration filename overrides the base directory for that file.

To publish the image streams while running the HRSV display:

```bash
ros2 launch launch/stereo_video_pipeline_hrsv.launch.py use_ros:=true
```

| Stream | Default ROS image topic |
|---|---|
| Left source eye | `/stereo_source/left/camera/image_raw` |
| Right source eye | `/stereo_source/right/camera/image_raw` |
| Side-by-side source | `/stereo_source/stereo/camera/image_raw` |
| Side-by-side rectified | `/stereo_rectify/stereo/camera/image_raw` |
| Side-by-side display with overlays | `/stereo_display/overlay/camera/image_raw` |

Each ROS publisher starts after its producer starts and its socket is available.
The launch checks every 250 ms for up to 15 seconds per stage and logs the
socket names if the wait expires. Custom socket names determine the ROS namespaces.

With `ffmpeg_image_transport` installed, each bridge sets an H.264 target bitrate
of 8 Mbit/s. Check for a packet on each FFmpeg topic with:

```bash
for stream in stereo_source/{left,right,stereo} stereo_rectify/stereo stereo_display/overlay; do
  ros2 topic echo "/$stream/camera/image_raw/ffmpeg" --once --field encoding --timeout 15
done
```

To select another video directory:

```bash
ros2 launch launch/stereo_video_pipeline_hrsv.launch.py config_dir:=/path/to/video
```

To inspect the arguments without starting the pipeline:

```bash
ros2 launch launch/stereo_video_pipeline_hrsv.launch.py --show-args
```
