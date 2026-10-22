"""Conservative public-file policy; manual review remains necessary."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BLOCK_SUFFIXES = {".bin", ".eep", ".eeprom", ".hex", ".rom", ".romdata", ".zip", ".7z", ".rar", ".key", ".pem", ".p12"}
BLOCK_NAMES = {".env", "id_rsa", "id_ed25519"}
problems = []
for p in ROOT.rglob("*"):
    if not p.is_file() or ".git" in p.parts or "__pycache__" in p.parts:
        continue
    if p.suffix.lower() in BLOCK_SUFFIXES or p.name.lower() in BLOCK_NAMES:
        problems.append(str(p.relative_to(ROOT)))
if problems:
    raise SystemExit("Blocked files: " + ", ".join(problems))
print("OK: no blocked firmware/archive/secret filenames")
