"""Host-only validation: never connects to a vehicle."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from selector import Inputs, Selector

class SelectorTests(unittest.TestCase):
    def setUp(self):
        self.s = Selector()

    def arm(self):
        self.s.update(Inputs(ms=0))
        self.s.update(Inputs(ms=2000))
        self.assertEqual(self.s.state, "armed")

    def tap(self, t):
        self.s.update(Inputs(ms=t, throttle_pct=12))
        self.s.update(Inputs(ms=t+100, throttle_pct=0))
        self.s.update(Inputs(ms=t+300, throttle_pct=0))

    def test_default(self):
        self.assertEqual(self.s.selected, 2)

    def test_cycles_by_distinct_presses(self):
        self.arm()
        for t, expected in [(2300,3), (2800,1), (3300,2)]:
            self.tap(t)
            self.assertEqual(self.s.selected, expected)

    def test_holding_does_not_repeat(self):
        self.arm()
        self.s.update(Inputs(ms=2300, throttle_pct=12))
        self.s.update(Inputs(ms=2400, throttle_pct=12))
        self.assertEqual(self.s.selected, 2)

    def test_motion_cancels(self):
        self.arm()
        self.s.update(Inputs(ms=2300, throttle_pct=12))
        self.s.update(Inputs(ms=2400, speed_kmh=0.1))
        self.assertEqual(self.s.selected, 2)
        self.assertEqual(self.s.state, "idle")

    def test_clutch_release_cancels(self):
        self.arm()
        self.s.update(Inputs(ms=2300, throttle_pct=12))
        self.s.update(Inputs(ms=2400, clutch=False))
        self.assertEqual(self.s.selected, 2)

    def test_brake_release_cancels(self):
        self.arm()
        self.s.update(Inputs(ms=2300, throttle_pct=12))
        self.s.update(Inputs(ms=2400, brake=False))
        self.assertEqual(self.s.selected, 2)

    def test_speed_sensor_invalid(self):
        self.arm()
        self.s.update(Inputs(ms=2300, speed_valid=False))
        self.assertEqual(self.s.state, "idle")

    def test_strong_throttle_cancels(self):
        self.arm()
        self.s.update(Inputs(ms=2300, throttle_pct=25))
        self.assertEqual(self.s.state, "idle")

    def test_rpm_above_idle_cancels(self):
        self.arm()
        self.s.update(Inputs(ms=2300, rpm=1500))
        self.assertEqual(self.s.state, "idle")

    def test_engine_off_cancels(self):
        self.arm()
        self.s.update(Inputs(ms=2300, engine=False))
        self.assertEqual(self.s.state, "idle")

    def test_short_tap_rejected(self):
        self.arm()
        self.s.update(Inputs(ms=2300, throttle_pct=12))
        self.s.update(Inputs(ms=2320, throttle_pct=0))
        self.assertEqual(self.s.selected, 2)

    def test_long_press_rejected(self):
        self.arm()
        self.s.update(Inputs(ms=2300, throttle_pct=12))
        self.s.update(Inputs(ms=3100, throttle_pct=12))
        self.assertEqual(self.s.state, "idle")

    def test_restart_returns_to_default(self):
        self.arm()
        self.tap(2300)
        self.assertEqual(self.s.selected, 3)
        self.assertEqual(Selector().selected, 2)

    def test_indicator_not_engine_control(self):
        self.arm()
        self.s.update(Inputs(ms=2300, throttle_pct=12))
        self.s.update(Inputs(ms=2400, throttle_pct=0))
        self.assertEqual(self.s.indication, 3)
        self.assertFalse(hasattr(self.s, "engine_rpm_output"))
        self.assertFalse(hasattr(self.s, "can_output"))

    def test_clock_rollback_cancels(self):
        self.arm()
        self.s.update(Inputs(ms=1900))
        self.assertEqual(self.s.state, "idle")

if __name__ == "__main__":
    unittest.main()
