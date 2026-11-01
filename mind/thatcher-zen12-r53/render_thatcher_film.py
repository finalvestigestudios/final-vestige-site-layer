"""Original silent educational storyboard film; source material is schematic, not experimental stimuli.
Repro: python render_thatcher_film.py. Requires Pillow and ffmpeg.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import subprocess, math
BASE=Path(__file__).resolve().parent
W,H=540,960
BG='#0C0F10'; GOLD='#C8A56B'; WHITE='#F4EDE1'; MUTED='#B7B0A4'; ACC='#4A4236'
FONTS='/usr/share/fonts/truetype/dejavu'
serif=lambda n: ImageFont.truetype(f'{FONTS}/DejaVuSerif.ttf',n)
sans=lambda n: ImageFont.truetype(f'{FONTS}/DejaVuSans.ttf',n)
bold=lambda n: ImageFont.truetype(f'{FONTS}/DejaVuSans-Bold.ttf',n)
def face(d, cx,cy, inverted=False, altered=False, scale=1):
    # Original symbolic facial drawing; not a photo or a scientific visual stimulus.
    x=lambda a:cx+a*scale;y=lambda b:cy+b*scale
    d.ellipse((x(-100),y(-142),x(100),y(135)),outline=GOLD,width=4)
    d.polygon([(x(-75),y(-120)),(x(-25),y(-165)),(x(45),y(-150)),(x(88),y(-112))],outline=GOLD)
    if not altered:
        for off in [-48,48]:
            d.arc((x(off-27),y(-45),x(off+27),y(-8)),0,180,fill=WHITE,width=4)
        d.arc((x(-48),y(30),x(48),y(90)),0,180,fill=WHITE,width=5)
    else:
        # Locally flip the expressive features, preserving face outline.
        for off in [-48,48]:
            d.arc((x(off-27),y(-45),x(off+27),y(-8)),180,360,fill=WHITE,width=4)
        d.arc((x(-48),y(30),x(48),y(90)),180,360,fill=WHITE,width=5)
    d.line((x(0),y(-5),x(-13),y(23),x(12),y(23)),fill=MUTED,width=3)
def write_center(d,txt,y,font,color=WHITE):
    box=d.textbbox((0,0),txt,font=font);d.text(((W-(box[2]-box[0]))/2,y),txt,font=font,fill=color)
def frame(i):
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
    d.rectangle((30,28,W-30,H-30),outline=ACC,width=2)
    d.text((50,60),'FINAL VESTIGE / MIND & PERCEPTION',font=bold(15),fill=GOLD)
    d.line((48,110,W-48,110),fill=ACC,width=2)
    if i==0:
        write_center(d,'THE FACE',145,serif(42));write_center(d,'THAT CHANGED',205,serif(42))
        face(d,270,500,altered=True,scale=1.2)
        write_center(d,'NOT A REAL PARTICIPANT TEST',830,bold(16),GOLD)
    if i==1:
        write_center(d,'1980',166,serif(76),GOLD);write_center(d,'PETER THOMPSON',300,bold(29))
        write_center(d,'A face seemed less strange',430,sans(23));write_center(d,'when viewed upside down.',474,sans(23))
        write_center(d,'FIRST REPORT: PERCEPTION 9, 483-484',810,sans(14),MUTED)
    if i==2:
        write_center(d,'THE CHANGE',175,serif(40));face(d,270,480,altered=True,scale=1.35)
        write_center(d,'Eyes and mouth reversed',755,sans(24),GOLD);write_center(d,'inside an upright face.',799,sans(24))
    if i==3:
        write_center(d,'TURN THE WHOLE FACE',185,serif(34))
        # in the film these are schematic rotated faces, not actual stimuli
        small=Image.new('RGBA',(310,350),(0,0,0,0));q=ImageDraw.Draw(small)
        face(q,155,175,altered=True,scale=.95)
        im.paste(small.rotate(180),(115,325),small.rotate(180))
        d=ImageDraw.Draw(im)
        write_center(d,'Judging the difference changes',770,sans(21));write_center(d,'when orientation changes.',810,sans(21))
    if i==4:
        write_center(d,'NOT A MAGIC TRICK',210,serif(35));write_center(d,'Face perception depends',405,sans(26));write_center(d,'on orientation and',450,sans(26));write_center(d,'relationships among features.',495,sans(24));write_center(d,'Different people respond differently.',745,sans(18),GOLD)
    if i==5:
        write_center(d,'WHAT DID YOU',230,serif(40));write_center(d,'NOT COMPARE?',285,serif(40));write_center(d,'One glance is not the whole record.',490,sans(23));write_center(d,'FOLLOW THE EVIDENCE',710,bold(24),GOLD);write_center(d,'finalvestige.com',760,sans(22))
    d.text((55,880),f'{i+1:02d}  /  06',font=sans(18),fill=MUTED)
    return im
for i in range(6): frame(i).save(BASE/f'frame-{i+1:02d}.png')
frame(0).save(BASE/'film-poster.png')
with (BASE/'frames.txt').open('w') as f:
    for i in range(6):
        f.write(f"file 'frame-{i+1:02d}.png'\nduration {40/6:.9f}\n")
    f.write("file 'frame-06.png'\n")
subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(BASE/'frames.txt'),'-vsync','cfr','-r','12','-frames:v','480','-c:v','libx264','-pix_fmt','yuv420p','-movflags','+faststart',str(BASE/'thatcher-40s.mp4')],check=True)
print('Rendered',BASE/'thatcher-40s.mp4')
