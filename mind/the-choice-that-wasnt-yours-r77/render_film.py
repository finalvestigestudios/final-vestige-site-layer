#!/usr/bin/env python3
"""Original silent 40-second choice-blindness explainer, no merchant media.
Produces film, first frame poster, caption VTT and six-scene contact sheet.
Requires Pillow and ffmpeg. Deterministic 540x960, 12fps, 480 frames.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess, hashlib
W,H,FPS,SECONDS=540,960,12,40
BASE=Path(__file__).resolve().parent
GOLD=(216,181,119); IVORY=(244,239,230); MUTE=(189,180,162); PANEL=(25,30,27)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def ft(n,b=False):return ImageFont.truetype(BOLD if b else FONT,n)
SCENES=[
    ('THE OTHER','PHOTOGRAPH','Sometimes the evidence changes.','And the reason still sounds certain.'),
    ('TWO IMAGES','ONE CHOICE','A participant chooses a portrait.','The choice is recorded.'),
    ('A QUIET','SWAP','The experimenter reveals','the other portrait instead.'),
    ('A READY','EXPLANATION','Some people miss the mismatch.','They explain what they were handed.'),
    ('SINCERE IS','NOT CERTAIN','A convincing account does not','verify the original decision.'),
    ('KEEP THE','RECORD','Return to what was chosen.','Johansson and colleagues, 2005.')]
TIMES=[0,6,13,20,27,34,40]
def center(draw,text,y,font,color):
    b=draw.textbbox((0,0),text,font=font);draw.text(((W-(b[2]-b[0]))//2,y),text,font=font,fill=color)
def portrait(draw,x,y,choice=False):
    edge=GOLD if choice else (76,77,66)
    draw.rounded_rectangle((x,y,x+176,y+258),radius=9,fill=PANEL,outline=edge,width=4 if choice else 2)
    draw.ellipse((x+50,y+34,x+128,y+126),fill=(111,113,100))
    draw.ellipse((x+17,y+136,x+159,y+243),fill=(90,92,82))
    draw.line((x+60,y+88,x+73,y+88),fill=IVORY,width=2)
    draw.line((x+106,y+88,x+119,y+88),fill=IVORY,width=2)
    if choice:draw.text((x+18,y+12),'SELECTED',font=ft(12,True),fill=GOLD)
def frame(t):
    i=next(j for j in range(6) if TIMES[j]<=t<TIMES[j+1])
    im=Image.new('RGB',(W,H),(10,13,13));d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,12),fill=GOLD);d.text((30,33),'FINAL VESTIGE  /  MIND ARCHIVE',font=ft(14,True),fill=GOLD)
    d.line((30,76,W-30,76),fill=(73,67,54),width=2)
    d.text((30,95),f'FIELD STUDY 0{i+1} / 06',font=ft(14),fill=MUTE)
    if i==0:
        portrait(d,92,210,True);portrait(d,272,210)
    elif i==1:
        portrait(d,92,210,True);portrait(d,272,210)
        d.line((178,506,178,540),fill=GOLD,width=5);center(d,'YOUR CHOICE',548,ft(16,True),GOLD)
    elif i==2:
        portrait(d,92,210);portrait(d,272,210,True)
        d.arc((130,174,405,519),160,336,fill=GOLD,width=6)
    elif i==3:
        portrait(d,176,210,True);d.rounded_rectangle((70,501,470,596),radius=8,fill=(25,31,27),outline=(86,77,61),width=2)
        center(d,'WHY THIS ONE?',530,ft(20,True),IVORY)
    elif i==4:
        portrait(d,90,210,True);portrait(d,270,210)
        d.line((174,545,366,545),fill=GOLD,width=3);center(d,'THE GAP',568,ft(18,True),GOLD)
    else:
        portrait(d,92,210,True);portrait(d,272,210)
        d.rectangle((90,500,450,570),outline=GOLD,width=3);center(d,'ORIGINAL SELECTION',520,ft(15,True),GOLD)
    d.rectangle((24,652,516,847),fill=(20,24,22),outline=(64,61,53),width=2)
    center(d,SCENES[i][0],672,ft(33,True),IVORY);center(d,SCENES[i][1],719,ft(33,True),GOLD)
    center(d,SCENES[i][2],785,ft(16),IVORY);center(d,SCENES[i][3],815,ft(15),MUTE)
    d.line((30,888,510,888),fill=(77,70,56),width=2)
    d.rectangle((30,888,30+int(480*(t/SECONDS)),893),fill=GOLD)
    d.text((30,914),'EXPLANATORY ANIMATION · NOT EXPERIMENT FOOTAGE',font=ft(11),fill=MUTE)
    return im
def stamp(sec):return '00:00:%02d.000'%sec
def main():
    fp=BASE/'the-other-photograph-40s.mp4'
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','25','-pix_fmt','yuv420p','-movflags','+faststart',str(fp)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for n in range(SECONDS*FPS):p.stdin.write(frame(n/FPS).tobytes())
    p.stdin.close();ret=p.wait()
    if ret:raise RuntimeError(f'ffmpeg failed {ret}')
    frame(0).save(BASE/'poster.png')
    c=Image.new('RGB',(360*3,640*2),(10,13,13))
    for i,sec in enumerate(TIMES[:-1]):
        x=(i%3)*360;y=(i//3)*640
        c.paste(frame(sec).resize((360,640)),(x,y))
    c.save(BASE/'contact-sheet.png')
    cues=[]
    for i in range(6):
        lines=' '.join(SCENES[i][2:])
        cues.append(f'{i+1}\n{stamp(TIMES[i])} --> {stamp(TIMES[i+1])}\n{lines}\n')
    (BASE/'captions.vtt').write_text('WEBVTT\n\n'+'\n'.join(cues),encoding='utf-8')
    print('video',fp.stat().st_size,'bytes, sha256',hashlib.sha256(fp.read_bytes()).hexdigest())
if __name__=='__main__':main()
