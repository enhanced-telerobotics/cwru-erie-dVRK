# ForceN large needle drivers

Run from the repository root:

```bash
ros2 run dvrk_robot dvrk_system -j system/system-ForceN-Teleop.json
```

Both PSM1 and PSM2 use `arm/PSM-LND_ForceN.json` with fixed custom instrument
`LND_FORCEN:400906`. 400906 is a local software identifier; the physical donor
instrument is the Classic Large Needle Driver 400006. Tool geometry, coupling,
jaw limits, torque limits and engagement motions are copied from the donor.

`PSM-LND_ForceN-kinematic.json` copies the standard PSM kinematics and changes
only joint 3 (insertion) to `qmin: 0.05`, `qmax: 0.20`, in metres. This assumes
the requested 50–200 mm range refers to the calibrated joint-3 position, not
tip depth or the DH-offset-adjusted coordinate. Both tools must have this same
range. The arm's kinematic and custom-index paths resolve relative to the arm configuration
directory. The index's instrument `file` resolves relative to the process working
directory, so launch from the repository root as shown above. Underscore field
names match dVRK 2.5.

These are normal software position limits, not a physical stop or a guarantee
for every operating state. The local PSM implementation disables PID position
limit enforcement during homing/engagement. The donor engagement sequence also
rotates the tool discs. Verify the actual sensor clearance and homing/engagement
behavior before operating with the sensor attached. Starting outside the range
is not corrected safely by this configuration alone. Leave clearance from the
physical collision boundaries when confirming the final limits.

Validation performed: JSON parsing, local path resolution, both PSM bindings,
50–200 mm limits, and donor tool parameter equality. No hardware run performed.

Reference: https://dvrk.readthedocs.io/main/pages/configuration/custom-instruments.html
