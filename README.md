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
