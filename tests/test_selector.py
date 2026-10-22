"""Host-only tests; no firmware or actual sensor connections."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from selector import Inputs, Selector


class SelectorTests(unittest.TestCase):
    def setUp(self):
        self.s = Selector()

    def feed(self, t, **kw):
        self.s.update_with_reset(Inputs(ms=t, **kw))

    def arm(self):
        for t in range(0, 2001, 100):
            self.feed(t)
        self.assertEqual(self.s.state, "armed")

    def tap(self, t):
        self.feed(t, throttle_pct=12)
        self.feed(t + 100)
        self.feed(t + 200)
        self.feed(t + 300)

    def test_default_stage1(self):
        self.assertEqual(self.s.selected, 2)

    def test_cycles_per_press(self):
        self.arm()
        for t, expect in [(2100, 3), (2600, 1), (3100, 2)]:
            self.tap(t)
            self.assertEqual(self.s.selected, expect)

    def test_hold_no_repeat(self):
        self.arm()
        for t in (2100, 2200, 2300, 2400):
            self.feed(t, throttle_pct=12)
        self.assertEqual(self.s.selected, 2)

    def test_commit_on_release_only(self):
        self.arm()
        self.feed(2100, throttle_pct=12)
        self.assertEqual(self.s.selected, 2)
        self.feed(2200)
        self.assertEqual(self.s.selected, 3)

    def test_pedal_short_tap_cancel(self):
        self.arm()
        self.feed(2100, throttle_pct=12)
        self.feed(2120)
        self.assertEqual(self.s.selected, 2)
        self.assertEqual(self.s.state, "locked")

    def test_pedal_long_press_cancel(self):
        self.arm()
        for t in range(2100, 3001, 100):
            self.feed(t, throttle_pct=12)
        self.assertEqual(self.s.state, "locked")
        self.assertEqual(self.s.selected, 2)

    def test_high_throttle_cancels(self):
        self.arm()
        self.feed(2100, throttle_pct=30)
        self.assertEqual(self.s.state, "locked")

    def test_hill_start_cannot_rearm_without_releasing_brake_or_clutch(self):
        self.arm()
        self.feed(2100, throttle_pct=30)
        for t in range(2200, 4501, 100):
            self.feed(t)
        self.assertEqual(self.s.state, "locked")
        self.assertEqual(self.s.selected, 2)

    def test_manual_release_unlocks_but_not_arms(self):
        self.arm()
        self.feed(2100, throttle_pct=30)
        self.feed(2200, brake=False)
        self.assertEqual(self.s.state, "idle")
        self.feed(2300)
        self.assertEqual(self.s.state, "arming")

    def test_speed_above_zero_aborts(self):
        self.arm()
        self.feed(2100, throttle_pct=12)
        self.feed(2200, speed_kmh=0.1)
        self.assertEqual(self.s.state, "locked")
        self.assertEqual(self.s.selected, 2)

    def test_clutch_released(self):
        self.arm()
        self.feed(2100, clutch=False)
        self.assertEqual(self.s.state, "locked")

    def test_brake_released(self):
        self.arm()
        self.feed(2100, brake=False)
        self.assertEqual(self.s.state, "locked")

    def test_invalid_speed_sensor(self):
        self.arm()
        self.feed(2100, speed_valid=False)
        self.assertEqual(self.s.state, "locked")

    def test_invalid_clutch_sensor(self):
        self.arm()
        self.feed(2100, clutch_valid=False)
        self.assertEqual(self.s.state, "locked")

    def test_invalid_brake_sensor(self):
        self.arm()
        self.feed(2100, brake_valid=False)
        self.assertEqual(self.s.state, "locked")

    def test_invalid_rpm_sensor(self):
        self.arm()
        self.feed(2100, rpm_valid=False)
        self.assertEqual(self.s.state, "locked")

    def test_invalid_throttle_sensor(self):
        self.arm()
        self.feed(2100, throttle_valid=False)
        self.assertEqual(self.s.state, "locked")

    def test_nan_throttle(self):
        self.arm()
        self.feed(2100, throttle_pct=float("nan"))
        self.assertEqual(self.s.state, "locked")

    def test_infinite_speed(self):
        self.arm()
        self.feed(2100, speed_kmh=float("inf"))
        self.assertEqual(self.s.state, "locked")

    def test_negative_speed(self):
        self.arm()
        self.feed(2100, speed_kmh=-1)
        self.assertEqual(self.s.state, "locked")

    def test_spurious_boolean_rpm(self):
        self.arm()
        self.feed(2100, rpm=True)
        self.assertEqual(self.s.state, "locked")

    def test_rpm_change_cancels(self):
        self.arm()
        self.feed(2100, rpm=1400)
        self.assertEqual(self.s.state, "locked")

    def test_engine_off_cancels(self):
        self.arm()
        self.feed(2100, engine=False)
        self.assertEqual(self.s.state, "locked")

    def test_duplicate_timestamp_cancels(self):
        self.arm()
        self.feed(2000)
        self.assertEqual(self.s.state, "locked")

    def test_timestamp_rollback_cancels(self):
        self.arm()
        self.feed(1900)
        self.assertEqual(self.s.state, "locked")

    def test_stale_sample_cancels(self):
        self.arm()
        self.feed(2400)
        self.assertEqual(self.s.state, "locked")

    def test_press_requires_arm(self):
        self.feed(0, throttle_pct=12)
        self.assertNotEqual(self.s.state, "armed")
        self.assertEqual(self.s.selected, 2)

    def test_restart_defaults_stage1(self):
        self.arm()
        self.tap(2100)
        self.assertEqual(self.s.selected, 3)
        self.assertEqual(Selector().selected, 2)

    def test_indicator_only_reports_index(self):
        self.arm()
        self.feed(2100, throttle_pct=12)
        self.feed(2200)
        self.assertEqual(self.s.indication, 3)
        self.assertFalse(hasattr(self.s, "rpm_output"))
        self.assertFalse(hasattr(self.s, "can_output"))
        self.assertFalse(hasattr(self.s, "torque_output"))

    def test_multiple_updates_do_not_repeat_indicator(self):
        self.arm()
        self.feed(2100, throttle_pct=12)
        self.feed(2200)
        self.assertEqual(self.s.indication, 3)
        self.feed(2300)
        self.assertIsNone(self.s.indication)

    def test_release_guard_blocks_bounce(self):
        self.arm()
        self.feed(2100, throttle_pct=12)
        self.feed(2200)
        self.feed(2250, throttle_pct=12)
        self.assertEqual(self.s.selected, 3)
        self.assertEqual(self.s.state, "locked")


if __name__ == "__main__":
    unittest.main()
