#!/usr/bin/env python3
"""R60 original Coué and Zen12 claims short, 40 seconds, no third-party assets."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess

OUT = Path(__file__).resolve().parent
W,H,FPS=540,960,12
DURATIONS=[7,7,7,6,7,6]
SANS='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
FG='#F4EFE6'; GOLD='#D7B77E'; MUTED='#D2C9BA'; SKY='#72B8F2'

def font(sz,bold=False,serif=False):
    return ImageFont.truetype(SERIF if serif else BOLD if bold else SANS,sz)

def wrap(draw,txt,ft,maxw):
    lines=[]; line=''
    for word in txt.split():
        trial=(line+' '+word).strip()
        if line and draw.textbbox((0,0),trial,font=ft)[2] > maxw:
            lines.append(line);line=word
        else:line=trial
    if line:lines.append(line)
    return lines

def scene(n,heading,sub,draw_extra):
    im=Image.new('RGB',(W,H),'#090A0A');d=ImageDraw.Draw(im)
    d.rounded_rectangle((22,22,518,938),radius=8,fill='#111313',outline='#997d55',width=2)
    d.text((48,63),'FINAL VESTIGE / MIND',font=font(20,True),fill=GOLD)
    d.line((48,112,492,112),fill='#574c3d',width=2)
    draw_extra(d)
    y=617
    for line in wrap(d,heading,font(43,serif=True),440):
        d.text((48,y),line,font=font(43,serif=True),fill=FG); y+=59
    y+=10
    for line in wrap(d,sub,font(21),430):
        d.text((48,y),line,font=font(21),fill=MUTED);y+=35
    d.line((48,875,492,875),fill='#574c3d',width=2)
    d.text((48,894),f'{n:02d} / 06  |  ORIGINAL EDUCATIONAL CONCEPT',font=font(13,True),fill=GOLD)
    path=OUT/f'scene-{n:02d}.png'; im.save(path,optimize=True);return path

scenes=[
 scene(1,'A sentence can travel.','A phrase can spread farther than the evidence behind it.',lambda d:(d.line((72,230,440,230),fill=GOLD,width=5),d.text((73,292),'1922',font=font(94,True),fill=GOLD))),
 scene(2,'Nancy. A public method.','Brooks recorded a clinic and a formula that Coué taught.',lambda d:(d.rectangle((92,198,440,425),outline=GOLD,width=4),d.text((120,273),'NANCY',font=font(54,True),fill=FG))),
 scene(3,'Twenty repetitions.','A knotted cord helped count a brief spoken routine.',lambda d:(d.arc((90,185,430,425),10,320,fill=GOLD,width=9),d.ellipse((114,214,142,242),fill=FG),d.ellipse((355,317,383,345),fill=FG))),
 scene(4,'Witness is not proof.','An encouraging account is not a controlled clinical trial.',lambda d:(d.ellipse((164,213,380,429),outline=GOLD,width=9),d.line((186,244,345,396),fill=GOLD,width=10))),
 scene(5,'Twelve minutes is time.','Zen12 markets an hour-equivalence. Product-specific proof remains unestablished.',lambda d:(d.arc((145,180,395,430),20,320,fill=GOLD,width=17),d.text((174,276),'12:00',font=font(52,True),fill=FG))),
 scene(6,'Read. Try. Decide.','A free routine and an honest source trail come before any offer.',lambda d:(d.line((100,250,440,250),fill=GOLD,width=3),d.text((138,290),'FV',font=font(111,serif=True),fill=GOLD)))
]
listfile=OUT/'concat.txt'
with listfile.open('w') as f:
    for path,duration in zip(scenes,DURATIONS):
        f.write(f"file '{path.name}'\n")
        f.write(f"duration {duration}\n")
    f.write(f"file '{scenes[-1].name}'\n")
video=OUT/'the-sentence-and-the-cord-40s.mp4'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(listfile),'-vf',f'fps={FPS},format=yuv420p','-t','40','-c:v','libx264','-preset','veryfast','-crf','25','-movflags','+faststart',str(video)],check=True,cwd=OUT)
print(video)
