# EGR calibration recognition — read-only, synthetic-only tests

## Goal

Recognize a common EDC15 16×13 DD/DC + D9 axis layout and separate a fresh-air-request EGR **candidate** from a similarly shaped N75-duty **candidate**. A low starting RPM (zero) supports the EGR interpretation; a substantially positive first RPM supports the N75 interpretation. These are heuristics based on the public ZedSuite source, not an authoritative map definition or ECU control-flow proof.

The tool also locates some 20×1 RPM curves that can represent EGR hysteresis. It compares source and tuned table cells **read-only** and reports geometry, number of modified values and whether the destination is uniform. It never writes a patch or recalculates checksums.

## Validation and boundaries

15 new unit tests use **fabricated** bytes only. Nothing in this repository identifies an individual vehicle, calibration or ECU dump. Public examples never include extracted private table contents or offsets.

Disabling EGR fault-path monitoring is **not** the same as reducing commanded EGR flow: the former changes diagnostic records and the latter changes control calibrations. Exhaust-emission consequences and the legality of disabling emission monitoring must be addressed independently; it is not proposed as a road-vehicle modification here.

No real pedal RAM inputs, executed C167 cross-references, diagnostic safeguards or checksum scheme have been verified. Passing host-only tests is not approval to flash an ECU.

## Source

Public ZedSuite EDC15VM map classifier: https://github.com/LeZed97/ZedSuite/blob/master/src-tauri/src/detector/ecu/bosch/edc15vm/mod.rs
