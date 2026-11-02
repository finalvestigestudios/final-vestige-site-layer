#!/usr/bin/env python3
"""Reproducible original 40-sec 9:16 silent explainer. NO product demonstration.
License: original Final Vestige Studios illustrative drawings and copy.
Runs with Pillow and ffmpeg; external fonts are local render dependencies only.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math, subprocess, tempfile, shutil, textwrap
OUT=Path(__file__).resolve().parent
W,H,FPS,FRAMES=540,960,12,480
BG=(9,11,11); FG=(245,240,230); GOLD=(203,169,109); MUTED=(177,170,155)
SANS='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
font=lambda path,size:ImageFont.truetype(path,size)
F_TITLE=font(SERIF,45); F_HEAD=font(SERIF,40); F_BODY=font(SANS,23); F_SMALL=font(SANS,16); F_NUM=font(SERIF,25)
scenes=[
 (0,6,'THE INSTRUCTION',['Do not think','of a white bear.']),
 (6,13,'THE MONITOR',['How do you know','whether it appeared?']),
 (13,20,'THE PARADOX',['To check for a thought,','you must recognize it.']),
 (20,27,'THE EXPERIMENT',['Wegner and colleagues','measured later rebound.']),
 (27,34,'THE LATER EVIDENCE',['31 studies: timing','and cognitive load matter.']),
 (34,40,'THE LIMIT',['An experiment is not','proof of an audio product.'])]

def text_center(d,xy,txt,f,color,space=0):
    bb=d.textbbox((0,0),txt,font=f)
    d.text((xy[0]-(bb[2]-bb[0])/2,xy[1]),txt,fill=color,font=f,stroke_width=0)

def draw_bear(draw,x,y,scale,outline=GOLD,alpha=255):
    # Plain original abstract bear illustration assembled from primitive curves.
    # No trademark, photograph, or proprietary stock art.
    s=scale
    ear1=(int(x-102*s),int(y-113*s),int(x-33*s),int(y-40*s))
    ear2=(int(x+33*s),int(y-113*s),int(x+102*s),int(y-40*s))
    head=(int(x-108*s),int(y-80*s),int(x+108*s),int(y+130*s))
    draw.ellipse(ear1,fill=(20,24,22),outline=outline,width=max(2,int(4*s)))
    draw.ellipse(ear2,fill=(20,24,22),outline=outline,width=max(2,int(4*s)))
    draw.ellipse(head,fill=(24,27,24),outline=outline,width=max(2,int(4*s)))
    draw.ellipse((x-42*s,y+48*s,x+42*s,y+105*s),fill=(43,43,34),outline=outline,width=max(1,int(2*s)))
    draw.ellipse((x-49*s,y-2*s,x-30*s,y+17*s),fill=FG)
    draw.ellipse((x+30*s,y-2*s,x+49*s,y+17*s),fill=FG)
    draw.ellipse((x-12*s,y+54*s,x+12*s,y+71*s),fill=GOLD)

def scene_at(t):
    for i,(start,end,_,__) in enumerate(scenes):
        if start <= t < end:return i
    return 5

def frame(t):
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
    # Vertical ruled field, slow-moving outline rings. No flashing or strobes.
    for j in range(0,9):
        x=40+j*60;d.line((x,0,x,H),fill=(16,19,17),width=1)
    for k in range(3):
        ry=395+int(22*math.sin(t*.21+k*.7));r=165+60*k
        d.ellipse((W//2-r,ry-r,W//2+r,ry+r),outline=(36+9*k,38+8*k,33+6*k),width=1)
    d.line((34,66,W-34,66),fill=(83,71,51),width=2)
    d.text((34,32),'FINAL VESTIGE   /   MIND & PERCEPTION',font=F_SMALL,fill=GOLD)
    idx=scene_at(t);start,end,label,lines=scenes[idx]
    d.text((34,93),f'0{idx+1} / 06   {label}',font=F_SMALL,fill=GOLD)
    shift=math.sin(t*.45)*4
    draw_bear(d,W/2,365+shift,1.0,outline=(161,143,105) if idx>=3 else GOLD)
    if idx==1:
        d.arc((120,217,420,539),50,316,fill=FG,width=3)
        d.line((389,497,419,527),fill=FG,width=3)
    if idx==2:
        for k in range(3):
            rr=145+22*k
            d.arc((W/2-rr,365-rr,W/2+rr,365+rr),205,337,fill=(90+25*k,84+20*k,65+16*k),width=3)
    if idx==3:
        # Draw original symbolic bell plus counted notches, not a real data visualization.
        d.rounded_rectangle((184,590,356,624),radius=7,fill=(28,31,27),outline=(92,79,54),width=2)
        for k in range(8): d.line((199+17*k,602,199+17*k,615),fill=(201,174,116),width=2)
    for q,line in enumerate(lines):
        text_center(d,(W/2,616+q*49),line,F_HEAD if idx in (0,5) else F_BODY,FG)
    text_center(d,(W/2,779),'ORIGINAL EDUCATIONAL ILLUSTRATION',F_SMALL,MUTED)
    text_center(d,(W/2,810),'Not an experiment recording or product proof.',F_SMALL,MUTED)
    d.line((34,877,W-34,877),fill=(90,79,59),width=2)
    d.rounded_rectangle((34,874,34+int((W-68)*(t/40)),880),radius=1,fill=GOLD)
    d.text((34,900),f'{t:04.1f} / 40 SEC  •  NO AUDIO',font=F_SMALL,fill=MUTED)
    return im

def main():
    poster=frame(0);poster.save(OUT/'poster.png',optimize=True)
    shot=Image.new('RGB',(W*3,H*2))
    for i,(start,end,_,__) in enumerate(scenes):shot.paste(frame((start+end)/2),((i%3)*W,(i//3)*H))
    shot.resize((810,960)).save(OUT/'six-scenes.png',optimize=True)
    with tempfile.TemporaryDirectory(prefix='fv-film-') as temp:
        tdir=Path(temp)
        for i in range(FRAMES):frame(i/FPS).save(tdir/f'{i:04d}.png')
        out=OUT/'the-bear-you-cant-unthink-40s.mp4'
        cmd=['ffmpeg','-loglevel','error','-y','-framerate',str(FPS),'-i',str(tdir/'%04d.png'),'-an','-c:v','libx264','-pix_fmt','yuv420p','-r',str(FPS),'-movflags','+faststart','-crf','24',str(out)]
        subprocess.run(cmd,check=True)
        print(out)
if __name__=='__main__': main()
