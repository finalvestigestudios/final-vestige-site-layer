#!/usr/bin/env python3
"""Original, silent, 42-second research microfilm for FV Mind R416.
No network, external media, commercial link, tracking, or personal information.
Needs Pillow and FFmpeg. Output is for unpublished QA, not deployment.
"""
import argparse
import math
import os
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, SECONDS = 640, 360, 2, 42
SCENES = [
    ("TWO TONES.", "ONE PERCEIVED RHYTHM.", "The sensation is not a clinical outcome."),
    ("PERCEPTION ≠", "BRAIN ENTRAINMENT", "A neural mechanism needs direct evidence."),
    ("14 STUDIES.", "MIXED FINDINGS.", "5 supportive · 8 contradictory · 1 mixed"),
    ("EEG SIGNAL ≠", "BETTER READING", "Different question. Different measurement."),
    ("ASK FOR", "PRODUCT-SPECIFIC PROOF", "Which recording, control, and task?"),
    ("A FREE FIRST STEP:", "OBSERVE YOUR ATTENTION", "Your decision does not require a purchase."),
]
VTT = """WEBVTT

00:00:00.000 --> 00:00:07.000
Two tones can create a perceived rhythm.

00:00:07.000 --> 00:00:14.000
Perception is not the same as brain entrainment.

00:00:14.000 --> 00:00:21.000
The published findings are inconsistent.

00:00:21.000 --> 00:00:28.000
An EEG response is not a completed task.

00:00:28.000 --> 00:00:35.000
Demand product-specific controlled evidence.

00:00:35.000 --> 00:00:42.000
Try a free observation; decide for yourself.
"""
TRANSCRIPT = """Original silent 42-second explanatory film, text-only transcript.
0–7s: Two slightly different tones can produce a perceived rhythmic sensation.
7–14s: A reported sensation does not automatically demonstrate brain entrainment.
14–21s: A 2023 review of fourteen studies reported five supportive, eight contradictory, and one mixed result for binaural-beat entrainment.
21–28s: Even a demonstrated EEG response would not, on its own, prove a reader completes tasks better.
28–35s: Ask what exact product was tested, against which comparator, and using what measured outcome.
35–42s: Try an ordinary free attention observation, and make an informed purchase decision without pressure.
Sources: https://pmc.ncbi.nlm.nih.gov/articles/PMC10198548/ ; https://pubmed.ncbi.nlm.nih.gov/38458383/ .
Not a demonstration of Zen12/Total Focus/Focus Shot efficacy or a product testimonial. No audio track, autoplay, or paid media.
"""

def font(size, serif=False):
    env = 'FV_FONT_SERIF' if serif else 'FV_FONT_SANS'
    tries = [os.environ.get(env), '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf' if serif else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf']
    for t in tries:
        if t:
            try: return ImageFont.truetype(t, size)
            except OSError: pass
    return ImageFont.load_default()

def center(draw, xy, msg, ft, color):
    box = draw.textbbox((0, 0), msg, font=ft)
    draw.text((xy[0] - (box[2] - box[0])/2, xy[1] - (box[3] - box[1])/2), msg, font=ft, fill=color)

def frame(index):
    sec = index/FPS
    scene = min(5, int(sec//7))
    local = sec - scene*7
    # Avoid a loud cut: fade in/out scene text for a couple of frames.
    alpha = min(1.0, local/0.7, (7-local)/0.7)
    alpha = max(0.22, alpha)
    im = Image.new('RGB', (W,H)); d = ImageDraw.Draw(im)
    for y in range(H):
        d.line((0,y,W,y), fill=(int(14+18*y/H),int(23+19*y/H),int(31+14*y/H)))
    d.rounded_rectangle((20,20,620,340),radius=14,outline=(113,126,126),width=2)
    # Animated, purely illustrative waveforms (not experimental EEG recordings).
    for row, color, freq, offset in [(100,(217,173,96),1.0,0),(125,(117,194,186),1.12,0.5)]:
        points = [(x,row + 11*math.sin(x*freq*0.055 + sec*1.5 + offset)) for x in range(35,606)]
        d.line(points, fill=color, width=2)
    title,sub,detail=SCENES[scene]
    foreground=(int(230*alpha),int(212*alpha),int(179*alpha))
    center(d,(W//2,196),title,font(26),foreground)
    center(d,(W//2,238),sub,font(24,serif=True),(int(242*alpha),int(197*alpha),int(119*alpha)))
    center(d,(W//2,280),detail,font(12),(int(203*alpha),int(218*alpha),int(211*alpha)))
    d.text((36,35),'FINAL VESTIGE STUDIOS  /  MIND & PERCEPTION',font=font(10),fill=(202,211,206))
    d.text((36,317),'Independent evidence visual · not a product trial',font=font(10),fill=(196,203,201))
    d.text((560,317),f'{scene+1}/6',font=font(11),fill=(240,190,100))
    return im

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',default='.')
    args=ap.parse_args()
    out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
    (out/'FV_R416_CAPTIONS.vtt').write_text(VTT,encoding='utf-8')
    (out/'FV_R416_TRANSCRIPT.txt').write_text(TRANSCRIPT,encoding='utf-8')
    frame(7).save(out/'FV_R416_POSTER.png',optimize=True)
    path=out/'FV_R416_42S.mp4'
    command=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','slow','-crf','27','-pix_fmt','yuv420p','-movflags','+faststart',str(path)]
    proc=subprocess.Popen(command,stdin=subprocess.PIPE)
    for i in range(SECONDS*FPS): proc.stdin.write(frame(i).tobytes())
    proc.stdin.close()
    code=proc.wait()
    if code: raise RuntimeError(f'FFmpeg failed: {code}')
    print(path, path.stat().st_size,'bytes')

if __name__=='__main__': main()
