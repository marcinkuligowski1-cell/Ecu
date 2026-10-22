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
