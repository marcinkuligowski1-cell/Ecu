# Compact V4.1 calibration checksum validation

This module independently reproduces the two checksum correction fields of a **specific** 48-KiB Bosch calibration block. It is not a general EDC15 checksum solver, and it must refuse unknown block layouts.

## Layout

- Block length: 0xC000 bytes.
- Recognized V4.1 marker: 11 bytes at relative +1.
- Subblock A: bytes [0, 0x0B7C), correction word at +0x0B7C.
- Subblock B: bytes [0x0B80, 0x0BFFC), correction word at +0x0BFFC.
- Processing starts with two words 0x8631 and 0xEFCD, uses a rotating two-word rolling checksum, and ends by converting the state to two 16-bit correction words.

## Tested scope

- Tested **privately** against a known factory image and a separately modified calibration image; both stored correction fields matched exactly in both images.
- The same two fields also matched in each of three privately assembled 48-KiB bank copies.
- An independently checked host-side edit that restored the disabled launch-control data axis was followed by correction recalculation and six matching checks.
- Twelve new public tests contain fabricated byte arrays only. No original or modified ROM, offsets from a private ECU outside the generic layout, or identifying information is present.

## Strict limitation

Matching these fields does not establish that an executable map switcher, idle signal acquisition, boot process, watchdog or live sensor routing will work on a physical ECU. **This repository has no functional multimapping firmware.** Do not flash output from any offline bank-scaffold tool.

The checksum algorithm was compared against the public checksum implementation in the [kw1281test](https://github.com/gmenounos/kw1281test) project and the Bosch V4.1 structures described in [ZedSuite](https://github.com/LeZed97/ZedSuite). Ensure license obligations are respected if reusing upstream source directly.
