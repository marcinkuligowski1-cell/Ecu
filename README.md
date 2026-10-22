# ECU multi-profile selector — offline research

Public, non-flashable Python reference state machine for selecting between three **simulated** calibration profiles with clutch, brake and distinct light accelerator presses.

## Behavior

- Starts in profile 2; cycles `2 → 3 → 1 → 2`.
- Requires clutch and brake held at zero speed and idle for 2 seconds to arm.
- A short, light accelerator **press and release** selects the next profile. Holding the pedal never auto-repeats.
- Invalid readings, stale samples, movement, elevated accelerator request or deviation from idle cancel selection.
- After a cancellation, clutch or brake must be released before another arming attempt.
- No change to actual fuel injection, engine RPM or CAN frames is possible with this code.

**Not an ECU patch and not flashable.** Passing host-only tests does not establish vehicle or bench safety.

Read [the safety analysis](docs/SAFETY_CASE.md), [project progress](docs/PROGRESS.md) and [public-data policy](SECURITY.md).

## Run locally

```sh
python -m unittest discover -s tests -v
python tools/check_public_tree.py
```

GitHub Actions repeats both checks for commits and pull requests.

## Read-only calibration research

A [standalone inspector](src/calibration_inspector.py) can recognize generic launch-control axis structures in offline byte streams and detect occupied candidate bank regions. It never rewrites firmware. Tests are synthetic. See [calibration research](docs/CALIBRATION_RESEARCH.md).

## C167 memory paging

Added a [read-only DPP research module](src/dpp_audit.py) and [paging explanation](docs/PAGING_RESEARCH.md). These contain no firmware and do not produce a flashable image. All tests use artificial data.

## Read-only EGR map family research

The [EGR candidate inspector](src/egr_inspector.py) distinguishes possible fresh-air-request tables from similarly shaped N75 maps and checks 20-point curves. Tests use synthetic byte arrays only. See [EGR research limits](docs/EGR_RESEARCH.md).

## Data-bank layout checker (non-flashable)

An [offline scaffold function](src/bank_layout.py) verifies fill bytes and overlapping blocks before assembling **data only**. All test data is artificial. It does not produce a flash-ready ECU binary. See [bank-layout restrictions](docs/BANK_LAYOUT.md).

## Verified compact calibration checksums (offline)

A [read-only validator and explicit correction writer](src/calibration_checksum.py) now supports a narrowly identified compact 48-KiB V4.1 block layout. See [checksum research and limitations](docs/CHECKSUM_RESEARCH.md). Tests operate only on artificial bytes; no real ECU firmware or vehicle diagnostics are stored here. There is still no runnable C167 profile-switch hook.
