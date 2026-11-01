#!/usr/bin/env python3
"""Original Final Vestige silent educational short. No third-party media.
Run: python render_40s.py. Requires Pillow, FFmpeg, FFprobe.
Timing: 7+7+7+7+6+6=40 seconds, 12 fps, six original designed cards.
This is a conceptual explanation, not actual experiment footage or product endorsement.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess
import math

OUT=Path(__file__).resolve().parent
W,H=540,960
BG='#090A0A'; FG='#F4EFE6'; WARM='#D3B078'; MUTED='#BDB3A5'; MID='#252522'
SANS='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
font=lambda size,bold=False,serif=False: ImageFont.truetype(SERIF if serif else BOLD if bold else SANS,size)

def center(draw,text,y,size,color=FG,bold=False,serif=False):
    f=font(size,bold,serif)
    for i,line in enumerate(text.split('\n')):
        box=draw.textbbox((0,0),line,font=f)
        draw.text(((W-(box[2]-box[0]))/2,y+i*size*1.35),line,font=f,fill=color)

def base(i):
    im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
    d.rectangle([30,32,W-30,H-32],outline='#61563F',width=2)
    d.line((50,105,W-50,105),fill='#4E473B',width=2)
    d.text((52,65),f'EVIDENCE NOTE  /  0{i+1}',font=font(19,True),fill=WARM)
    d.line((50,H-120,W-50,H-120),fill='#4E473B',width=2)
    center(d,'FINAL VESTIGE  /  MIND & PERCEPTION',H-93,14,WARM,True)
    return im,d

def art(d,i):
    if i==0:
        d.line([(90,640),(250,300),(450,640)],fill=MUTED,width=4)
        d.line([(270,620),(270,355)],fill=WARM,width=5)
        for k in range(4): d.line([(270,390+k*56),(270,419+k*56)],fill=BG,width=10)
        d.rectangle((137,536,208,570),fill='#3D4340');d.rectangle((332,536,404,570),fill='#3D4340')
    elif i==1:
        d.rounded_rectangle((74,320,465,660),radius=16,fill='#181816',outline='#7E6847',width=3)
        center(d,'“SMASHED?”',427,42,WARM,True)
        d.line((125,561,410,561),fill='#948264',width=3)
    elif i==2:
        d.ellipse((154,345,396,587),outline=WARM,width=7)
        d.line((366,552,442,636),fill=WARM,width=12)
        center(d,'NO GLASS',431,27,FG,True)
        center(d,'IN FILM',474,26,MUTED,True)
    elif i==3:
        d.line((270,330,270,648),fill=WARM,width=2)
        d.rectangle((72,370,240,593),outline='#69645D',width=3)
        d.rectangle((300,370,468,593),outline='#69645D',width=3)
        d.text((116,470),'SEEN',font=font(20,True),fill=FG)
        d.text((343,470),'ASKED',font=font(20,True),fill=FG)
    elif i==4:
        for r in range(40,165,25): d.ellipse((270-r,480-r,270+r,480+r),outline='#6D634F',width=2)
        center(d,'?',414,88,WARM,True,True)
    elif i==5:
        for x,y in [(162,600),(270,600),(378,600)]:
            d.ellipse((x-11,y-11,x+11,y+11),fill=WARM)
        center(d,'SOURCES',386,42,FG,True,True)
        center(d,'BEFORE CLAIMS',458,31,WARM,True)

scenes=[
 ('THE FILM','SHOWED A ROAD.','No broken glass.'),
 ('A QUESTION','ADDED A WORD.','“Smashed.”'),
 ('A WEEK LATER,','THE GLASS?','It had not appeared.'),
 ('TWO SOURCES.','ONE ANSWER.','Seeing and hearing differ.'),
 ('A CHANGED REPORT','IS NOT A BRAIN SCAN.','Mechanisms remain debated.'),
 ('WHAT CAN WE SAY?','EVIDENCE FIRST.','Not proof of an audio product.'),
]
lengths=[7,7,7,7,6,6]
paths=[]
for i,(t,main,sub) in enumerate(scenes):
    im,d=base(i)
    center(d,t,165,32,MUTED,True)
    center(d,main,235,37,FG,True,True)
    art(d,i)
    center(d,sub,730,23,WARM)
    path=OUT/f'scene-{i+1:02}.png'; im.save(path,optimize=True);paths.append(path)
(OUT/'poster.png').write_bytes(paths[0].read_bytes())
inputs=[]
for p,sec in zip(paths,lengths):inputs+=['-loop','1','-framerate','12','-t',str(sec),'-i',str(p)]
cmd=['ffmpeg','-hide_banner','-loglevel','error','-y',*inputs,'-filter_complex',''.join(f'[{i}:v]setsar=1[v{i}];' for i in range(6))+''.join(f'[v{i}]' for i in range(6))+'concat=n=6:v=1:a=0[v]','-map','[v]','-c:v','libx264','-preset','veryfast','-crf','27','-r','12','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'absent-glass-40s.mp4')]
subprocess.run(cmd,check=True)
print('Rendered:',OUT/'absent-glass-40s.mp4')
