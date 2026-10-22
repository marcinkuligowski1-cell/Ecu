"""Offline profile selection simulator.

This module has no ECU, CAN, RPM output, calibration writing, or vehicle I/O.
It is NOT a firmware implementation and its tests do not establish road safety.
"""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Inputs:
    ms: int
    engine: bool = True
    clutch: bool = True
    brake: bool = True
    speed_kmh: float = 0.0
    speed_valid: bool = True
    rpm: int = 850
    rpm_valid: bool = True
    throttle_pct: float = 0.0
    throttle_valid: bool = True
    clutch_valid: bool = True
    brake_valid: bool = True


class Selector:
    """Fail-closed simulation of discrete three-profile selection.

    Selection commits on throttle RELEASE after a distinct light press.
    Cancelled selection requires release of an arming pedal before rearming.
    """

    ARM_MS = 2000
    MAX_SAMPLE_GAP_MS = 250
    PRESS_PCT = 10.0
    RELEASE_PCT = 3.0
    ABORT_PCT = 20.0
    MIN_PRESS_MS = 50
    MAX_PRESS_MS = 700
    RELEASE_GUARD_MS = 160
    IDLE_RPM_MIN = 650
    IDLE_RPM_MAX = 1100

    def __init__(self) -> None:
        self.selected = 2
        self.state = "idle"
        self.since = 0
        self.indication = None
        self.last_ms = None
        self._pending = None

    def _reset(self, *, lock: bool = False) -> None:
        self.state = "locked" if lock else "idle"
        self._pending = None
        self.indication = None

    @staticmethod
    def _finite_number(value, *, minimum: float, maximum: float) -> bool:
        return (not isinstance(value, bool)
                and isinstance(value, (int, float))
                and isfinite(value)
                and minimum <= value <= maximum)

    @staticmethod
    def _boolean(value) -> bool:
        return isinstance(value, bool)

    def _valid(self, x: Inputs) -> bool:
        return (isinstance(x.ms, int) and not isinstance(x.ms, bool) and x.ms >= 0
                and all(self._boolean(v) for v in (
                    x.engine, x.clutch, x.brake, x.speed_valid, x.rpm_valid,
                    x.throttle_valid, x.clutch_valid, x.brake_valid))
                and all((x.speed_valid, x.rpm_valid, x.throttle_valid,
                         x.clutch_valid, x.brake_valid))
                and self._finite_number(x.speed_kmh, minimum=0, maximum=300)
                and self._finite_number(x.rpm, minimum=0, maximum=8000)
                and self._finite_number(x.throttle_pct, minimum=0, maximum=100))

    def update(self, x: Inputs) -> None:
        """Read one snapshot; update selected profile and event only."""
        self.indication = None
        if not self._valid(x):
            self._reset(lock=True)
            self.last_ms = None
            return

        if self.last_ms is not None:
            delta = x.ms - self.last_ms
            if delta <= 0 or delta > self.MAX_SAMPLE_GAP_MS:
                self._reset(lock=True)
                self.last_ms = x.ms
                return
        self.last_ms = x.ms

        safe = (x.engine and x.brake and x.clutch and x.speed_kmh == 0
                and self.IDLE_RPM_MIN <= x.rpm <= self.IDLE_RPM_MAX
                and x.throttle_pct <= self.ABORT_PCT)
        if not safe:
            self._reset(lock=True)
            return

        released = x.throttle_pct <= self.RELEASE_PCT
        if self.state == "locked":
            return
        if self.state == "idle":
            if released:
                self.since = x.ms
                self.state = "arming"
        elif self.state == "arming":
            if not released:
                self._reset(lock=True)
            elif x.ms - self.since >= self.ARM_MS:
                self.state = "armed"
        elif self.state == "armed":
            if x.throttle_pct >= self.PRESS_PCT:
                self._pending = 1 if self.selected == 3 else self.selected + 1
                self.since = x.ms
                self.state = "pressed"
        elif self.state == "pressed":
            duration = x.ms - self.since
            if duration > self.MAX_PRESS_MS:
                self._reset(lock=True)
            elif released:
                if duration < self.MIN_PRESS_MS:
                    self._reset(lock=True)
                else:
                    self.selected = self._pending
                    self.indication = self.selected
                    self._pending = None
                    self.since = x.ms
                    self.state = "release_guard"
        elif self.state == "release_guard":
            if not released:
                self._reset(lock=True)
            elif x.ms - self.since >= self.RELEASE_GUARD_MS:
                self.state = "armed"

    def update_with_reset(self, x: Inputs) -> None:
        """Release of clutch or brake unlocks without immediately rearming."""
        if self.state == "locked" and self._valid(x) and (not x.brake or not x.clutch):
            self._reset(lock=False)
            self.last_ms = x.ms
            return
        self.update(x)
