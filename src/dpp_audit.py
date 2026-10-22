"""Read-only C166/C167 DPP address analysis (NOT firmware integration).

A matched byte sequence is not proof of reachable instructions.
CPU mapping and no-override assumptions must be verified separately.
"""
from dataclasses import dataclass

PAGE_BYTES = 0x4000
MAX_DPP = 0x3FF
MAX_CPU = (MAX_DPP + 1) * PAGE_BYTES


@dataclass(frozen=True)
class DppCandidate:
    offset: int
    register: int
    page: int


def cpu_data_address(logical_address: int, dpps: tuple[int, int, int, int]) -> int:
    """Translate a 16-bit paged C167 data address (no override/PEC)."""
    if not isinstance(logical_address, int) or isinstance(logical_address, bool) or not 0 <= logical_address <= 0xFFFF:
        raise ValueError("16-bit logical address required")
    if len(dpps) != 4 or any(not isinstance(v, int) or isinstance(v, bool) or not 0 <= v <= MAX_DPP for v in dpps):
        raise ValueError("four 10-bit DPP indices required")
    return dpps[logical_address >> 14] * PAGE_BYTES + (logical_address & 0x3FFF)


def flash_relative(cpu_physical: int, flash_cpu_base: int, flash_size: int) -> int | None:
    """Resolve a CPU address to chip offset with an explicitly supplied assumed base."""
    if any(not isinstance(v, int) or isinstance(v, bool) for v in (cpu_physical, flash_cpu_base, flash_size)):
        raise ValueError("integer inputs required")
    if cpu_physical < 0 or flash_cpu_base < 0 or flash_size <= 0:
        raise ValueError("invalid addresses or size")
    at = cpu_physical - flash_cpu_base
    return at if 0 <= at < flash_size else None


def find_dpp_immediate_shapes(data: bytes, *, code_ranges: tuple[tuple[int, int], ...] | None = None) -> list[DppCandidate]:
    """Aligned E6 00..03 <imm16> signatures; NOT decoded control flow."""
    if code_ranges is None:
        code_ranges = ((0, len(data)),)
    found = []
    for start, end in code_ranges:
        if start < 0 or end > len(data) or start > end or start % 2 or end % 2:
            raise ValueError("bad aligned range")
        for offset in range(start, end - 3, 2):
            if data[offset] != 0xE6 or data[offset + 1] > 3:
                continue
            page = int.from_bytes(data[offset + 2:offset + 4], "little")
            if page <= MAX_DPP:
                found.append(DppCandidate(offset, data[offset + 1], page))
    return found


def changed_dpp_indices(before: tuple[int, int, int, int], after: tuple[int, int, int, int]) -> tuple[int, ...]:
    for config in (before, after):
        if len(config) != 4 or any(not isinstance(n, int) or isinstance(n, bool) or n < 0 or n > MAX_DPP for n in config):
            raise ValueError("bad DPP configuration")
    return tuple(i for i in range(4) if before[i] != after[i])


def reject_unreviewed_dpp_changes(before: tuple[int, int, int, int], after: tuple[int, int, int, int], reviewed_registers: set[int]) -> None:
    """Reject mutations to pointer registers not explicitly reviewed."""
    if not reviewed_registers.issubset({0, 1, 2, 3}):
        raise ValueError("unknown DPP register")
    changes = set(changed_dpp_indices(before, after))
    if not changes.issubset(reviewed_registers):
        raise ValueError(f"unreviewed page pointer mutations: {sorted(changes - reviewed_registers)}")
