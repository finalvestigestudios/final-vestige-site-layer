#!/usr/bin/env bash
# Original source-controlled 42-second silent review-film builder; no remote assets, trackers or paid tools.
# Reproduce: bash build_original_42s.sh [output.mp4]
set -euo pipefail
command -v ffmpeg >/dev/null || { echo "ffmpeg not installed" >&2; exit 2; }
OUT="${1:-ZEN12_42S_REVIEW.mp4}"
FONT="${FV_FILM_FONT:-/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf}"
test -r "$FONT" || { echo "Set FV_FILM_FONT to a readable licensed local TTF; no fonts bundled" >&2; exit 3; }
# Six seven-second beats. Captions and full transcript remain separate accessible files.
# This is an editorial motion graphic, NOT a laboratory trial, seller product demonstration or promised efficacy.
VF="drawtext=fontfile=$FONT:text='FINAL VESTIGE  /  MIND & PERCEPTION':fontsize=23:fontcolor=0xdcb875:x=(w-text_w)/2:y=88,"
VF+="drawtext=fontfile=$FONT:text='ILLUSTRATION ONLY  -  NO EXPERIMENTAL DATA':fontsize=20:fontcolor=0xc9c0b3:x=(w-text_w)/2:y=600,"
VF+="drawtext=fontfile=$FONT:text='ONE TARGET FOUND':fontsize=66:fontcolor=0xf3ecdf:x=(w-text_w)/2:y=260:enable='between(t,0,6.999)',"
VF+="drawtext=fontfile=$FONT:text='THE SECOND IS MISSED':fontsize=38:fontcolor=0xdcb875:x=(w-text_w)/2:y=370:enable='between(t,0,6.999)',"
VF+="drawtext=fontfile=$FONT:text='ATTENTIONAL BLINK':fontsize=65:fontcolor=0xf3ecdf:x=(w-text_w)/2:y=260:enable='between(t,7,13.999)',"
VF+="drawtext=fontfile=$FONT:text='NOT AN EYE BLINK':fontsize=38:fontcolor=0xdcb875:x=(w-text_w)/2:y=370:enable='between(t,7,13.999)',"
VF+="drawtext=fontfile=$FONT:text='THREE MONTHS':fontsize=68:fontcolor=0xf3ecdf:x=(w-text_w)/2:y=260:enable='between(t,14,20.999)',"
VF+="drawtext=fontfile=$FONT:text='INTENSIVE MENTAL TRAINING':fontsize=35:fontcolor=0xdcb875:x=(w-text_w)/2:y=370:enable='between(t,14,20.999)',"
VF+="drawtext=fontfile=$FONT:text='NOT A ZEN12 TRIAL':fontsize=62:fontcolor=0xf3ecdf:x=(w-text_w)/2:y=260:enable='between(t,21,27.999)',"
VF+="drawtext=fontfile=$FONT:text='NO VERIFIED HOUR EQUIVALENCE':fontsize=35:fontcolor=0xdcb875:x=(w-text_w)/2:y=370:enable='between(t,21,27.999)',"
VF+="drawtext=fontfile=$FONT:text='CHECK THE ACTUAL OFFER':fontsize=56:fontcolor=0xf3ecdf:x=(w-text_w)/2:y=260:enable='between(t,28,34.999)',"
VF+="drawtext=fontfile=$FONT:text='FILES  /  EVIDENCE  /  RETURNS':fontsize=34:fontcolor=0xdcb875:x=(w-text_w)/2:y=370:enable='between(t,28,34.999)',"
VF+="drawtext=fontfile=$FONT:text='TRY A FREE ROUTINE':fontsize=62:fontcolor=0xf3ecdf:x=(w-text_w)/2:y=260:enable='between(t,35,42)',"
VF+="drawtext=fontfile=$FONT:text='DECIDE FOR YOURSELF':fontsize=38:fontcolor=0xdcb875:x=(w-text_w)/2:y=370:enable='between(t,35,42)'"
ffmpeg -hide_banner -loglevel error -y -f lavfi -i "color=c=0x10161c:s=1280x720:r=24:d=42" -vf "$VF" -c:v libx264 -preset veryfast -crf 32 -pix_fmt yuv420p -movflags +faststart -an "$OUT"
echo "Produced review-only original 42-second silent clip: $OUT"
echo "Check duration with ffprobe; attach ZEN12_42S_CAPTIONS.vtt and show transcript if video is later approved for staging."
