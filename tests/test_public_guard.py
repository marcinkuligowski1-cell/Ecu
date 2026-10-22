"""Offline tests for the public repository guard."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from check_public_tree import scan


class PublicGuardTests(unittest.TestCase):
    def test_public_text_accepted(self):
        with tempfile.TemporaryDirectory() as temp:
            (Path(temp) / "README.md").write_text("Public research repository\n")
            self.assertEqual(scan(Path(temp)), [])

    def test_unlisted_file_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            (Path(temp) / "dump.bin").write_bytes(b"some fake bytes")
            self.assertTrue(scan(Path(temp)))

    def test_private_key_marker_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            (Path(temp) / "README.md").write_text("-----BEGIN " + "PRIVATE KEY-----")
            self.assertTrue(scan(Path(temp)))

    def test_oversized_file_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            (Path(temp) / "README.md").write_text("x" * 100001)
            self.assertTrue(scan(Path(temp)))


if __name__ == "__main__":
    unittest.main()
