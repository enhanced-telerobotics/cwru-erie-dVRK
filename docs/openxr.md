# Classic OpenXR video

[Back to quick start](../README.md).

## OpenXR Classic headset video

Launch the Classic patient cart (fixed SUJ, ECM, PSM1 and PSM2), OpenXR
headset and stereo video overlay together, without teleoperation. Add
`panel:=screen`, `panel:=web`, or `panel:=both` to also start a control panel:

```bash
ros2 launch launch/openxr_dvrk.launch.py device:=HD
# SD cameras:
ros2 launch launch/openxr_dvrk.launch.py device:=SD
```

`device` defaults to `HD` and selects the existing source/alignment configs plus
`stereo_display_openxr_hd.json` or `stereo_display_openxr_sd.json`. Both OpenXR
display configs specify per-eye sizes of 1920x1080 (HD) and 960x540 (SD) and
send the HUD overlay to sawOpenXR through `@dvrk:console:stereo_overlay`.

Source readiness
starts alignment, alignment readiness starts the overlay, and overlay readiness
starts the robot system and any selected control panels. Exiting any pipeline process or the
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
