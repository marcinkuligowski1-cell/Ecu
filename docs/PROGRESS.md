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
