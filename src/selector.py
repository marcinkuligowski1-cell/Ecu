"""Offline simulator only: no physical ECU, CAN or engine interfaces."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Inputs:
    ms: int
    engine: bool = True
    clutch: bool = True
    brake: bool = True
    speed_kmh: float = 0.0
    speed_valid: bool = True
    rpm: int = 850
    throttle_pct: float = 0.0

class Selector:
    ARM_MS = 2000
    PRESS_PCT = 10.0
    RELEASE_PCT = 3.0
    ABORT_PCT = 20.0
    MIN_PRESS_MS = 50
    MAX_PRESS_MS = 700
    RELEASE_GUARD_MS = 160

    def __init__(self):
        self.selected = 2
        self.pending = None
        self.state = "idle"
        self.since = 0
        self.indication = None
        self.last_ms = None

    def cancel(self):
        self.state = "idle"
        self.pending = None
        self.indication = None

    def update(self, x: Inputs):
        self.indication = None
        if self.last_ms is not None and x.ms < self.last_ms:
            self.cancel()
            self.last_ms = x.ms
            return
        self.last_ms = x.ms
        safe = (x.engine and x.brake and x.clutch and x.speed_valid
                and x.speed_kmh == 0.0 and 650 <= x.rpm <= 1100
                and 0 <= x.throttle_pct <= self.ABORT_PCT)
        if not safe:
            self.cancel()
            return
        released = x.throttle_pct <= self.RELEASE_PCT
        if self.state == "idle":
            if released:
                self.since = x.ms
                self.state = "arming"
        elif self.state == "arming":
            if not released:
                self.cancel()
            elif x.ms - self.since >= self.ARM_MS:
                self.state = "armed"
        elif self.state == "armed":
            if x.throttle_pct >= self.PRESS_PCT:
                self.pending = 1 if self.selected == 3 else self.selected + 1
                self.since = x.ms
                self.state = "pressed"
        elif self.state == "pressed":
            duration = x.ms - self.since
            if duration > self.MAX_PRESS_MS:
                self.cancel()
            elif released:
                if duration < self.MIN_PRESS_MS:
                    self.cancel()
                else:
                    self.selected = self.pending
                    self.indication = self.selected
                    self.pending = None
                    self.since = x.ms
                    self.state = "release_guard"
        elif self.state == "release_guard":
            if not released:
                self.cancel()
            elif x.ms - self.since >= self.RELEASE_GUARD_MS:
                self.state = "armed"
