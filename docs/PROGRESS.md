# Engineering progress — public sanitized report

## 2026-10-22
- Repository initialized without original firmware.
- Added a host-only three-profile selector simulation. Default profile is 2.
- Simulation: hold clutch and brake at zero speed and idle for two seconds, then each short, distinct light throttle press/release requests the next profile (2 -> 3 -> 1 -> 2).
- Interlocks cancel selection upon movement, invalid speed, pedal release, excessive throttle or RPM outside idle range.
- Wrote 15 offline unit tests plus a conservative public-file scanner.
- Test results from GitHub Actions require independent verification.

## Verification status

| Item | Status |
|---|---|
| Three-profile selector | Offline prototype |
| Separate pedal-press detection | Host-only tests |
| Physical pedal inputs | Not validated |
| Firmware bank mapping | Not validated |
| Tachometer display | Concept only; no CAN writes |
| Launch Control replacement | Not implemented |
| ECU checksum & bench test | Not performed |
| Flashable multimap | **Not available** |

## Next engineering work
1. Validate actual hardware signal acquisition privately on a bench.
2. Check noise, timeouts and fail-closed behavior of candidate input signals.
3. Independently validate code-bank assumptions and memory integrity.
4. Isolate instrument display from true engine-speed calculations.
5. Do not attempt ECU flashing based on these host tests.
