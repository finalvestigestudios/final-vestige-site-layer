#!/usr/bin/env bash
set -euo pipefail
OUT="${1:-zen12_source_before_claim_42s.mp4}"
# Original soundless editorial sequence, not evidence of meditation efficacy.
# Requires FFmpeg with libx264 and drawtext. Reproduces a self-contained 42-second MP4.
ffmpeg -hide_banner -loglevel error -y -f lavfi -i 'color=c=0x0d1311:s=960x540:r=24:d=42' \
-vf "drawbox=x=68:y=146:w=616:h=208:color=0x30291c:t=fill:enable='between(t,0,14)',drawbox=x=68:y=146:w=616:h=208:color=0x1b302e:t=fill:enable='between(t,14,28)',drawbox=x=68:y=146:w=616:h=208:color=0x30301f:t=fill:enable='between(t,28,42)',drawtext=text='THE CLAIM':fontcolor=0xf4efe6:fontsize=62:x=100:y=180:enable='between(t,0,14)',drawtext=text='is not the result':fontcolor=0xe0c392:fontsize=35:x=100:y=270:enable='between(t,0,14)',drawtext=text='THE COMPARISON':fontcolor=0xf4efe6:fontsize=52:x=100:y=180:enable='between(t,14,28)',drawtext=text='asks what changed':fontcolor=0xe0c392:fontsize=35:x=100:y=270:enable='between(t,14,28)',drawtext=text='YOUR CHOICE':fontcolor=0xf4efe6:fontsize=62:x=100:y=180:enable='between(t,28,42)',drawtext=text='starts with evidence':fontcolor=0xe0c392:fontsize=35:x=100:y=270:enable='between(t,28,42)',drawtext=text='FINAL VESTIGE / SOURCE BEFORE CLAIM':fontcolor=0xb8955e:fontsize=23:x=68:y=460" \
-an -c:v libx264 -profile:v baseline -pix_fmt yuv420p -preset veryfast -crf 31 -movflags +faststart "$OUT"
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 "$OUT"
