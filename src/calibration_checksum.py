"""Host-side Bosch V4.1 compact calibration checksum checks, no ECU I/O.

This implementation is restricted to a specific 48-KiB block layout and must
not be assumed correct for other EDC15 variants. It cannot create a usable
map-switch firmware. Based on public C166 algorithm analysis; see docs.
"""
from dataclasses import dataclass

BLOCK_LEN = 0xC000
PARTS = ((0, 0x0B7C, 0x0B7C), (0x0B80, 0x0BFFC, 0x0BFFC))
SEED_LOW = 0x8631
SEED_HIGH = 0xEFCD
_MASK = 0xFFFF
V41_MARKER = bytes.fromhex("67 FF FF FF FF FF FF 56 34 2E 31")


@dataclass(frozen=True)
class CheckResult:
    field_offset: int
    stored: int
    expected: int
    match: bool


def _word(buf: bytes, pos: int) -> int:
    return buf[pos] | (buf[pos+1] << 8)


def _ror16(value: int, shift: int) -> int:
    shift &= 15
    return ((value >> shift) | (value << (16-shift))) & _MASK


def _rol16(value: int, shift: int) -> int:
    shift &= 15
    return ((value << shift) | (value >> (16-shift))) & _MASK


def calculate_correction(data: bytes) -> int:
    """Return correction using the CPU-equivalent two-pair rotation loop."""
    return _calc(data)


def _calc(data: bytes) -> int:
    """Exact 4-word loop of the CPU checksum; no byte ranges are skipped."""
    if not data or len(data) % 4:
        raise ValueError("bad size")
    lo, hi = SEED_LOW, SEED_HIGH
    offset = 0
    while offset < len(data):
        lo ^= _word(data, offset); offset += 2
        shift = hi & 15
        lo = _rol16(lo, shift)
        carry = int(shift != 0 and (lo & 1) != 0)
        hi = (hi - _word(data, offset) - carry) & _MASK; offset += 2
        hi ^= lo
        if offset >= len(data):
            break
        lo = (lo - _word(data, offset) - 1 + 0xDAAD) & _MASK; offset += 2
        hi ^= _word(data, offset); offset += 2
        hi = _ror16(hi, lo & 15)
    return (((hi ^ 0xDF9B) & _MASK) << 16) | ((lo - 0xAB85) & _MASK)


def _validate(block: bytes) -> None:
    if len(block) != BLOCK_LEN:
        raise ValueError("Expected exactly one 48-KiB block")
    if block[1:12] != V41_MARKER:
        raise ValueError("Unrecognized V4.1 block marker; refusing to proceed")


def inspect_block(block: bytes) -> tuple[CheckResult, CheckResult]:
    """Read-only inspection of two known checksum-bearing subregions."""
    _validate(block)
    results = []
    for start, end, field in PARTS:
        expected = _calc(block[start:end])
        stored = int.from_bytes(block[field:field+4], "little")
        results.append(CheckResult(field, stored, expected, expected == stored))
    return tuple(results)


def rewrite_correction_fields(block: bytes) -> bytes:
    """Return a COPY with just two correction fields updated. Not flashable."""
    _validate(block)
    result = bytearray(block)
    for start, end, field in PARTS:
        result[field:field+4] = _calc(result[start:end]).to_bytes(4, "little")
    return bytes(result)
