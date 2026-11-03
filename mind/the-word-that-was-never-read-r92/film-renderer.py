#!/usr/bin/env python3
"""Original FV R92 educational 40-second vertical silent film.
No network access. Only Pillow + system ffmpeg. Run: python film-renderer.py
Output is NOT cleared for website publication. Transcript and captions required.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math, subprocess

HERE=Path(__file__).resolve().parent
W,H,FPS,SECS=540,960,12,40
BG=(9,13,14); PANEL=(21,29,28); BRONZE=(217,177,111); IVORY=(245,238,224); MUTE=(188,180,164)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
normal=lambda s: ImageFont.truetype(FONT,s)
serif=lambda s: ImageFont.truetype(SERIF,s)
SCENES=[
 (0,6,'A LIST IS READ','bed   rest   awake','A sequence of related words\nleaves a pattern behind.'),
 (6,12,'THE LIST CLOSES','WHAT REMAINS?','The original page is gone.\nOnly the report remains.'),
 (12,19,'AN ANSWER APPEARS','SLEEP','A plausible word can be remembered\neven when it was not presented.'),
 (19,26,'TWO RECORDS','PRESENTED  /  REPORTED','These are different records.\nOne should not replace the other.'),
 (26,33,'A LABORATORY RESULT','1995','Roediger and McDermott studied\nword-list false recall, not all lives.'),
 (33,40,'THE SOURCE TRAIL','CERTAINTY IS NOT\nA SOURCE','Read the study. Keep the original.\nAsk what was actually shown.')]

def centered(d,xy,message,font,color,max_width=485,spacing=10):
    lines=message.split('\n')
    sizes=[d.textbbox((0,0),line,font=font)[2] for line in lines]
    if max(sizes or [0])>max_width: raise ValueError('Text too wide: '+message)
    lineheight=font.size+spacing
    top=xy[1]-len(lines)*lineheight//2
    for i,line in enumerate(lines): d.text(((W-sizes[i])/2,top+i*lineheight),line,font=font,fill=color)

def frame(sec):
    index=next(i for i,(a,b,*_) in enumerate(SCENES) if a <= sec < b)
    a,b,title,key,subtitle=SCENES[index]
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
    # Subtle stationary matrix. No flashing or optical triggers.
    for x in range(42,W,50): d.line((x,0,x,H),fill=(12,18,18),width=1)
    for y in range(46,H,55): d.line((0,y,W,y),fill=(12,18,18),width=1)
    d.rectangle((18,18,W-18,H-18),outline=(70,64,53),width=2)
    d.text((38,40),'FINAL VESTIGE   /   MIND',font=normal(16),fill=BRONZE)
    d.line((38,85,502,85),fill=(96,84,67),width=2)
    d.text((38,112),f'FIELD NOTE 0{index+1}    •    ORIGINAL ILLUSTRATION',font=normal(12),fill=MUTE)
    d.rounded_rectangle((39,228,501,704),radius=10,fill=PANEL,outline=(85,72,53),width=2)
    centered(d,(W//2,294),title,normal(22),BRONZE)
    # Scene-specific evidence visual, never a purported experimental recording.
    if index==0:
        centered(d,(W//2,459),key,serif(28),IVORY)
        d.line((92,507,448,507),fill=BRONZE,width=2)
        centered(d,(W//2,571),'dream   pillow   tired',normal(22),IVORY)
    elif index==1:
        for j in range(4):
            off=(sec-a)*3 if j%2==0 else 0
            d.line((115,394+j*36,420-off,394+j*36),fill=(104,96,80),width=3)
        centered(d,(W//2,591),'[ original not shown ]',normal(18),MUTE)
    elif index==2:
        pulse=0.5+0.5*math.sin((sec-a)*1.3)
        c=tuple(int(IVORY[i]*(.8+.2*pulse)) for i in range(3))
        centered(d,(W//2,464),key,serif(67),c)
        centered(d,(W//2,585),'NOT ON THE LIST',normal(17),BRONZE)
    elif index==3:
        d.rounded_rectangle((71,402,248,580),radius=5,outline=BRONZE,width=2)
        d.rounded_rectangle((292,402,469,580),radius=5,outline=BRONZE,width=2)
        centered(d,(W//2,635),'SOURCE  ≠  MEMORY',normal(20),IVORY)
        d.text((98,479),'ORIGINAL',font=normal(17),fill=IVORY)
        d.text((320,479),'REPORT',font=normal(17),fill=IVORY)
    elif index==4:
        centered(d,(W//2,461),key,serif(76),IVORY)
        centered(d,(W//2,581),'CONTROLLED WORD LISTS',normal(18),BRONZE)
    else:
        centered(d,(W//2,452),key,serif(36),IVORY)
        centered(d,(W//2,587),'CHECK THE ORIGINAL',normal(18),BRONZE)
    d.line((38,740,502,740),fill=(96,84,67),width=2)
    centered(d,(W//2,819),subtitle,normal(19),IVORY,spacing=15)
    d.rectangle((38,900,502,908),fill=(57,58,53))
    d.rectangle((38,900,38+int(464*(sec/SECS)),908),fill=BRONZE)
    d.text((38,925),'EDUCATIONAL SCHEMATIC • NOT AN EXPERIMENT',font=normal(11),fill=MUTE)
    return im

if __name__=='__main__':
    command=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','29','-pix_fmt','yuv420p','-movflags','+faststart',str(HERE/'the-missing-word-40s.mp4')]
    proc=subprocess.Popen(command,stdin=subprocess.PIPE)
    try:
        for i in range(FPS*SECS):
            proc.stdin.write(frame((i+.01)/FPS).tobytes())
    finally:
        proc.stdin.close()
    if proc.wait(): raise RuntimeError('ffmpeg failed')
    frame(12.1).save(HERE/'poster.png',optimize=True)
    print('Rendered',FPS*SECS,'frames at',FPS,'fps')
