"""Synthetic firmware-like byte streams only, no private data in test fixtures."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / 'src'))
from calibration_inspector import (speed_axis_encoding, find_enabled_lc,
    find_disabled_lc, compare_launch_control, nonfill_offsets, dpp_immediate_candidates)

class CalibrationInspectorTests(unittest.TestCase):
    def setUp(self):
        self.original=bytearray([0xC3]*8192)
        self.sig=1000
        self.original[self.sig:self.sig+16]=bytes.fromhex('AB CD 02 00 80 00 00 0A 99 88 02 00 00 00 70 17')
        self.changed=bytearray(self.original)
        self.changed[self.sig+2:self.sig+32]=speed_axis_encoding()

    def test_lc_axis_30_bytes(self):
        self.assertEqual(len(speed_axis_encoding()),30)
    def test_source_disabled_found(self):
        found=find_disabled_lc(self.original)
        self.assertEqual(len(found),1)
        self.assertEqual(found[0].signature_offset,self.sig)
    def test_target_enabled_found(self):
        found=find_enabled_lc(self.changed)
        self.assertEqual(len(found),1)
        self.assertEqual(found[0].axis_header_offset,self.sig+2)
        self.assertEqual(found[0].map_offset,self.sig+86)
    def test_no_false_active_in_original(self):
        self.assertEqual(find_enabled_lc(self.original),[])
    def test_change_detected(self):
        found=compare_launch_control(self.original,self.changed)
        self.assertEqual(len(found),1)
        self.assertGreater(found[0].axis_changed_bytes,0)
        self.assertTrue(found[0].map_700_bytes_unchanged)
    def test_detect_data_change_inside_map(self):
        self.changed[self.sig+86+4]=0x00
        found=compare_launch_control(self.original,self.changed)
        self.assertFalse(found[0].map_700_bytes_unchanged)
    def test_mismatched_length_refused(self):
        with self.assertRaises(ValueError):
            compare_launch_control(self.original,self.changed[:-1])
    def test_truncated_map_is_not_reported(self):
        shortened=self.changed[:self.sig+86+699]
        self.assertEqual(find_enabled_lc(shortened),[])
    def test_empty_binary(self):
        self.assertEqual(find_enabled_lc(b''),[])
        self.assertEqual(find_disabled_lc(b''),[])
    def test_reserved_data_collision(self):
        self.original[500:503]=b'ABC'
        self.assertEqual(nonfill_offsets(self.original,499,5),[500,501,502])
    def test_reserved_data_clear_region(self):
        self.assertEqual(nonfill_offsets(self.original,200,100),[])
    def test_reserved_bad_range_rejected(self):
        with self.assertRaises(ValueError): nonfill_offsets(self.original,8190,5)
    def test_dpp_candidates_aligned(self):
        self.original[200:204]=bytes.fromhex('E6 00 3C 00')
        self.original[301:305]=bytes.fromhex('E6 00 3C 00')
        self.assertIn(200,dpp_immediate_candidates(self.original,0x3C))
        self.assertNotIn(301,dpp_immediate_candidates(self.original,0x3C))
    def test_dpp_other_register_not_found(self):
        self.original[200:204]=bytes.fromhex('E6 00 3C 00')
        self.assertNotIn(200,dpp_immediate_candidates(self.original,0x3C,1))
    def test_lc_pattern_offset_not_copied(self):
        candidate=compare_launch_control(self.original,self.changed)[0]
        self.assertGreater(candidate.map_offset,candidate.axis_offset)

if __name__=='__main__':unittest.main()
