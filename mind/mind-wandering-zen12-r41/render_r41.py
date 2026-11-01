#!/usr/bin/env python3
"""Reproducible original 40s silent educational film. Requires Pillow + ffmpeg.
No third-party footage, audio, logos, claims or web requests. Poster and MP4 offline.
The VTT text equivalents are source controlled separately.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math, subprocess

OUT = Path(__file__).resolve().parent
W, H, FPS = 540, 960, 12
DURATIONS = (6, 7, 7, 7, 7, 6)
SCENES = [
    ("YOU SAT DOWN", "TO PAY ATTENTION.", ["Then your mind wandered.", "That isn't the end of the story."], "WANDER"),
    ("THE MOMENT", "YOU NOTICE", ["Fourteen meditators pressed a button", "when they noticed attention drift."], "NOTICE"),
    ("FOUR PHASES.", "ONE ORDINARY MIND.", ["Wander. Notice. Shift. Focus.", "A useful model, not a magic switch."], "SHIFT"),
    ("A SCAN ISN'T", "A SALES RECEIPT.", ["Brain imaging did not test a product", "or guarantee any audio benefit."], "EVIDENCE"),
    ("TRY FOUR", "QUIET MINUTES.", ["Let attention wander; notice it.", "Then return. No purchase required."], "PRACTICE"),
    ("WHAT DOES", "THE RECORD PROVE?", ["A sincere experience needs evidence.", "FINAL VESTIGE STUDIOS"], "RETURN"),
]
FONTPATH = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONTBOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font = lambda size, bold=False: ImageFont.truetype(FONTBOLD if bold else FONTPATH, size)

def centered(draw, y, text, size, fill, bold=False):
    f = font(size, bold)
    bb = draw.textbbox((0, 0), text, font=f)
    draw.text(((W-(bb[2]-bb[0]))/2, y), text, fill=fill, font=f)

def card(number):
    title1, title2, notes, marker = SCENES[number]
    im = Image.new('RGB', (W,H), '#090B0B')
    d = ImageDraw.Draw(im)
    for y in range(H):
        v = int(10 + 11*y/H)
        d.line([(0,y),(W,y)], fill=(v,v+2,v+2))
    d.rounded_rectangle((25,24,W-25,H-24), radius=24, outline='#9A7C4E', width=2)
    centered(d, 67, 'F I N A L   V E S T I G E', 19, '#EBD9B5', True)
    centered(d, 116, 'MIND / PERCEPTION / EVIDENCE', 15, '#B7A98B')
    d.line((72,169,W-72,169), fill='#7B6747',width=2)
    centered(d, 221, title1, 37, '#F5E8D1', True)
    centered(d, 277, title2, 35, '#D4AD6E', True)
    cy = 487
    # Schematic research-process checkpoints, not an EEG trace.
    d.line((110,cy,430,cy),fill='#B8955E',width=5)
    for i, x in enumerate((110,216,324,430)):
        active = min(number,3) == i
        radius=24 if active else 13
        d.ellipse((x-radius,cy-radius,x+radius,cy+radius),fill='#D2B16F' if active else '#34464B',outline='#EFE6CD',width=2)
    d.rounded_rectangle((173,551,367,595), radius=22, outline='#A48859', width=2)
    centered(d, 560,marker,22,'#EEE7DB',True)
    for j,note in enumerate(notes): centered(d,664 + 47*j,note,21,'#E7E2D7')
    d.line((73,800,W-73,800),fill='#5B5C53',width=2)
    centered(d,825,'A STUDY IS NOT A PRODUCT TRIAL.',16,'#C4B9A7')
    centered(d,874,f'{number+1:02d} / 06  •  ORIGINAL EXPLAINER',16,'#AFAE9F')
    return im

def main():
    images = [card(i) for i in range(len(SCENES))]
    images[0].save(OUT/'the-return-poster.png',optimize=True)
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','24','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'the-return-40s.mp4')]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for img, seconds in zip(images,DURATIONS):
            payload=img.tobytes()
            for _ in range(seconds*FPS): proc.stdin.write(payload)
        proc.stdin.close()
        if proc.wait()!=0: raise RuntimeError('ffmpeg render failed')
    finally:
        if proc.poll() is None: proc.kill()
    print('Rendered original 40-second 540x960 12 fps silent clip and poster')

if __name__=='__main__': main()
