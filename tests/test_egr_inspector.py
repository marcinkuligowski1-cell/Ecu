"""Only artificial firmware-like data: never contains original ECU data."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from egr_inspector import scan_16x13, scan_hysteresis_20, compare_map


def words(*values):
    return b''.join(int(v).to_bytes(2, 'little') for v in values)


def fixture(rpm_start=0, target=7000):
    rom = bytearray([0xC3]*2048)
    rpm = tuple(rpm_start + 250*i for i in range(16))
    load = tuple(200*i for i in range(13))
    desc = 128
    data = words(0xDD7C,16,*rpm,0xD904,13,*load,*([target]*208))
    rom[desc:desc+len(data)] = data
    return rom, desc, desc + 4 + 32 + 4 + 26


class EgrInspectorTests(unittest.TestCase):
    def test_finds_egr_shape(self):
        rom, start, values = fixture()
        xs = scan_16x13(rom)
        self.assertEqual(len(xs), 1)
        self.assertEqual(xs[0].descriptor,start)
        self.assertEqual(xs[0].data_offset,values)
        self.assertEqual(xs[0].kind,'egr_fresh_air_candidate')

    def test_distinguishes_n75_shape(self):
        rom, _, _ = fixture(rpm_start=750)
        self.assertEqual(scan_16x13(rom)[0].kind,'n75_duty_candidate')

    def test_distinguishes_uncertain_shape(self):
        rom, _, _ = fixture(rpm_start=250)
        self.assertEqual(scan_16x13(rom)[0].kind,'unknown_dd_d9')

    def test_rejects_wrong_axis_count(self):
        rom, s, _ = fixture()
        rom[s+2:s+4] = words(15)
        self.assertEqual(scan_16x13(rom),[])

    def test_rejects_nonmonotonic_axis(self):
        rom, s, _ = fixture()
        rom[s+4+2*5:s+4+2*6] = words(0)
        self.assertEqual(scan_16x13(rom),[])

    def test_rejects_out_of_bounds(self):
        rom, _, _ = fixture()
        self.assertEqual(scan_16x13(rom[:300]),[])

    def test_identity_unchanged(self):
        rom, _, _ = fixture()
        cand = scan_16x13(rom)[0]
        c = compare_map(rom,rom,cand)
        self.assertEqual((c.changed_bytes,c.changed_cells), (0,0))
        self.assertTrue(c.axes_unchanged)

    def test_uniform_destination(self):
        rom,_,off=fixture(target=7000)
        mod=bytearray(rom)
        mod[off:off+416]=words(*([8500]*208))
        c=compare_map(rom,mod,scan_16x13(rom)[0])
        self.assertEqual(c.changed_cells,208)
        self.assertEqual(c.modified_min,8500)
        self.assertEqual(c.modified_unique_values,1)

    def test_mixed_original_only_changed_cells(self):
        rom,_,off=fixture(target=8500)
        rom[off+2*20:off+2*21]=words(3000)
        mod=bytearray(rom)
        mod[off+2*20:off+2*21]=words(8500)
        c=compare_map(rom,mod,scan_16x13(rom)[0])
        self.assertEqual(c.changed_cells,1)
        self.assertGreater(c.changed_bytes,0)

    def test_axes_modified_reported(self):
        rom,s,_=fixture()
        mod=bytearray(rom)
        mod[s+4:s+6]=words(1)
        self.assertFalse(compare_map(rom,mod,scan_16x13(rom)[0]).axes_unchanged)

    def test_images_different_lengths_fail(self):
        rom,_,_=fixture()
        with self.assertRaises(ValueError):
            compare_map(rom,rom[:-1],scan_16x13(rom)[0])

    def test_invalid_scan_range(self):
        rom,_,_=fixture()
        with self.assertRaises(ValueError):
            scan_16x13(rom,start=100,end=3000)

    def test_hysteresis_detects_curve(self):
        rom=bytearray([0xC3]*1024)
        rom[128:128+84]=words(0xDD10,20,*range(200,4200,200),*([400]*20))
        r=scan_hysteresis_20(rom)
        self.assertEqual(len(r),1)
        self.assertEqual(r[0].shape,(20,1))

    def test_hysteresis_rejects_flat_axis(self):
        rom=bytearray([0xC3]*1024)
        rom[128:128+84]=words(0xDD10,20,*([200]*20),*([400]*20))
        self.assertEqual(scan_hysteresis_20(rom),[])

    def test_hysteresis_comparison(self):
        rom=bytearray([0xC3]*1024)
        rom[128:128+84]=words(0xDD10,20,*range(200,4200,200),*([400]*20))
        candidate=scan_hysteresis_20(rom)[0]
        mod=bytearray(rom);mod[candidate.data_offset:candidate.data_offset+2]=words(410)
        self.assertEqual(compare_map(rom,mod,candidate).changed_cells,1)

if __name__=='__main__': unittest.main()
