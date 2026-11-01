#!/usr/bin/env python3
"""Final Vestige R46: entirely original silent, captioned 40-sec schematic.
Standard library + Pillow and ffmpeg. No external assets or network calls.
Not a physiological experiment, a merchant demo, or a health claim.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, subprocess

WIDTH, HEIGHT, FPS, SECONDS = 540, 960, 12, 40
OUT = Path(__file__).resolve().parent
GOLD = (199,166,108)
CREAM = (244,239,230)
MUTED = (211,202,185)
SANS = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
SERIF = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
FB = lambda n: ImageFont.truetype(SANS, n)
FS = lambda n: ImageFont.truetype(SERIF, n)

SCENES = [
    (0, 6.5, 'THE INSTRUCTION', ['Don\'t think of', 'a white bear.'], 'A harmless instruction in a controlled thought task'),
    (6.5, 13.0, 'THE MONITOR', ['To check it is gone,', 'you search for it.'], 'Instructions can influence what is noticed'),
    (13.0, 19.5, 'THE 1987 EXPERIMENT', ['A bell for the bear.', 'Five minutes.'], 'Participants marked reported intrusions'),
    (19.5, 26.0, 'THE REBOUND', ['Sometimes the bear', 'returns later.'], 'A subsequent thought period yielded more reports'),
    (26.0, 33.0, 'THE 2020 CORRECTION', ['During is not', 'the same as after.'], '31 studies; immediate effects depended on load'),
    (33.0, 40.0, 'THE LIMIT OF PROOF', ['A finding is not', 'a product promise.'], 'Notice a thought. Choose where attention goes.'),
]


def center(draw, y, s, font, fill=CREAM, max_width=490, spacing=0):
    box = draw.textbbox((0, 0), s, font=font)
    w = box[2] - box[0]
    if w > max_width:
        raise ValueError(f'Line would clip: {s}, width={w}')
    draw.text(((WIDTH-w)//2, y), s, font=font, fill=fill, stroke_width=0)


def bear(d, ox=0, oy=0, scale=1.0, alpha=1.0):
    def rect(x,y,x2,y2,fill,r=4):
        d.rounded_rectangle((int(x*scale+ox),int(y*scale+oy),int(x2*scale+ox),int(y2*scale+oy)),radius=int(r*scale), fill=fill)
    def ell(x,y,x2,y2,fill):
        d.ellipse((int(x*scale+ox),int(y*scale+oy),int(x2*scale+ox),int(y2*scale+oy)), fill=fill)
    ell(0,65,234,183,CREAM)
    ell(173,0,277,121,CREAM)
    ell(189,-19,226,25,CREAM)
    ell(238,-17,271,25,CREAM)
    for x in [32,93,167,208]:rect(x,147,x+29,277,CREAM,9)
    ell(248,58,295,94,(219,215,206)); ell(247,60,263,76,(25,25,24));ell(229,51,239,61,(25,25,24))


def background(t):
    im = Image.new('RGB', (WIDTH,HEIGHT), '#090a0a')
    pix=im.load()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            dx=(x-270)/WIDTH;dy=(y-385)/HEIGHT
            v=max(0,1-math.sqrt(dx*dx*2+dy*dy*1.8))
            pix[x,y]=(int(9+20*v),int(10+17*v),int(10+12*v))
    return im

BASE=background(0)

def frame(t):
    im=BASE.copy(); d=ImageDraw.Draw(im)
    index=next(i for i,(start,end,*_) in enumerate(SCENES) if start <= t < end)
    start,end,kicker,lines,note=SCENES[index]
    progress=(t-start)/(end-start)
    d.line((36,92,504,92),fill=(78,64,43),width=2)
    d.line((36,92,36+int(468*(t/SECONDS)),92),fill=GOLD,width=4)
    center(d,45,'FINAL VESTIGE  /  MIND & PERCEPTION',FB(14),GOLD)
    center(d,137,kicker,FB(17),GOLD)
    d.ellipse((101,234,439,572),outline=(122,100,66),width=2)
    d.ellipse((122,255,418,551),outline=(52,45,36),width=2)
    if index in (0,1,3,5):
        offset=math.sin(progress*math.pi)*3
        bear(d,ox=122+offset,oy=286,scale=1.00)
    elif index==2:
        d.ellipse((233,303,307,375),outline=CREAM,width=5)
        d.line((270,375,270,435),fill=CREAM,width=5)
        d.ellipse((242,425,299,481),outline=GOLD,width=4)
        center(d,510,'RING WHEN NOTICED',FB(14),GOLD)
    elif index==4:
        d.line((270,265,270,541),fill=(91,75,53),width=2)
        center(d,330,'DURING',FB(22),CREAM,max_width=235)
        center(d,405,'AFTER',FB(22),CREAM,max_width=235)
        center(d,485,'LOAD MATTERS',FB(17),GOLD)
    d.line((48,607,492,607),fill=(72,61,47),width=2)
    y=639
    for text in lines:
        center(d,y,text,FS(34),CREAM)
        y+=54
    d.line((86,783,454,783),fill=(72,61,47),width=1)
    # note wraps at at most 39 chars each, always check clip
    words=note.split(' ');parts=[];cur=''
    for w in words:
        nxt=(cur+' '+w).strip()
        if d.textbbox((0,0),nxt,font=FB(17))[2] > 465 and cur:
            parts.append(cur);cur=w
        else:cur=nxt
    if cur:parts.append(cur)
    for j,p in enumerate(parts):center(d,808+j*31,p,FB(17),MUTED)
    center(d,917,'SOURCE-BASED  ·  NO COMMERCIAL OUTCOME CLAIM',FB(11),GOLD)
    return im


def render():
    mp4=OUT/'the-bear-returns-40s.mp4'
    args=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{WIDTH}x{HEIGHT}','-framerate',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','28','-pix_fmt','yuv420p','-movflags','+faststart',str(mp4)]
    proc=subprocess.Popen(args,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for k in range(FPS*SECONDS):
            im=frame(k/FPS)
            if k==12:im.save(OUT/'the-bear-returns-poster.png')
            proc.stdin.write(im.tobytes())
        proc.stdin.close()
        error=proc.stderr.read().decode('utf-8','replace')
        if proc.wait():raise RuntimeError(error)
    except Exception:
        proc.kill();raise
    return mp4

if __name__=='__main__':
    p=render();print(p, p.stat().st_size)
