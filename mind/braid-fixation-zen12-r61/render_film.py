#!/usr/bin/env python3
"""R61 original James Braid and Zen12 evidence short, 40 seconds, no third-party assets."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess

OUT = Path(__file__).resolve().parent
W,H,FPS=540,960,12
DURATIONS=[6,7,7,7,7,6]
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
 scene(1,'Manchester, 1841.','A surgeon saw strange behavior at a public demonstration.',lambda d:(d.rectangle((89,192,449,419),outline=GOLD,width=4),d.text((132,268),'1841',font=font(82,True),fill=FG))),
 scene(2,'An invisible force?','Mesmerists proposed a magnetic fluid transmitted by an operator.',lambda d:(d.ellipse((110,199,433,429),outline=GOLD,width=4),d.arc((140,215,400,425),0,280,fill=SKY,width=9))),
 scene(3,'Remove the magnet.','Braid considered whether fixed attention might explain an observation.',lambda d:(d.line((268,177,268,310),fill=GOLD,width=4),d.ellipse((230,300,306,376),fill=GOLD),d.arc((170,250,368,448),20,330,fill=FG,width=5))),
 scene(4,'Observation is not cause.','The unusual response might be real while the explanation was wrong.',lambda d:(d.text((76,220),'OBSERVED',font=font(39,True),fill=FG),d.line((77,289,460,289),fill=GOLD,width=5),d.text((76,333),'EXPLAINED?',font=font(37,True),fill=SKY))),
 scene(5,'Theories still compete.','Modern hypnosis science studies suggestion and subjective agency.',lambda d:(d.rectangle((89,195,446,420),outline=GOLD,width=3),d.line((110,240,423,240),fill=FG,width=3),d.line((110,285,400,285),fill=FG,width=3),d.line((110,330,367,330),fill=FG,width=3))),
 scene(6,'12 minutes is not proof.','A listening duration cannot validate a promised benefit. Check the sources.',lambda d:(d.arc((135,175,404,444),15,330,fill=GOLD,width=13),d.text((163,280),'12:00',font=font(52,True),fill=FG)))
]
listfile=OUT/'concat.txt'
with listfile.open('w') as f:
    for path,duration in zip(scenes,DURATIONS):
        f.write(f"file '{path.name}'\n")
        f.write(f"duration {duration}\n")
    f.write(f"file '{scenes[-1].name}'\n")
video=OUT/'the-magnet-disappeared-40s.mp4'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(listfile),'-vf',f'fps={FPS},format=yuv420p','-t','40','-c:v','libx264','-preset','veryfast','-crf','25','-movflags','+faststart',str(video)],check=True,cwd=OUT)
print(video)
