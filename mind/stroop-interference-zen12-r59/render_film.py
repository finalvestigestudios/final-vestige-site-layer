#!/usr/bin/env python3
"""Reproducible six-card, original silent 40s educational film. No stock assets."""
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
 scene(1,'The word is not the ink.','A familiar word can compete with the answer you were asked to give.',lambda d:d.text((45,255),'RED',font=font(142,True),fill=SKY)),
 scene(2,'An experiment, 1935.','J. Ridley Stroop compared defined reading and color-naming tasks.',lambda d:(d.rectangle((75,215,450,425),fill='#1C201E',outline=GOLD,width=3),d.text((105,257),'1935',font=font(93,True),fill=GOLD))),
 scene(3,'Compare the tasks.','Group means for naming 100 colors: 63.3 s vs 110.3 s in Stroop\'s experiment.',lambda d:(d.text((60,225),'63.3 s',font=font(65,True),fill=GOLD),d.text((60,350),'110.3 s',font=font(65,True),fill=SKY))),
 scene(4,'Not a diagnosis.','A task-specific delay does not measure someone\'s intelligence or clinical condition.',lambda d:(d.ellipse((170,225,370,425),outline=GOLD,width=9),d.line((197,253,345,398),fill=GOLD,width=10))),
 scene(5,'Twelve minutes is time.','Duration of a listening session is not proof of any particular meditation benefit.',lambda d:(d.arc((145,180,395,430),20,320,fill=GOLD,width=17),d.text((174,276),'12:00',font=font(52,True),fill=FG))),
 scene(6,'Sources before promises.','Read the evidence. Try a free exercise. Decide what fits you.',lambda d:(d.line((100,250,440,250),fill=GOLD,width=3),d.text((138,290),'FV',font=font(111,serif=True),fill=GOLD)))
]
listfile=OUT/'concat.txt'
with listfile.open('w') as f:
    for path,duration in zip(scenes,DURATIONS):
        f.write(f"file '{path.name}'\n")
        f.write(f"duration {duration}\n")
    f.write(f"file '{scenes[-1].name}'\n")
video=OUT/'the-word-is-not-the-ink-40s.mp4'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(listfile),'-vf',f'fps={FPS},format=yuv420p','-t','40','-c:v','libx264','-preset','veryfast','-crf','25','-movflags','+faststart',str(video)],check=True,cwd=OUT)
print(video)
