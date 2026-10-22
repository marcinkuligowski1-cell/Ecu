"""Conservative public repository allowlist: manual review still required."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {
    "README.md", "SECURITY.md", ".gitignore", ".github/workflows/tests.yml",
    "docs/PROGRESS.md", "docs/SAFETY_CASE.md", "src/selector.py",
    "tests/test_selector.py", "tests/test_public_guard.py",
    "src/calibration_inspector.py", "tests/test_calibration_inspector.py",
    "docs/CALIBRATION_RESEARCH.md",
    "tools/check_public_tree.py",
}
DENIED_EXTENSIONS = {".bin", ".eep", ".eeprom", ".hex", ".rom", ".romdata",
                     ".zip", ".rar", ".7z", ".pem", ".p12", ".key", ".pdf"}
DENIED_NAMES = {".env", "id_rsa", "id_ed25519"}
MAX_BYTES = 100_000
MARKERS = [
    ("possible vehicle VIN", re.compile(r"\b[A-HJ-NPR-Z0-9]{17}\b")),
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}")),
]


def scan(root: Path = ROOT):
    issues = []
    for path in root.rglob("*"):
        if not path.is_file() or ".git" in path.relative_to(root).parts or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(root).as_posix()
        if relative not in ALLOWED:
            issues.append((relative, "file not in explicit public allowlist"))
            continue
        if path.suffix.lower() in DENIED_EXTENSIONS or path.name.lower() in DENIED_NAMES:
            issues.append((relative, "blocked file type"))
            continue
        if path.stat().st_size > MAX_BYTES:
            issues.append((relative, "unexpectedly large file"))
            continue
        if relative == "tools/check_public_tree.py":
            continue  # Own regex source is self-matching; manual review mandatory.
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            issues.append((relative, "not UTF-8 text"))
            continue
        for description, pattern in MARKERS:
            if pattern.search(content):
                issues.append((relative, description))
    return issues


if __name__ == "__main__":
    found = scan()
    if found:
        for filename, reason in found:
            print(f"BLOCK: {filename} ({reason})")
        raise SystemExit(1)
    print("OK: public repository allowlist and basic leak check passed")
