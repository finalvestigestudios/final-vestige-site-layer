#!/usr/bin/env bash
# Reproducible, rights-original, silent 42-second educational video proof.
# Requires ffmpeg with libx264, drawtext, and DejaVu Sans.
# Usage: bash build_zen12_film.sh [output_file.mp4]
set -euo pipefail
OUT="${1:-zen12_42s_original_silent.mp4}"
FONT="${FV_FONT:-/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf}"
test -f "$FONT" || { echo "Missing FV_FONT" >&2; exit 4; }
TEXT=("YOUR EYES SEE ONE HAND" "YOUR SKIN FEELS ANOTHER" "MATCH THE TIMING" "OWNERSHIP CAN FEEL UNCERTAIN" "A REPORT IS EVIDENCE" "NOT EVERY CLAIMED CAUSE" "FORMAT IS NOT EFFICACY" "A SHORT RECORDING IS A FORMAT" "TRY A FREE BASELINE" "TWELVE MINUTES ONE TASK" "CHOOSE WITH EVIDENCE" "FINAL VESTIGE MIND ARCHIVE")
FILTER="drawbox=x=32:y=32:w=896:h=476:color=0xBA9A61:t=2,"
FILTER+="drawtext=fontfile=$FONT:text='FINAL VESTIGE   /   THE MIND ARCHIVE':fontcolor=0xE7CF9A:fontsize=22:x=75:y=72,"
for i in {0..5}; do
  s=$((i*7)); e=$((s+7)); a=$((i*2)); b=$((a+1))
  FILTER+="drawtext=fontfile=$FONT:text='${TEXT[$a]}':fontcolor=0xF4F0E8:fontsize=40:x=75:y=200:enable='between(t,$s,$e)',"
  FILTER+="drawtext=fontfile=$FONT:text='${TEXT[$b]}':fontcolor=0xD7C8AC:fontsize=27:x=75:y=283:enable='between(t,$s,$e)',"
done
FILTER+="drawtext=fontfile=$FONT:text='NO PRODUCT OR HEALTH OUTCOME IS PROMISED':fontcolor=0xD1C8B5:fontsize=16:x=75:y=453"
ffmpeg -hide_banner -loglevel error -y -f lavfi -i "color=c=0x152D35:s=960x540:r=24:d=42" \
  -vf "$FILTER" -an -c:v libx264 -preset veryfast -crf 27 \
  -pix_fmt yuv420p -movflags +faststart -t 42 "$OUT"
ffprobe -v error -show_entries format=duration -of default=nw=1 "$OUT"
echo "Video has NO AUDIO. Provide VTT captions and the full transcript when embedding."
