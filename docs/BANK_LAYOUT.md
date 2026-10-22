# Calibration bank scaffold — intentionally NOT flashable

A private offline proof-of-layout can be built by copying a complete calibration source block into two other verified empty regions, keeping the tuned source bank unchanged. The block phase is checked and every destination byte must match the expected fill byte in **both** source files. The rest of the input image is identical and remains unchanged.

The public utility src/bank_layout.py accepts explicit inputs and offsets, never contains the owner's images, and has no tool to program an ECU. Every source and destination is constrained by bounds, fill and overlap checks; both SHA-256 hashes and all changed ranges are audited. Twelve tests use synthetic images.

**This is a data-layout scaffold, not a firmware image.** Relocated calibration blocks can contain position-dependent descriptors, per-block checksums, constants referenced by executable code and ECU-specific metadata. No checksum algorithm, memory page switcher, cold-start fallback, interrupt safety, diagnostic state routing or CAN gauge confirmation is implemented. The returned flashable and checksum_verified audit properties are always **false**.

Never flash a scaffold, even if a programmer reports that its file length is correct. Physical ECU bench and recovery checks must be independently performed after executable integration and checksum validation.
