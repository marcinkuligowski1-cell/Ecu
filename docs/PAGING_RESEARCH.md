# C166/C167 data paging — offline research only

The C167 has four data page pointers (DPP0–DPP3). Each selects a 16-KiB page. For an ordinary paged logical 16-bit data address, its two most significant bits select one DPP.

For this restricted case, assuming no EXTS/EXTP override or PEC transfer:

    physical = DPP[logical >> 14] * 0x4000 + (logical & 0x3FFF)

Source: Infineon C167CR User's Manual, CPU chapter on Data Page Pointers.

## Why generic three-bank code cannot be copied blindly

Some EDC15 map-switch examples modify DPP0, DPP1, and DPP2 together. However, a specific ECU can use one of those pointers for unrelated tables, code constants, or intermediate data. Changing it without tracing all consumers can silently corrupt reads.

The read-only src/dpp_audit.py includes an address translator, an aligned opcode-shape scanner and a guard against modifying unreviewed page-pointer registers. Raw shape matches do **not** establish that the instructions are executed.

## Boundaries and safety

- All tests use synthetic values and synthetic byte streams.
- CPU-to-FLASH base addresses must be explicitly supplied and verified for each hardware variant.
- This tool is neither an ECU disassembler nor a firmware patcher, checksum writer, CAN driver or runtime implementation.
- Full cross-reference/interrupt control flow, sensor provenance, checksum variant, instrument isolation and hardware-in-loop tests are required before any ECU FLASH can be considered.
- Never commit vehicle-specific original FLASH, private addresses, identifying records, or calibration bytes to this public repository.
