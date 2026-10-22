# Calibration research — public, synthetic-only

This phase adds a **read-only** locator for a known EDC15 launch-control (LC) speed-axis structure and a separate check for whether a candidate destination block is already occupied.

## Public references and scope

The LC layout is described in publicly released ZedSuite source code, especially `src-tauri/src/detector/ecu/bosch/launch_control.rs` and `src/lib/ecu/solutions/index.ts` in [LeZed97/ZedSuite](https://github.com/LeZed97/ZedSuite) (GPL-3.0). The scanner is a reference implementation using the publicly documented data format. It contains no proprietary ECU program.

The scanner locates a neutralized descriptor in one **synthetic** input and an enabled speed-axis signature in another. It checks whether the mapped table data is unchanged and whether a proposed bank region contains non-fill bytes.

**It cannot verify** execution of the LC function in ECU code, identify physical pedal inputs, solve C167 memory paging, rewrite engine calibration, remove LC safely, or repair firmware checksums. A recognizable 30-byte axis is not proof of firmware functionality.

## Tests

15 new unit tests use fabricated byte streams. The existing 35 tests exercise the host-only pedal selector and the public-file policy. GitHub Actions executes 50 tests in total.

## Public/private boundary

No original or modified ECU BIN, EEPROM, VIN, private calibration, proprietary dump, extracted memory address or vehicle-specific diagnostic is published here. Private inspections run outside GitHub. Never paste private binary excerpts in GitHub Issues or workflow logs.

## Verification gate

A safe ECU implementation still requires independently validated reachable C167 control flow, RAM signal provenance, full DPP lifetime, checksum variant verification, instrumentation isolation, and bench/hardware-in-loop tests. Passing public CI **does not** establish vehicle or flash safety.
