#!/usr/bin/env python3
"""Final Vestige Studios original R51 40s silent educational film.
No stock assets, network calls, audio, user data, or affiliate CTA. Needs Pillow and ffmpeg.
Run: python render_film.py. Captions and transcript are separate plain text artifacts.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math, subprocess

ROOT = Path(__file__).resolve().parent
W, H, FPS, SECONDS = 540, 960, 12, 40
BG = (10, 12, 14)
IVORY = (242, 233, 214)
GOLD = (212, 173, 105)
DIM = (160, 153, 142)
LINE = (65, 61, 53)
FONT_BASE = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_SERIF = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'

def font(size, bold=False, serif=False):
    path = FONT_SERIF if serif else FONT_BOLD if bold else FONT_BASE
    return ImageFont.truetype(path, size)

def text_center(draw, text, y, size, fill=IVORY, bold=False, serif=False):
    f=font(size,bold,serif)
    box=draw.textbbox((0,0),text,font=f)
    draw.text(((W-(box[2]-box[0]))/2,y),text,font=f,fill=fill)

def multiline(draw, lines, y, size=34, fill=IVORY, gap=12):
    for line in lines:
        text_center(draw,line,y,size,fill)
        y+=size+gap

def screen_base(scene):
    img=Image.new('RGB',(W,H),BG)
    d=ImageDraw.Draw(img)
    d.rectangle([0,0,W,8],fill=GOLD)
    for x in range(0,W,30):
        d.line((x,0,x,H),fill=(16,18,20),width=1)
    for y in range(0,H,32):
        d.line((0,y,W,y),fill=(16,18,20),width=1)
    d.text((36,36),'FINAL VESTIGE  /  THE MIND',font=font(17,True),fill=GOLD)
    d.line((36,80,W-36,80),fill=LINE,width=2)
    d.text((36,836),f'EVIDENCE NOTE   /   {scene+1:02d} OF 06',font=font(16,True),fill=GOLD)
    d.line((36,882,W-36,882),fill=LINE,width=2)
    d.text((36,908),'ORIGINAL EDUCATIONAL FILM · NOT A VISION TEST',font=font(11,True),fill=DIM)
    return img

def scene_art(scene):
    im=screen_base(scene);d=ImageDraw.Draw(im)
    if scene==0:
        text_center(d,'TWO NUMBERS',166,42,IVORY,True)
        text_center(d,'ONE RAPID STREAM',224,30,DIM)
        for j,s in enumerate(['K   P   Q   L','J   7   N   R','A   4   C   X','M   T   Z   B']):
            text_center(d,s,354+j*61,37,GOLD if j in (1,2) else DIM)
        d.line((90,315,450,315),fill=GOLD,width=2)
    if scene==1:
        multiline(d,['YOU REPORT','THE FIRST.'],190,53)
        text_center(d,'7',393,182,GOLD,serif=True)
        text_center(d,'The next target arrives soon after.',715,23,DIM)
    if scene==2:
        multiline(d,['THE SECOND','WAS PRESENTED.'],185,44)
        text_center(d,'4',387,188,(111,104,90),serif=True)
        d.line((125,600,415,600),fill=GOLD,width=3)
        multiline(d,['The report can still fail.','No shutter has been observed.'],634,22,DIM,9)
    if scene==3:
        multiline(d,['THE EXCEPTION','MATTERS.'],166,46)
        d.rounded_rectangle((104,372,436,572),radius=15,outline=GOLD,width=3)
        d.text((141,399),'7',font=font(115,serif=True),fill=IVORY)
        d.text((313,399),'4',font=font(115,serif=True),fill=GOLD)
        multiline(d,['Immediate neighbors can','sometimes escape the gap.'],650,25,DIM,9)
    if scene==4:
        multiline(d,['TRAINING IS','NOT A PRODUCT TRIAL.'],157,41)
        d.rounded_rectangle((72,349,468,464),radius=11,fill=(26,28,28),outline=LINE,width=2)
        text_center(d,'3 MONTHS',373,45,GOLD,True)
        text_center(d,'INTENSIVE MEDITATION STUDY',441,18,DIM)
        d.rounded_rectangle((72,512,468,627),radius=11,fill=(26,28,28),outline=LINE,width=2)
        text_center(d,'12 MINUTES',536,45,IVORY,True)
        text_center(d,'COMMERCIAL AUDIO CLAIM',604,18,DIM)
        d.line((88,481,452,481),fill=(132,76,65),width=3)
    if scene==5:
        multiline(d,['WHAT WAS','MEASURED?'],178,51)
        multiline(d,['WHAT WAS','INFERRED?'],375,49,GOLD)
        text_center(d,'FOLLOW THE EVIDENCE.',647,26,IVORY,True)
        d.line((89,718,451,718),fill=GOLD,width=3)
    return im

def scene_at_time(t):
    return 0 if t<6 else 1 if t<12 else 2 if t<18 else 3 if t<25 else 4 if t<32 else 5

def main():
    originals=[scene_art(i) for i in range(6)]
    # A static source poster plus frame-level progress convey duration without flicker.
    originals[0].save(ROOT/'film-poster.png',optimize=True)
    out=ROOT/'attentional-blink-evidence-40s.mp4'
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}',
         '-r',str(FPS),'-i','-','-an','-c:v','libx264','-pix_fmt','yuv420p','-preset','veryfast',
         '-crf','28','-movflags','+faststart','-frames:v',str(SECONDS*FPS),str(out)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for f in range(SECONDS*FPS):
            t=f/FPS
            im=originals[scene_at_time(t)].copy()
            d=ImageDraw.Draw(im)
            x0,x1=36,W-36
            d.rectangle((x0,867,x1,872),fill=(58,53,46))
            d.rectangle((x0,867,x0+int((x1-x0)*f/(SECONDS*FPS)),872),fill=GOLD)
            d.text((W-122,36),f'{int(t):02d} / 40s',font=font(16,True),fill=DIM)
            proc.stdin.write(im.tobytes())
    except BrokenPipeError:
        raise RuntimeError('ffmpeg closed pipe prematurely')
    finally:
        proc.stdin.close()
    stderr=proc.stderr.read().decode(errors='replace')
    rc=proc.wait()
    if rc:raise RuntimeError(f'ffmpeg exit {rc}: {stderr}')
    print(f'{out.name} {out.stat().st_size} bytes; {SECONDS*FPS} frames at {FPS} fps, {W}x{H}')
if __name__=='__main__':main()
