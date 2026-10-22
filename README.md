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
