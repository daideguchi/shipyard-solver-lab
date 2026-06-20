import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs"
SOURCE = ROOT / "official_submission" / "myalgorithm.py"
ZIP_PATH = OUTPUT_DIR / "official_submission_candidate.zip"
MANIFEST_PATH = OUTPUT_DIR / "official_submission_manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"missing candidate algorithm: {SOURCE}")

    OUTPUT_DIR.mkdir(exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(SOURCE, arcname="myalgorithm.py")

    manifest = {
        "boundary": "candidate package for official OGC platform readiness; send only through an allowed official OGC window",
        "zip_path": str(ZIP_PATH.relative_to(ROOT)),
        "zip_size_bytes": ZIP_PATH.stat().st_size,
        "zip_sha256": sha256(ZIP_PATH),
        "files": [
            {
                "archive_path": "myalgorithm.py",
                "source_path": str(SOURCE.relative_to(ROOT)),
                "source_sha256": sha256(SOURCE),
            }
        ],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("official_submission_package_ok")
    print(f"zip={ZIP_PATH.relative_to(ROOT)}")
    print(f"zip_size_bytes={manifest['zip_size_bytes']}")
    print(f"zip_sha256={manifest['zip_sha256']}")
    print(f"manifest={MANIFEST_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
