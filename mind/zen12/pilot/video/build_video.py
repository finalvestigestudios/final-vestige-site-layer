#!/usr/bin/env python3
"""Final Vestige original silent editorial motion study.
40.0 sec, 16:9, 15fps, local fonts only; no stock media, audio or product footage.
All meaningful words appear on screen with separate captions/transcript.
"""
import argparse, math, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W,H,FPS,DURATION=960,540,15,40
BG=(9,11,11); TEXT=(244,239,230); GOLD=(199,166,108); MUTED=(183,174,158); PANEL=(22,25,24)
SANS='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
def font(path,size):return ImageFont.truetype(path,size)
def ease(t):return t*t*(3-2*t)
def text_center(d,txt,y,size=44,color=TEXT,face=SERIF):
    f=font(face,size);box=d.textbbox((0,0),txt,font=f);w=box[2]-box[0]
    d.text(((W-w)/2,y),txt,font=f,fill=color)
def frame(sec):
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
    d.rectangle((32,27,928,513),outline=(66,57,43),width=2)
    d.line((57,70,903,70),fill=(68,60,47),width=1)
    d.text((63,41),'FINAL VESTIGE',fill=GOLD,font=font(BOLD,17))
    d.text((761,42),'MIND / FIELD STUDY',fill=MUTED,font=font(SANS,13))
    d.text((63,483),'An editorial illustration — not a product test',fill=MUTED,font=font(SANS,13))
    d.text((823,482),f'{sec:04.1f} / 40',fill=MUTED,font=font(SANS,13))
    if sec<8:
        phase=sec/8
        text_center(d,'THE HOUR YOU',155,53,face=SERIF)
        text_center(d,'NEVER FIND',222,58,color=GOLD,face=SERIF)
        d.text((211,322),'An impossible schedule is not a practice.',font=font(SANS,22),fill=TEXT)
        for i in range(12):
            x=221+i*45
            d.rounded_rectangle((x,375,x+30,387),radius=6,fill=(58,54,45) if i<10 else GOLD)
        d.text((350,415),'What could fit today?',font=font(SANS,18),fill=MUTED)
    elif sec<16:
        phase=(sec-8)/8
        text_center(d,'TWELVE MINUTES',150,63,color=GOLD,face=SERIF)
        text_center(d,'IS STILL TIME',231,43,face=SERIF)
        for i in range(12):
            angle=-math.pi/2+i*math.pi*2/12
            x=480+math.cos(angle)*127;y=365+math.sin(angle)*80
            r=9 if i<=int(phase*11) else 5
            d.ellipse((x-r,y-r,x+r,y+r),fill=GOLD if i<=int(phase*11) else (72,68,57))
        d.text((330,451),'Time saved is not proof of equivalent effects.',font=font(SANS,15),fill=MUTED)
    elif sec<24:
        phase=(sec-16)/8
        text_center(d,'TRY THIS NOW',151,57,face=SERIF)
        text_center(d,'Notice. Wander. Return.',225,37,color=GOLD,face=SERIF)
        a=phase*2*math.pi
        cx,cy=480,370
        r=58+8*math.sin(2*a)
        d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=GOLD,width=4)
        d.ellipse((cx-9,cy-9,cx+9,cy+9),fill=TEXT)
        d.text((326,448),'There is no score. You can begin for free.',font=font(SANS,17),fill=MUTED)
    elif sec<32:
        phase=(sec-24)/8
        text_center(d,'WHAT ZEN12 OFFERS',150,45,face=SERIF)
        text_center(d,'12 levels  /  4 listening styles',226,31,color=GOLD,face=SANS)
        labels=['GUIDED','MUSIC','NATURE','WHITE NOISE']
        for j,label in enumerate(labels):
            x=135+j*176
            d.rounded_rectangle((x,319,x+156,390),radius=9,fill=PANEL,outline=(75,66,51),width=2)
            d.text((x+12,336),label,fill=TEXT,font=font(BOLD,15))
            d.line((x+13,376,x+146,376),fill=GOLD,width=2)
        d.text((229,445),'Formats described by seller; benefits unverified.',font=font(SANS,18),fill=MUTED)
    else:
        text_center(d,'FOLLOW THE EVIDENCE',135,48,face=SERIF)
        text_center(d,'BEFORE THE PROMISE',204,52,color=GOLD,face=SERIF)
        d.line((330,282,630,282),fill=GOLD,width=2)
        text_center(d,'Compare the sources, limits, and free options.',309,21,face=SANS)
        text_center(d,'No product purchasing link is active.',361,19,face=SANS)
        text_center(d,'Future qualifying links may earn us a commission.',403,17,color=GOLD,face=SANS)
    d.rectangle((63,83,63+int((sec/DURATION)*840),87),fill=GOLD)
    return im
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--poster',type=Path,required=True)
    a=p.parse_args();a.out.parent.mkdir(parents=True,exist_ok=True);a.poster.parent.mkdir(parents=True,exist_ok=True)
    frame(32.4).save(a.poster,optimize=True)
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','-','-c:v','libx264','-preset','fast','-crf','27','-pix_fmt','yuv420p','-movflags','+faststart','-an',str(a.out)]
    x=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for i in range(DURATION*FPS):x.stdin.write(frame(i/FPS).tobytes())
        x.stdin.close();code=x.wait(timeout=120)
        if code:raise RuntimeError(f'ffmpeg {code}')
    finally:
        if x.poll() is None:x.kill()
    print(f'mp4={a.out} ({a.out.stat().st_size} bytes); poster={a.poster} ({a.poster.stat().st_size} bytes)')
if __name__=='__main__':main()
