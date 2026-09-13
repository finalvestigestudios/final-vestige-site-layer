#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
A="$HERE/assets"
mkdir -p "$A"
# Human-like synthetic speech only for pipeline validation; not a production narrator.
ffmpeg -y -hide_banner -loglevel error -f lavfi -i "flite=text='On March eighteenth, nineteen thirty seven, the investigator arrived.':voice=slt" -ar 48000 -ac 2 "$A/voice1.wav"
ffmpeg -y -hide_banner -loglevel error -f lavfi -i "flite=text='A leak. A spark. A simple chain of events.':voice=slt" -ar 48000 -ac 2 "$A/voice2.wav"
ffmpeg -y -hide_banner -loglevel error -f lavfi -i "flite=text='But the evidence would only let them say one thing for certain.':voice=slt" -ar 48000 -ac 2 "$A/voice3.wav"
# Low documentary bed: quiet low tone + filtered noise.
ffmpeg -y -hide_banner -loglevel error -f lavfi -i "sine=frequency=92:duration=12:sample_rate=48000" -f lavfi -i "anoisesrc=color=pink:duration=12:sample_rate=48000:amplitude=0.035" -filter_complex "[0:a]volume=0.08[a];[1:a]lowpass=f=900,volume=0.25[b];[a][b]amix=inputs=2:normalize=0" -ac 2 "$A/music.wav"
# Short clearly audible page/mechanical-like cue for layer verification.
ffmpeg -y -hide_banner -loglevel error -f lavfi -i "anoisesrc=color=white:duration=0.28:sample_rate=48000:amplitude=0.25" -af "highpass=f=1200,lowpass=f=6500,afade=t=out:st=0.08:d=0.20" -ac 2 "$A/sfx.wav"
