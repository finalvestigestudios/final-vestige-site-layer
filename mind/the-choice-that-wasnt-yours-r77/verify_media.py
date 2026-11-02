#!/usr/bin/env python3
"""Offline only; verify actual rendered original film, VTT and review package."""
from pathlib import Path
from PIL import Image
import subprocess, json, re, zipfile, hashlib
D=Path(__file__).resolve().parent
video=D/'the-other-photograph-40s.mp4'
info=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=codec_name,width,height,r_frame_rate,nb_frames,duration','-of','json',str(video)]))['streams'][0]
assert (info['codec_name'],info['width'],info['height'],info['r_frame_rate'],info['nb_frames'])==('h264',540,960,'12/1','480')
assert float(info['duration'])==40.0
assert Image.open(D/'poster.png').size==(540,960)
assert Image.open(D/'contact-sheet.png').size==(1080,1280)
vtt=(D/'captions.vtt').read_text(encoding='utf-8')
assert vtt.startswith('WEBVTT') and len(re.findall(' --> ',vtt))==6
assert '00:00:00.000 --> 00:00:06.000' in vtt
assert '00:00:34.000 --> 00:00:40.000' in vtt
player=(D/'offline-review.html').read_text(encoding='utf-8')
assert '<video controls preload="none"' in player
assert '<track kind="captions"' in player and '<ol>' in player
assert '<script' not in player and 'autoplay' not in player.lower()
archive=D/'r77-offline-review.zip'
with zipfile.ZipFile(archive) as z:assert z.testzip() is None and len(z.namelist())>=6
print('PASS 10 native checks; 40.000 s, 480 H.264 frames, 540x960, 6 cues, transcript, clean ZIP')
print('VIDEO_SHA256='+hashlib.sha256(video.read_bytes()).hexdigest())
print('ZIP_SHA256='+hashlib.sha256(archive.read_bytes()).hexdigest())
