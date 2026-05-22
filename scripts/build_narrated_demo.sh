#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ "${SKIP_RECORD:-0}" != "1" ]]; then
  npm run demo:record
fi

say -v Samantha -r 145 -f submission/demo-narration.txt -o media/demo-narration.aiff
ffmpeg -y -i media/demo-narration.aiff -ar 48000 -ac 2 media/demo-narration.wav >/tmp/shipyard_demo_audio.log 2>&1

ffmpeg -y \
  -i media/shipyard-solver-lab-demo.webm \
  -i media/demo-narration.wav \
  -i submission/demo-subtitles.srt \
  -filter:v "tpad=stop_mode=clone:stop_duration=8" \
  -map 0:v:0 \
  -map 1:a:0 \
  -map 2:s:0 \
  -c:v libx264 \
  -pix_fmt yuv420p \
  -preset veryfast \
  -crf 23 \
  -c:a aac \
  -b:a 160k \
  -c:s mov_text \
  -metadata:s:s:0 language=eng \
  -shortest \
  media/shipyard-solver-lab-demo-narrated.mp4

ffmpeg -y -ss 00:00:18 -i media/shipyard-solver-lab-demo-narrated.mp4 -frames:v 1 -q:v 3 media/shipyard-solver-lab-demo-thumb.png >/tmp/shipyard_demo_thumb.log 2>&1

rm -f media/demo-narration.aiff media/demo-narration.wav

echo "shipyard_solver_narrated_demo_ok"
echo "video=media/shipyard-solver-lab-demo-narrated.mp4"
echo "thumbnail=media/shipyard-solver-lab-demo-thumb.png"
