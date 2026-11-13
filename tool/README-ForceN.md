# ForceN tools

Run from the repository root:

```bash
ros2 run dvrk_robot dvrk_system -j system/system-ForceN-Teleop.json
```

The default setup uses `400906` on PSM1 and `400972` on PSM2. To change tools,
update the PSM's `arm_file` in `system/system-ForceN-Teleop.json`:

| Physical tool | Fixed selection | Arm configuration | USB alias |
| --- | --- | --- | --- |
| Classic LND 400006 | `LND_FORCEN:400906` | `arm/PSM-400906-ForceN.json` | `400906` |
| Classic MBF 400172 | `MBF_FORCEN:400972` | `arm/PSM-400972-ForceN.json` | `400972` |
| Non-geared S LND 420006 | `LND_FORCEN:420906` | `arm/PSM-420906-ForceN.json` | `420906` |
| Second Classic MBF 400172E | `MBF_FORCEN:400872` | `arm/PSM-400872-ForceN.json` | `400872` |

Arm-file paths in the system configuration are relative to `system/`, for
example `../arm/PSM-420906-ForceN.json`.

Each arm uses fixed tool detection and `tool/custom-tool-index-ForceN.json`.
The ForceN IDs are local software IDs, not manufacturer model numbers. Each
sensor has its own ID and `/dev/<ID>` alias, so both MBFs can run together.
dVRK may append `[..]` to a tool type; `MBF_FORCEN:400872[..]` maps to `/dev/400872`.

Tool parameters come from the corresponding original dVRK instruments. Both
MBFs use the Classic 400172 parameters; only the 420006 LND has tool generation S.
All arms remain Classic.

Tool engagement pitch and yaw targets are 10 degrees inside each tool's
configured joint limits: approximately +/-70 degrees for both LND axes,
and +/-60 degrees pitch and +/-80 degrees yaw for both MBFs. Both MBF roll
engagement targets are capped at their configured limits (+/-4.4506 rad).
Jaw engagement targets remain zero. These engagement targets override the
original instrument definitions; verify clearance for the larger wrist sweep.

Insertion limits are calibrated PSM joint positions, not tip depth:

| Tools | Kinematic file | Insertion range |
| --- | --- | --- |
| Classic LND and both MBFs | `tool/ForceN-Classic-kinematic.json` | 65–210 mm |
| S LND only | `tool/ForceN-Si-kinematic.json` | 15–210 mm |

All arms use `cannula_depth: 0.070` m for the no-cannula bench setup. This sets
the native engagement-check threshold, not the insertion limits. Editing a
shared kinematic file changes every arm that uses it.

Arm kinematic and custom-index paths resolve relative to the arm configuration
directory. Index tool-file paths resolve relative to the process working
directory, so launch from the repository root.

When migrating from instance IDs, reinstall and reload the ForceN driver's
udev rules, reconnect sensors, rebuild/source `force_n`, and restart dVRK and
the tool manager. Old instance messages such as `400972[2..2]` are rejected.

Software position limits are not enforced during all homing/engagement stages;
verify sensor clearance and engagement behavior before operating. Limits are
provisional: configuration checks passed, but no hardware run was performed.
