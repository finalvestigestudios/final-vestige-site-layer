#!/usr/bin/env bash
# FV Mind R415 original silent 42s micro-film; no paid SaaS or external media.
set -euo pipefail
cd "$(dirname "$0")"
command -v ffmpeg >/dev/null || { echo "ffmpeg required" >&2; exit 2; }
out=mindwandering_42s.mp4
filter="drawtext=font='DejaVu Sans':text='YOUR EYES MOVE DOWN THE PAGE':x=(w-text_w)/2:y=145:fontsize=23:fontcolor=0xF2D9A1:enable='between(t,0,6.999)',\
drawtext=font='DejaVu Sans':text='A DIFFERENT THOUGHT ENTERS':x=(w-text_w)/2:y=145:fontsize=23:fontcolor=0xF2D9A1:enable='between(t,7,13.999)',\
drawtext=font='DejaVu Sans':text='THE LINES KEEP PASSING':x=(w-text_w)/2:y=145:fontsize=23:fontcolor=0xF2D9A1:enable='between(t,14,20.999)',\
drawtext=font='DejaVu Sans':text='WHAT DID I JUST READ?':x=(w-text_w)/2:y=145:fontsize=23:fontcolor=0xF2D9A1:enable='between(t,21,27.999)',\
drawtext=font='DejaVu Sans':text='NOTICE. THEN RETURN.':x=(w-text_w)/2:y=145:fontsize=23:fontcolor=0xF2D9A1:enable='between(t,28,34.999)',\
drawtext=font='DejaVu Sans':text='AN EXPERIMENT, NOT A MIRACLE':x=(w-text_w)/2:y=145:fontsize=21:fontcolor=0xF2D9A1:enable='gte(t,35)',\
drawtext=font='DejaVu Sans':text='FINAL VESTIGE  /  MIND AND PERCEPTION':x=(w-text_w)/2:y=295:fontsize=13:fontcolor=0xA8B7B8"
ffmpeg -hide_banner -loglevel error -y -f lavfi -i "color=c=0x142029:s=640x360:r=2:d=42" -vf "$filter" -an -c:v libx264 -preset slow -crf 34 -pix_fmt yuv420p -movflags +faststart -t 42 "$out"
ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height -show_entries format=duration,size -of default=noprint_wrappers=1 "$out"
printf 'Original offline silent video generated: %s\n' "$out"
