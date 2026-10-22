"""Read-only, host-only binary layout inspector. NEVER writes firmware.

The LC structural signature is derived independently from the published description
of the EDC15 data layout in LeZed97/ZedSuite (GPL-3.0), see:
https://github.com/LeZed97/ZedSuite/blob/master/src-tauri/src/detector/ecu/bosch/launch_control.rs
This is a metadata locator, NOT a checksum corrector nor a safe ECU patcher.
"""
from __future__ import annotations
from dataclasses import dataclass

LC_SPEED_STEPS = tuple(range(0, 261, 20))
LC_MAP_LENGTH = 700
LC_SIG_TO_AXIS = 2
LC_SIG_TO_MAP = 86


def speed_axis_encoding():
    return (14).to_bytes(2, "little") + b"".join(v.to_bytes(2, "little") for v in LC_SPEED_STEPS)


@dataclass(frozen=True)
class LaunchControlRegion:
    signature_offset: int
    axis_header_offset: int
    map_offset: int
    enabled: bool


def _has_map_within_bounds(data: bytes, signature_offset: int) -> bool:
    return (signature_offset >= 0 and
            signature_offset + LC_SIG_TO_MAP + LC_MAP_LENGTH <= len(data))


def find_enabled_lc(data: bytes) -> list[LaunchControlRegion]:
    """Find axis with the exact 14 speed values; not proof of functional LC."""
    needle = speed_axis_encoding()
    found = []
    pos = 0
    while True:
        pos = data.find(needle, pos)
        if pos < 0:
            break
        sig = pos - LC_SIG_TO_AXIS
        if _has_map_within_bounds(data, sig):
            found.append(LaunchControlRegion(sig, pos, sig + LC_SIG_TO_MAP, True))
        pos += 1
    return found


def find_disabled_lc(data: bytes) -> list[LaunchControlRegion]:
    """Find neutralized axis descriptor; no code flow or pedal mapping inferred."""
    found = []
    for sig in range(max(0, len(data)-LC_SIG_TO_MAP-LC_MAP_LENGTH+1)):
        if (data[sig+2:sig+8] == bytes.fromhex("02 00 80 00 00 0A")
                and data[sig+10:sig+16] == bytes.fromhex("02 00 00 00 70 17")):
            found.append(LaunchControlRegion(sig, sig+LC_SIG_TO_AXIS,
                                             sig+LC_SIG_TO_MAP, False))
    return found


@dataclass(frozen=True)
class CalibrationChange:
    signature_offset: int
    axis_offset: int
    map_offset: int
    axis_changed_bytes: int
    map_700_bytes_unchanged: bool


def compare_launch_control(original: bytes, tuned: bytes) -> list[CalibrationChange]:
    if len(original) != len(tuned):
        raise ValueError("Different image lengths")
    disabled = {x.signature_offset: x for x in find_disabled_lc(original)}
    changes = []
    for active in find_enabled_lc(tuned):
        if active.signature_offset not in disabled:
            continue
        at = active.axis_header_offset
        changes.append(CalibrationChange(
            signature_offset=active.signature_offset,
            axis_offset=at,
            map_offset=active.map_offset,
            axis_changed_bytes=sum(a != b for a,b in zip(original[at:at+30], tuned[at:at+30])),
            map_700_bytes_unchanged=(original[active.map_offset:active.map_offset+LC_MAP_LENGTH]
                                     ==tuned[active.map_offset:active.map_offset+LC_MAP_LENGTH])
        ))
    return changes


def nonfill_offsets(data: bytes, start: int, length: int, fill: int=0xC3) -> list[int]:
    """Detect that a proposed destination is NOT actually a free bank."""
    if start < 0 or length <= 0 or start+length>len(data):
        raise ValueError("Invalid candidate bank bounds")
    if fill < 0 or fill > 255:
        raise ValueError("Bad fill byte")
    return [start+i for i,v in enumerate(data[start:start+length]) if v!=fill]


def dpp_immediate_candidates(data:bytes, value: int, register: int=0) -> list[int]:
    """Aligned byte signatures; NOT decoded control flow."""
    if not (0 <= value <= 65535 and 0 <= register <= 3):
        raise ValueError("Invalid DPP target")
    patt=bytes((0xE6, register)) + value.to_bytes(2,'little')
    return [i for i in range(0,len(data)-3,2) if data[i:i+4]==patt]
