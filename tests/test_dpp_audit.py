"""Artificial data only. Tests do not prove executable ECU safety."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dpp_audit import (PAGE_BYTES, MAX_CPU, DppCandidate, cpu_data_address,
                       flash_relative, find_dpp_immediate_shapes, changed_dpp_indices,
                       reject_unreviewed_dpp_changes)


class DppAuditTests(unittest.TestCase):
    def setUp(self):
        self.dpps = (0x28, 0x29, 0x12, 0x03)

    def test_pages_are_16k(self):
        self.assertEqual(PAGE_BYTES, 16384)

    def test_dpp0_base(self):
        self.assertEqual(cpu_data_address(0, self.dpps), 0xA0000)

    def test_dpp1_base(self):
        self.assertEqual(cpu_data_address(0x4000, self.dpps), 0xA4000)

    def test_dpp2_base_differs_from_generic_multimap_example(self):
        self.assertEqual(cpu_data_address(0x8000, self.dpps), 0x48000)

    def test_dpp3_base(self):
        self.assertEqual(cpu_data_address(0xC000, self.dpps), 0xC000)

    def test_page_boundary(self):
        self.assertEqual(cpu_data_address(0x3FFF, self.dpps), 0xA3FFF)
        self.assertEqual(cpu_data_address(0x4000, self.dpps), 0xA4000)

    def test_logical_offset_preserved(self):
        self.assertEqual(cpu_data_address(0x8234, self.dpps), 0x48234)

    def test_max_physical_memory(self):
        self.assertEqual(MAX_CPU, 0x1000000)

    def test_bad_logical_address(self):
        with self.assertRaises(ValueError):
            cpu_data_address(0x10000, self.dpps)

    def test_bad_page(self):
        with self.assertRaises(ValueError):
            cpu_data_address(0, (0x400, 0, 0, 0))

    def test_wrong_page_tuple(self):
        with self.assertRaises(ValueError):
            cpu_data_address(0, (0, 0, 0))

    def test_flash_relative_assumed_base(self):
        self.assertEqual(flash_relative(0xA0000, 0x40000, 0x80000), 0x60000)

    def test_dpp2_assumed_flash_offset(self):
        self.assertEqual(flash_relative(cpu_data_address(0x8000, self.dpps), 0x40000, 0x80000), 0x8000)

    def test_unmapped_region(self):
        self.assertIsNone(flash_relative(0x8000, 0x40000, 0x80000))

    def test_last_flash_byte(self):
        self.assertEqual(flash_relative(0xBFFFF, 0x40000, 0x80000), 0x7FFFF)

    def test_exact_end_not_part_of_flash(self):
        self.assertIsNone(flash_relative(0xC0000, 0x40000, 0x80000))

    def test_find_aligned_shape(self):
        blob = bytes.fromhex("c3 c3 e6 00 28 00 e6 02 12 00 c3 c3")
        self.assertEqual(find_dpp_immediate_shapes(blob), [DppCandidate(2, 0, 40), DppCandidate(6, 2, 18)])

    def test_unaligned_shape_not_called_candidate(self):
        blob = bytes.fromhex("c3 e6 00 28 00 c3 c3 c3")
        self.assertEqual(find_dpp_immediate_shapes(blob), [])

    def test_range_filter(self):
        blob = bytes.fromhex("e6 00 28 00 e6 02 12 00")
        self.assertEqual(find_dpp_immediate_shapes(blob, code_ranges=((4, 8),)), [DppCandidate(4, 2, 18)])

    def test_bad_range(self):
        with self.assertRaises(ValueError):
            find_dpp_immediate_shapes(b"\0" * 8, code_ranges=((1, 8),))

    def test_invalid_out_of_range_page_excluded(self):
        self.assertEqual(find_dpp_immediate_shapes(bytes.fromhex("e6 00 ff 7f")), [])

    def test_unknown_opcode_excluded(self):
        self.assertEqual(find_dpp_immediate_shapes(bytes.fromhex("a6 00 3c 00")), [])

    def test_guard_reject_unreviewed_dpp2(self):
        with self.assertRaises(ValueError):
            reject_unreviewed_dpp_changes(self.dpps, (0x24, 0x25, 0x26, 3), {0, 1})

    def test_guard_allows_only_reviewed(self):
        reject_unreviewed_dpp_changes(self.dpps, (0x24, 0x25, 0x12, 3), {0, 1})

    def test_change_indices(self):
        self.assertEqual(changed_dpp_indices(self.dpps, (0x24, 0x25, 0x12, 3)), (0, 1))

    def test_no_mutation(self):
        self.assertEqual(changed_dpp_indices(self.dpps, self.dpps), ())


if __name__ == "__main__":
    unittest.main()
