# ECU calibration selector — research workspace

Public, non-flashable research code for a **three-profile calibration selector**.

## What is included

- A host-only Python state machine for a proposed pedal-input selector.
- Automated safety-oriented unit tests.
- A public-file scanner to prevent accidental uploads of ECU firmware, EEPROM dumps, archives, keys and obvious identifiers.
- GitHub Actions CI and a progress log.

## What is NOT included

No firmware images, EEPROM dumps, VINs, vehicle identifiers, immobilizer data, private diagnostics, secrets, or working ECU patches.

**This repository does not contain a flashable ECU binary.** All selector behaviour is simulated. It is not connected to engine torque control, the tachometer, a CAN bus, or physical pedal inputs.

See `docs/PROGRESS.md` and `SECURITY.md` for limitations and next verification steps.

### Local checks

```sh
python -m unittest discover -s tests -v
python tools/check_public_tree.py
```

This is experimental software for offline analysis and bench-only verification.
