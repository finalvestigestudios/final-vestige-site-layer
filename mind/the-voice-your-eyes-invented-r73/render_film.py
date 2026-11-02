#!/usr/bin/env python3
"""Original 40-second silent educational film for FV Mind R73.

Requires Pillow, opencv-python, ffmpeg. No network calls. Narrative illustration,
NOT a demonstration of actual McGurk audio or an endorsement of any merchant.
"""
from pathlib import Path
import math, subprocess, textwrap, hashlib
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W,H,FPS = 540,960,12
DURATIONS=[7,7,7,7,6,6]
OUT=Path(__file__).resolve().parent
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
SERIF_BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
C_BG=(13,25,34); C_BG2=(24,45,56); C_GOLD=(233,194,132); C_WHITE=(248,243,227); C_MUTED=(200,209,205)
SCENES=[
 ('THE SOUND\nBETWEEN\nMOUTH & EAR','Perception is more than a microphone.', 'OBSERVATION / 01'),
 ('THE SOUND\nSAYS  “BA”','The film shows a mouth forming “ga”.', 'EVIDENCE / 02'),
 ('SOME\nREPORT “DA”','The isolated soundtrack contains no “da”.', 'EXPERIENCE / 03'),
 ('NOT EVERYONE\nHEARS IT','The effect varies across people and clips.', 'REPLICATION / 04'),
 ('A REPORT\nIS NOT A CAUSE','What happened? What was perceived?', 'METHOD / 05'),
 ('SEPARATE\nTHE EVIDENCE','An unusual experience still needs a test.', 'FINAL VESTIGE / 06'),
]

def f(font,size):return ImageFont.truetype(font,size)

def linebreak(draw,txt,font,maxw):
    words=txt.split(); lines=[]; cur=''
    for word in words:
        trial=(cur+' '+word).strip()
        if draw.textbbox((0,0),trial,font=font)[2] > maxw and cur:lines.append(cur);cur=word
        else:cur=trial
    if cur:lines.append(cur)
    return lines

def scene_image(i):
    img=Image.new('RGB',(W,H)); pix=img.load()
    for y in range(H):
        s=y/H
        for x in range(W):
            k=math.sin(x/113+y/151)*.024
            t=min(1,max(0,s*.65+k))
            pix[x,y]=tuple(int(C_BG[j]*(1-t)+C_BG2[j]*t) for j in range(3))
    d=ImageDraw.Draw(img)
    d.rectangle((21,20,W-21,H-20),outline=(130,111,83),width=2)
    d.line((49,88,W-49,88), fill=C_GOLD,width=2)
    d.text((49,49),'F I N A L   V E S T I G E',font=f(BOLD,19),fill=C_GOLD)
    d.text((49,116),'MIND & PERCEPTION  /  AN ORIGINAL FILM',font=f(FONT,14),fill=C_MUTED)
    # stylised scientific observation motif - two rings/eye-mouth, not real stimulus
    cx=W//2;cy=323
    for r in [114,86,54]:d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(90+int(r/7),94+int(r/8),97+int(r/9)),width=2)
    if i in (0,1,2):
        d.rounded_rectangle((cx-74,cy-36,cx+74,cy+36),radius=34,outline=C_GOLD,width=4)
        if i==2:d.text((cx-45,cy-25),'DA?',font=f(SERIF_BOLD,34),fill=C_WHITE)
        else:d.arc((cx-52,cy-22,cx+52,cy+22),0,180,fill=C_GOLD,width=5)
    elif i==3:
        for j in range(7):
            d.ellipse((cx-75+j*24,cy-16+(j%3)*8,cx-62+j*24,cy-3+(j%3)*8),fill=C_GOLD if j%2 else C_WHITE)
    elif i==4:
        d.line((cx-65,cy+30,cx+65,cy-30),fill=C_GOLD,width=5)
        d.ellipse((cx-69,cy-4,cx-5,cy+60),outline=C_WHITE,width=3)
        d.ellipse((cx+5,cy-60,cx+69,cy+4),outline=C_GOLD,width=3)
    else:
        d.polygon([(cx,cy-64),(cx-68,cy+65),(cx+68,cy+65)],outline=C_GOLD,width=3)
        d.text((cx-13,cy-31),'?',font=f(SERIF_BOLD,53),fill=C_WHITE)
    header,subtitle,tag=SCENES[i]
    text_font=f(SERIF_BOLD,46 if i in (0,3,4,5) else 54)
    lines=header.split('\n'); top=503
    for line in lines:
        box=d.textbbox((0,0),line,font=text_font);ww=box[2]-box[0]
        d.text(((W-ww)//2,top),line,font=text_font,fill=C_WHITE);top+=70
    d.line((67,top+18,W-67,top+18),fill=C_GOLD,width=2)
    smallfont=f(FONT,24); lines=linebreak(d,subtitle,smallfont,W-110)
    for k,line in enumerate(lines):
        box=d.textbbox((0,0),line,font=smallfont);ww=box[2]-box[0]
        d.text(((W-ww)//2,top+43+k*34),line,font=smallfont,fill=C_MUTED)
    d.text((48,H-101),tag,font=f(BOLD,16),fill=C_GOLD)
    d.text((48,H-69),'ILLUSTRATIVE · NOT THE ORIGINAL 1976 EXPERIMENT',font=f(FONT,12),fill=C_MUTED)
    return img

def render():
    bases=[]
    for i in range(6):
        p=OUT/f'scene-{i+1:02}.png';im=scene_image(i);im.save(p);bases.append(np.array(im)[:,:,::-1].copy())
    frames=sum(DURATIONS)*FPS
    raw=OUT/'film-raw.mp4';final=OUT/'the-sound-between-mouth-and-ear-40s.mp4'
    writer=cv2.VideoWriter(str(raw),cv2.VideoWriter_fourcc(*'mp4v'),FPS,(W,H))
    assert writer.isOpened(),'VideoWriter failed'
    n=0
    for idx,duration in enumerate(DURATIONS):
        for j in range(duration*FPS):
            frame=bases[idx].copy()
            # only decorative gold line is animated; avoids implying we are reproducing an audiovisual test
            x0=68; y0=830
            for x in range(x0,W-68):
                amplitude=9*math.sin((x/26.0)+(j/7.0))*math.sin(math.pi*(j+1)/(duration*FPS+1))
                xx=x+1;yy=int(y0+amplitude)
                cv2.line(frame,(x,y0),(xx,yy),(120,185,226),1,cv2.LINE_AA)
            writer.write(frame);n+=1
    writer.release();assert n==frames==480,(n,frames)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(raw),'-c:v','libx264','-preset','veryfast','-crf','22','-pix_fmt','yuv420p','-movflags','+faststart','-an',str(final)],check=True)
    raw.unlink()
    # One-grid editorial review of six original frames
    thumb=Image.new('RGB',(3*180,2*320),(5,8,12))
    for i in range(6):thumb.paste(Image.open(OUT/f'scene-{i+1:02}.png').resize((180,320)),((i%3)*180,(i//3)*320))
    thumb.save(OUT/'contact-sheet.png')
    Image.open(OUT/'scene-01.png').save(OUT/'poster.png')
    print('FRAMES',n,'BYTES',final.stat().st_size,'SHA256',hashlib.sha256(final.read_bytes()).hexdigest())
if __name__=='__main__':render()
