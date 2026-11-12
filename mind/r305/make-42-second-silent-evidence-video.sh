#!/usr/bin/env bash
# FV Mind R305: original silent 42-second evidence microfilm, no proprietary assets.
# Requires ffmpeg with drawtext/libx264. Input is only local text and installed font.
set -euo pipefail
out="mind-r305-42-second-evidence-check.mp4"
font="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
if [ ! -f "$font" ]; then echo "Required local font not available" >&2; exit 2; fi
temp="$(mktemp -d)"; trap 'rm -rf "$temp"' EXIT
printf '%s\n' "A question changed" "what witnesses reported." > "$temp/one"
printf '%s\n' "An audio promise" "still needs proof." > "$temp/two"
printf '%s\n' "Zen12 seller lists" "12 levels / 48 MP3s" > "$temp/three"
printf '%s\n' "The package is real." "The claimed outcome?" "Not established here." > "$temp/four"
printf '%s\n' "Try a free routine." "Check the actual terms." > "$temp/five"
# No audio; human-recorded narration is not implied. External captions/transcript are separate.
ffmpeg -hide_banner -loglevel error -y \
  -f lavfi -i "color=c=0x12343F:s=960x540:r=12:d=42" \
  -vf "drawbox=x=40:y=37:w=880:h=4:c=0xD9B67E:t=fill,\
drawbox=x=40:y=496:w=880:h=2:c=0x789A99:t=fill,\
drawtext=fontfile='$font':text='FINAL VESTIGE  /  EVIDENCE BEFORE OUTCOMES':x=44:y=455:fontsize=19:fontcolor=0xC2DAD4,\
drawtext=fontfile='$font':textfile='$temp/one':x=(w-text_w)/2:y=(h-text_h)/2:fontsize=48:line_spacing=19:fontcolor=0xFFF2D9:enable='between(t,0,7.99)',\
drawtext=fontfile='$font':textfile='$temp/two':x=(w-text_w)/2:y=(h-text_h)/2:fontsize=48:line_spacing=19:fontcolor=0xFFF2D9:enable='between(t,8,15.99)',\
drawtext=fontfile='$font':textfile='$temp/three':x=(w-text_w)/2:y=(h-text_h)/2:fontsize=46:line_spacing=18:fontcolor=0xFFF2D9:enable='between(t,16,23.99)',\
drawtext=fontfile='$font':textfile='$temp/four':x=(w-text_w)/2:y=(h-text_h)/2:fontsize=44:line_spacing=15:fontcolor=0xFFF2D9:enable='between(t,24,32.99)',\
drawtext=fontfile='$font':textfile='$temp/five':x=(w-text_w)/2:y=(h-text_h)/2:fontsize=48:line_spacing=19:fontcolor=0xFFF2D9:enable='between(t,33,42)'" \
  -c:v libx264 -preset slow -crf 25 -pix_fmt yuv420p -movflags +faststart -an -t 42 "$out"
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 "$out"
