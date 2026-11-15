#!/usr/bin/env python3
"""Reproducibly render a 42-second original SILENT educational film.
Needs Pillow + ffmpeg; no third-party media, voice or paid services.
Output filename must match B guide. Generated MP4 is not a merchant endorsement.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import subprocess
OUT = Path(__file__).resolve().parent
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
W, H, FPS, SECONDS = 640, 360, 1, 42
VIDEO_W, VIDEO_H = 320, 180
SCENES = [
 ('THE SECOND SIGNAL', 'Why can something obvious still escape notice?'),
 ('ATTENTION HAS LIMITS', 'In laboratory tasks, noticing one target can cost you the next.'),
 ('A RESULT IS NOT A PROMISE', 'A controlled experiment is not a product endorsement.'),
 ('WHAT ZEN12 ACTUALLY SELLS', 'Its seller describes 12 course levels and 48 recordings.'),
 ('WHAT HAS NOT BEEN TESTED', 'The studies cited here did not test the Zen12 package.'),
 ('TRY THE FREE BASELINE', 'Compare your own practice before considering a purchase.'),
]
large=ImageFont.truetype(BOLD,30)
small=ImageFont.truetype(FONT,18)
tiny=ImageFont.truetype(FONT,14)
cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{VIDEO_W}x{VIDEO_H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','slow','-crf','47','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'zen12_42s_original_silent.mp4')]
p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
for n in range(FPS*SECONDS):
    sec=n/FPS
    idx=min(int(sec//7),5)
    image=Image.new('RGB',(W,H),(14,22,31))
    d=ImageDraw.Draw(image)
    for rad,stroke in [(74,(44,83,89)),(52,(54,113,119)),(26,(196,162,106))]:
        d.ellipse((320-rad,98-rad,320+rad,98+rad),outline=stroke,width=2)
    x=int(320+43*((sec%7)/7*2-1))
    d.ellipse((x-7,91,x+7,105),fill=(233,192,118))
    title,sub=SCENES[idx]
    d.text((W/2,211),title,font=large,fill=(246,239,220),anchor='mm')
    lines=[];cur=''
    for word in sub.split():
        nxt=(cur+' '+word).strip()
        if d.textlength(nxt,font=small)>545 and cur:lines.append(cur);cur=word
        else:cur=nxt
    if cur:lines.append(cur)
    for j,line in enumerate(lines):
        d.text((W/2,263+j*23),line,font=small,fill=(195,209,207),anchor='mm')
    d.rectangle((35,337,605,340),fill=(54,64,71))
    d.rectangle((35,337,35+int(570*(n+1)/(FPS*SECONDS)),340),fill=(221,180,108))
    d.text((36,16),'FINAL VESTIGE  /  MIND & PERCEPTION',font=tiny,fill=(158,176,180))
    p.stdin.write(image.resize((VIDEO_W,VIDEO_H),Image.Resampling.LANCZOS).tobytes())
p.stdin.close()
if p.wait():raise RuntimeError('ffmpeg render failed')
print(OUT/'zen12_42s_original_silent.mp4')
