# Offline selector: assumptions, hazards, and verification requirements

This public repository contains **only** an offline Python state-machine simulator. It has no vehicle, CAN, EEPROM, FLASH, injection, or tachometer interface.

## Functional contract (offline simulation)

- Three profiles; profile 2 selected after each simulator initialization.
- Two seconds of continuous valid samples with clutch and brake held, engine at idle, speed exactly zero, and accelerator released, arms selection.
- Every short, low-throttle **press followed by release** selects the next profile; holding throttle does not repeat.
- Throttle above the demonstration threshold counts as driving intent and aborts selection.
- Sensor validity failure, NaN/Infinity, time reversal, duplicate timestamp, data-gap timeout, movement, excessive RPM, or pedal release stops selection.
- After aborting, at least one arming pedal must be released to permit rearming.
- The `indication` output is a profile **number**, not a CAN frame or engine-RPM request.

All time, speed, pedal and RPM thresholds are illustrative and have **not** been validated against physical signals. They must not be transferred to engine control as-is.

## Unresolved hazards

1. Actual ECU input pin polarity, analog conversion, RAM bit provenance, filter timing and failure diagnostics have not been confirmed.
2. A displayed speed of zero may not prove true standstill, especially on a slope.
3. Accelerator use at idle may raise engine speed or request torque. This simulator does not override real engine behavior.
4. C167 memory paging, watchdog, interrupts, RAM layout, stack, checksum and physical ECU runtime behavior are not verified.
5. Instrument-only confirmations must remain isolated from engine-speed computations. No instrument patch is present.
6. Engine fault-path modifications may mask mechanical problems. This repository contains none.

## Release gate

Never treat the host-only test results as proof of vehicle safety. A flashable image requires separately verified hardware IO, reviewed firmware integration, independent output isolation, checksum checks and bench/hardware-in-loop tests.
