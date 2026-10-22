# Sanitized engineering progress

## 2026-10-22: initial public baseline

- Public GitHub repository created with non-flashable Python code, synthetic tests and no ECU dumps.
- First GitHub Actions run passed 15 offline unit tests.

## 2026-10-22: robustness update

- Added strict sensor validity and numeric-range checks, including NaN and Infinity rejection.
- Added monotonic timestamps and maximum allowed sampling-gap checks.
- Added latched cancellation after invalid conditions: a release of clutch or brake is required before rearming.
- Updated tests: 31 selector tests plus 4 public-file guard tests.
- Strengthened the publication guard using an explicit file allowlist, UTF-8 and size checks, and basic sensitive-marker detection.
- Added a safety review distinguishing host-only results from ECU hardware verification.

## Verification matrix

| Feature | State |
|---|---|
| Three-profile selector | Offline simulation only |
| Distinct press/release and debouncing | Offline tested |
| Sensor failures, stale inputs and hill-start cases | Offline tested |
| Public-file data protection | Preflight and manual review |
| Physical pedal signal identification | Not verified |
| Calibration bank mapping / code injection | Not verified |
| Tachometer command integration | Not performed |
| Removal of existing launch control | Not performed |
| Checksum + real ECU bench validation | Not performed |
| Flashable three-map firmware | **Not available** |

Do not publish private calibrations, original ECU images, vehicle identifiers, immobilizer data, or diagnostic logs.

## 2026-10-22: calibration signature audit

- Verified the public ZedSuite LC axis description against private firmware, without uploading any private material.
- Added a read-only signature inspector and bank-collision checks.
- Added 15 tests with synthetic data: 50 total offline tests.
- Checksum reproduction remains unresolved; this repository has no checksum writer or flashable image.
- Physical pedal variables, code injection and ECU bench tests remain unverified.

## 2026-10-22: DPP architecture and calibration-bank integrity review

- Examined the C167's 16-KiB data page pointer model from the manufacturer manual.
- Added a read-only DPP address translator, aligned instruction-shape scanner and a check for unreviewed page-pointer modifications.
- Added 26 synthetic host-only tests (76 total).
- A separate **private**, read-only review confirmed that a generic third-pointer rewrite would change a memory page unrelated to the intended new calibration selection. Control-flow reachability remains unverified.
- Private block analysis found repeated checksum-like markers; checksum validation remains unresolved.
- No original FLASH, EEPROM, private offsets or calibration data was published.

## 2026-10-22: diagnostic-path separation (sanitized)

- User confirmed the Stage 1 diagnostic suppressions were also applied with ZedSuite.
- Privately compared the original and modified images using the compact EDC15 fault-path layout described in ZedSuite's public source.
- Confirmed three grouped diagnostic-path records with seven modified status triplets. These changes are distinct from the LC activation axis and performance calibration changes.
- Original per-path status words must be treated as version-specific. A generic tool's “re-enable” operation may not reproduce the exact original record; do not attempt restoration without private byte-for-byte verification.
- Safety-critical boost deviation diagnostics require explicit review before any candidate firmware is produced; switching calibration profiles must not silently alter global diagnostic behavior.
- Public repository still contains no original images, diagnostic codes associated with the owner's ECU, unique offsets, or private calibration data.

## 2026-10-22 — EGR vs N75 calibration classification

- Added a read-only 16×13 map scanner distinguishing likely EGR fresh-air requests from similarly shaped N75 duty tables.
- Added recognition of possible EGR hysteresis 20×1 curves, and independent difference counts for calibration data versus diagnostic-path records.
- Added 15 artificial-data unit tests (91 total host-only tests).
- Classified affected map families privately; no private offsets, table values, ECU BIN files or DTC selections are placed on public GitHub.
- Meaning and safety of all ECU maps still require reachable C167 execution analysis and bench verification. No road-safe flashable image exists.

## 2026-10-22 — block-aligned three-bank candidate review

- Discovered that previous candidate bank locations did not follow the compact 48-KiB block layout and would overwrite reserved bytes.
- Prepared a generic offline bank scaffold helper that refuses nonempty destinations and out-of-bank differences, and never modifies original source files.
- Added twelve synthetic block-layout tests; **103 total public host tests**.
- The private copy plan respects existing reserved bytes but has unverified per-block checksums and NO executable map switching. **It is not flashable.**

## 2026-10-22 — calibration checksum breakthrough

- A Bosch two-word rolling checksum and correction scheme reproduced **both** stored 32-bit checksum fields in each of two separately provided images, checked privately without exporting either.
- The same algorithm confirmed all six checksum fields of a private 3-bank data-only scaffold.
- Restored a previously activated LC speed-axis descriptor in a private tuned data copy, preserving all other tuning/DTC bytes and recomputing the affected correction field.
- Added a public implementation with **12 synthetic tests** (115 total public host-only tests).
- Found a BOOT metadata table pointing into a separate boot-service region; most previously reported DPP0 reset signatures reside there rather than in the main engine application. Runtime reachability remains unverified.
- Still blocked on a validated executable C167 switching hook, hardware pedal flags and full runtime control-flow integration. **Do not flash the intermediate image.**

## 2026-10-22 — evaluated existing EDC15 multimap generators

- Researched VAG EDC+ (edcpl.us/multimap), which advertises EDC15V/VM profile switching plus code injection and checksum handling. The switcher requires an account and a paid entitlement; compatibility with the exact user's image is not yet verified.
- Researched Chip & Tune by HB EDC15 Mapswitch, which advertises three banks for distributor-pump and pump-injector EDC15, pedal/CC controls and tachometer feedback. It requires an account, and the vendor requires separate checksum correction.
- ZedSuite remains useful for map comparisons, but its published roadmap explicitly excludes an automatic multimap switcher.
- Prepared a **private, non-flashable** builder-input package from privately held images, with one calibration variant returned to a neutral LC axis. The inputs retain existing checksums unchanged, so do NOT flash them and do NOT publish them.
- No third-party generator has been executed and no flashable output has been produced. Before using a vendor-generated output, independent firmware/boot safety checks and ECU-recovery capability remain required because only one ECU is available.
