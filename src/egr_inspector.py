"""Read-only heuristic classification of EDC15VM EGR and similarly shaped maps.

Does not modify data, decode ECU code flow, or prove EGR valve behavior.
All public tests use synthetic bytes.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class MapCandidate:
    descriptor: int
    data_offset: int
    kind: str
    shape: tuple[int, int]
    rpm_axis: tuple[int, ...]
    other_axis: tuple[int, ...]


@dataclass(frozen=True)
class MapComparison:
    descriptor: int
    kind: str
    data_offset: int
    cells: int
    changed_cells: int
    changed_bytes: int
    axes_unchanged: bool
    original_min: int
    original_max: int
    modified_min: int
    modified_max: int
    modified_unique_values: int


def _u16(image: bytes, pos: int) -> int:
    return image[pos] | (image[pos + 1] << 8)


def _increasing(values: tuple[int, ...]) -> bool:
    return all(a < b for a, b in zip(values, values[1:]))


def scan_16x13(image: bytes, *, start: int = 0, end: int | None = None) -> list[MapCandidate]:
    """Recognize DD/DC + D9 family. Label EGR only when RPM starts at zero.

    The same axis IDs are used by N75 duty cycle tables in some ROMs.
    Axes alone cannot verify physical map usage.
    """
    end = len(image) if end is None else end
    if start < 0 or start > end or end > len(image):
        raise ValueError("invalid scan range")
    out = []
    for p in range(start + (start & 1), end - 482 + 1, 2):
        if image[p + 1] not in (0xDD, 0xDC) or _u16(image, p + 2) != 16:
            continue
        second = p + 4 + 32
        if image[second + 1] != 0xD9 or _u16(image, second + 2) != 13:
            continue
        rpm = tuple(_u16(image, p + 4 + 2*i) for i in range(16))
        other = tuple(_u16(image, second + 4 + 2*i) for i in range(13))
        if not (_increasing(rpm) and _increasing(other) and 0 <= rpm[0] <= 1500
                and 2500 <= rpm[-1] <= 7000 and 0 <= other[0] <= 500
                and 2000 <= other[-1] <= 7000):
            continue
        kind = "egr_fresh_air_candidate" if rpm[0] <= 100 else (
            "n75_duty_candidate" if rpm[0] >= 400 else "unknown_dd_d9")
        out.append(MapCandidate(p, second + 4 + 26, kind, (16, 13), rpm, other))
    return out


def scan_hysteresis_20(image: bytes, *, start: int = 0, end: int | None = None) -> list[MapCandidate]:
    """Generic 20-point RPM curves, among which EGR hysteresis may appear."""
    end = len(image) if end is None else end
    if start < 0 or start > end or end > len(image):
        raise ValueError("invalid scan range")
    out = []
    for p in range(start + (start & 1), end - 84 + 1, 2):
        if image[p + 1] not in (0xDD, 0xDC, 0xEB) or _u16(image, p + 2) != 20:
            continue
        rpm = tuple(_u16(image, p + 4 + 2*i) for i in range(20))
        if not (_increasing(rpm) and rpm[0] <= 1500 and 1500 <= rpm[-1] <= 6500):
            continue
        out.append(MapCandidate(p, p + 44, "egr_hysteresis_candidate", (20, 1), rpm, ()))
    return out


def compare_map(original: bytes, modified: bytes, candidate: MapCandidate) -> MapComparison:
    """Compare only values of a structurally identified map, never patch."""
    if len(original) != len(modified):
        raise ValueError("image size mismatch")
    cells = candidate.shape[0] * candidate.shape[1]
    start = candidate.data_offset
    end = start + 2*cells
    if start < candidate.descriptor or end > len(original):
        raise ValueError("candidate outside image")
    ov = tuple(_u16(original, start+2*i) for i in range(cells))
    mv = tuple(_u16(modified, start+2*i) for i in range(cells))
    return MapComparison(
        candidate.descriptor, candidate.kind, start, cells,
        sum(a != b for a, b in zip(ov, mv)),
        sum(a != b for a, b in zip(original[start:end], modified[start:end])),
        original[candidate.descriptor:start] == modified[candidate.descriptor:start],
        min(ov), max(ov), min(mv), max(mv), len(set(mv)))
