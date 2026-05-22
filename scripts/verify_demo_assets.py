import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIDEO = ROOT / "media" / "shipyard-solver-lab-demo-narrated.mp4"
THUMB = ROOT / "media" / "shipyard-solver-lab-demo-thumb.png"


def ffprobe(path: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


if not VIDEO.exists():
    raise SystemExit(f"missing demo video: {VIDEO.relative_to(ROOT)}")
if not THUMB.exists():
    raise SystemExit(f"missing demo thumbnail: {THUMB.relative_to(ROOT)}")

payload = ffprobe(VIDEO)
duration = float(payload["format"]["duration"])
size = int(payload["format"]["size"])
streams = {stream["codec_type"] for stream in payload["streams"]}

if not 90 <= duration <= 160:
    raise SystemExit(f"unexpected demo duration: {duration}")
if size < 1_000_000:
    raise SystemExit(f"demo video too small: {size}")
if not {"video", "audio", "subtitle"}.issubset(streams):
    raise SystemExit(f"expected video/audio/subtitle streams, got {streams}")
if THUMB.stat().st_size < 20_000:
    raise SystemExit(f"thumbnail too small: {THUMB.stat().st_size}")

print("shipyard_solver_demo_assets_ok")
print(f"duration={duration:.2f}")
print(f"size={size}")
print(f"streams={','.join(sorted(streams))}")
print(f"thumbnail={THUMB.relative_to(ROOT)}")
