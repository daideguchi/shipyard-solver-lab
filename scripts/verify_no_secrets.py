from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [
    re.compile(r"AIza[0-9A-Za-z_\-]{20,}"),
    re.compile(r"-----BEGIN PRIVATE KEY-----"),
    re.compile(r"gho_[0-9A-Za-z_]{20,}"),
    re.compile(r"sk-[0-9A-Za-z_\-]{20,}"),
    re.compile(r"AQ\\.Ab8"),
]

SKIP_DIRS = {".git", "__pycache__"}
SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".mp4", ".webm"}

for path in ROOT.rglob("*"):
    if not path.is_file():
        continue
    if path.resolve() == Path(__file__).resolve():
        continue
    if any(part in SKIP_DIRS for part in path.parts):
        continue
    if path.suffix.lower() in SKIP_SUFFIXES:
        continue
    text = path.read_text(errors="ignore")
    for pattern in PATTERNS:
        if pattern.search(text):
            raise SystemExit(f"possible secret in {path.relative_to(ROOT)}")

print("shipyard_solver_no_secrets_ok")

