"""All bank tests operate exclusively on invented, artificial byte arrays."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from bank_layout import BankPlan,build_scaffold

SZ=0xC000
SRC=0x20000
A=SRC-2*SZ
B=SRC-SZ


def fixtures():
    stock=bytearray([0xC3]*(SRC+SZ+0x2000))
    stock[SRC:SRC+SZ]=b'Q'*SZ
    tuned=bytearray(stock)
    tuned[SRC+100:SRC+200]=b'Z'*100
    return stock,tuned,BankPlan(SRC,SZ,A,B)


class BankTests(unittest.TestCase):
    def test_three_banks(self):
        s,t,p=fixtures()
        img,a=build_scaffold(s,t,p)
        self.assertEqual(img[A:A+SZ],s[SRC:SRC+SZ])
        self.assertEqual(img[B:B+SZ],t[SRC:SRC+SZ])
        self.assertEqual(img[SRC:SRC+SZ],t[SRC:SRC+SZ])

    def test_preserves_unrelated_prefix(self):
        s,t,p=fixtures();s[A-5:A-1]=b'abcd';t[A-5:A-1]=b'abcd'
        img,_=build_scaffold(s,t,p)
        self.assertEqual(img[A-5:A-1],b'abcd')

    def test_preserves_executable_tail(self):
        s,t,p=fixtures();s[SRC+SZ+10:SRC+SZ+13]=b'XYZ';t[SRC+SZ+10:SRC+SZ+13]=b'XYZ'
        img,_=build_scaffold(s,t,p)
        self.assertEqual(img[SRC+SZ+10:SRC+SZ+13],b'XYZ')

    def test_reports_not_flashable(self):
        s,t,p=fixtures();_,audit=build_scaffold(s,t,p)
        self.assertFalse(audit.flashable)
        self.assertFalse(audit.checksum_verified)

    def test_audit_sha256(self):
        s,t,p=fixtures();_,audit=build_scaffold(s,t,p)
        self.assertEqual(len(audit.stock_sha256),64)
        self.assertEqual(len(audit.tuned_sha256),64)
        self.assertEqual(len(audit.image_sha256),64)

    def test_disallows_collision(self):
        s,t,p=fixtures();s[A+50]=0x12;t[A+50]=0x12
        with self.assertRaises(ValueError):build_scaffold(s,t,p)

    def test_disallows_mismatch_outside_calibration(self):
        s,t,p=fixtures();t[10]=0x25
        with self.assertRaises(ValueError):build_scaffold(s,t,p)

    def test_disallows_overlapping_banks(self):
        s,t,p=fixtures()
        with self.assertRaises(ValueError):build_scaffold(s,t,BankPlan(SRC,SZ,SRC-2*SZ,SRC))

    def test_disallows_misaligned_banks(self):
        s,t,p=fixtures()
        with self.assertRaises(ValueError):build_scaffold(s,t,BankPlan(SRC,SZ,A+2,B))

    def test_disallows_bad_bounds(self):
        s,t,p=fixtures()
        with self.assertRaises(ValueError):build_scaffold(s,t,BankPlan(SRC+SZ,SZ,A,B))

    def test_disallows_bad_fill_byte(self):
        s,t,p=fixtures()
        with self.assertRaises(ValueError):build_scaffold(s,t,BankPlan(SRC,SZ,A,B,999))

    def test_determinism(self):
        s,t,p=fixtures();a,_=build_scaffold(s,t,p);b,_=build_scaffold(s,t,p)
        self.assertEqual(a,b)

if __name__=='__main__':unittest.main()
