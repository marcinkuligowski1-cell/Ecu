"""Fabricated V4.1 blocks only; no private ECU calibration data."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from calibration_checksum import (
    BLOCK_LEN, V41_MARKER, calculate_correction,
    inspect_block, rewrite_correction_fields,
)


def fake_block():
    payload = bytearray([0xC3] * BLOCK_LEN)
    payload[1:12] = V41_MARKER
    return bytes(payload)


class ChecksumTests(unittest.TestCase):
    def test_independent_synthetic_check_vector_first_region(self):
        self.assertEqual(calculate_correction(fake_block()[:0xB7C]), 0x160C9E64)

    def test_independent_synthetic_check_vector_second_region(self):
        self.assertEqual(calculate_correction(fake_block()[0xB80:0xBFFC]), 0xC8CB9321)

    def test_fixes_both_fields_on_copy(self):
        img = rewrite_correction_fields(fake_block())
        self.assertTrue(all(x.match for x in inspect_block(img)))

    def test_does_not_mutate_original(self):
        original = fake_block()
        restored = rewrite_correction_fields(original)
        self.assertNotEqual(original, restored)
        self.assertEqual(original[0xB7C:0xB80], b"\xC3" * 4)

    def test_idempotent(self):
        img = rewrite_correction_fields(fake_block())
        self.assertEqual(rewrite_correction_fields(img), img)

    def test_first_region_corruption_detected(self):
        img = bytearray(rewrite_correction_fields(fake_block()))
        img[100] ^= 0x10
        self.assertFalse(inspect_block(img)[0].match)
        self.assertTrue(inspect_block(img)[1].match)

    def test_second_region_corruption_detected(self):
        img = bytearray(rewrite_correction_fields(fake_block()))
        img[0x4100] ^= 0x20
        self.assertTrue(inspect_block(img)[0].match)
        self.assertFalse(inspect_block(img)[1].match)

    def test_rewrite_only_two_checksum_fields(self):
        original = fake_block()
        updated = rewrite_correction_fields(original)
        assert len(updated) == len(original)
        self.assertTrue(all(i in list(range(0xB7C, 0xB80)) + list(range(0xBFFC, 0xC000))
                            for i, (a, b) in enumerate(zip(original, updated)) if a != b))

    def test_wrong_block_length_rejected(self):
        with self.assertRaises(ValueError):
            inspect_block(fake_block()[:-1])

    def test_unrecognized_header_rejected(self):
        broken = bytearray(fake_block())
        broken[1] ^= 0x01
        with self.assertRaises(ValueError):
            rewrite_correction_fields(broken)

    def test_not_multiple_of_four_rejected(self):
        with self.assertRaises(ValueError):
            calculate_correction(b"123")

    def test_correction_field_is_not_truncated(self):
        updated = rewrite_correction_fields(fake_block())
        self.assertEqual(int.from_bytes(updated[0xB7C:0xB80], "little"), 0x160C9E64)
        self.assertEqual(int.from_bytes(updated[0xBFFC:0xC000], "little"), 0xC8CB9321)


if __name__ == "__main__":
    unittest.main()
