"""Reproducible local renderer for Final Vestige R50 original 40s silent educational film.
Requires Pillow and ffmpeg. No third-party image, video, voice or music assets.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess

OUT=Path(__file__).parent
W,H=540,960
SANS='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
CREAM=(239,231,213); GOLD=(211,174,113); MUTED=(174,164,146)
SCENES=[
 (7,'A FACE.','A SOUND.','The familiar clues of a human voice.','two'),
 (7,'BA','GA','Sound: “ba”   /   Mouth: “ga”','split'),
 (7,'SOME HEAR','“DA”','The recorded sound has not changed.','rings'),
 (7,'BUT NOT','EVERYONE.','The response depends on the viewer and test.','scatter'),
 (6,'EXPERIENCE','≠ PROOF','A vivid impression is not a product trial.','scale'),
 (6,'ASK WHAT','WAS TESTED.','Final Vestige · Evidence before claims','archive'),
]
def font(path,size): return ImageFont.truetype(path,size)
def center(draw,txt,y,ft,color=CREAM):
    box=draw.textbbox((0,0),txt,font=ft)
    draw.text(((W-(box[2]-box[0]))/2,y),txt,font=ft,fill=color)
def render_scene(i,scene):
    seconds,top,bottom,sub,kind=scene
    img=Image.new('RGB',(W,H));pix=img.load()
    for y in range(H):
        k=y/H
        base=(int(11+8*k),int(18+8*k),int(18+5*k))
        for x in range(W): pix[x,y]=base
    d=ImageDraw.Draw(img)
    for n in range(9):
        c=(30+n*2,43+n*2,42+n)
        d.arc((45-n*20,178-n*20,W-45+n*20,670+n*20),190,340,fill=c,width=2)
    d.line([(62,81),(W-62,81)],fill=(104,91,70),width=2)
    d.text((62,47),'FINAL VESTIGE   /   MIND & PERCEPTION',font=font(BOLD,13),fill=GOLD)
    if kind=='two':
        d.ellipse((97,250,232,385),outline=GOLD,width=5);d.ellipse((307,250,442,385),outline=GOLD,width=5)
        d.arc((130,287,198,347),10,165,fill=CREAM,width=5)
        for k in range(5):d.arc((326+k*6,286+k*7,415-k*6,356-k*7),200,340,fill=CREAM,width=3)
    elif kind=='split':
        d.rounded_rectangle((56,245,258,440),radius=24,outline=GOLD,width=4)
        d.rounded_rectangle((282,245,484,440),radius=24,outline=CREAM,width=4)
        center(d,'⇄',333,font(BOLD,44),GOLD)
    elif kind=='rings':
        for radius in (38,77,118,158):d.ellipse((270-radius,339-radius,270+radius,339+radius),outline=(103+int(radius*.3),94+int(radius*.2),73),width=4)
        center(d,'?',297,font(BOLD,64),CREAM)
    elif kind=='scatter':
        for x,y in [(90,308),(150,396),(240,275),(300,362),(408,288),(460,422),(212,455)]:
            d.ellipse((x-11,y-11,x+11,y+11),fill=GOLD if x%3 else MUTED)
        d.line([(90,308),(150,396),(240,275),(300,362),(408,288),(460,422)],fill=(110,91,67),width=3)
    elif kind=='scale':
        d.line((270,246,270,456),fill=GOLD,width=5);d.line((140,298,401,298),fill=GOLD,width=5)
        d.line((170,298,145,384),fill=CREAM,width=2);d.line((368,298,395,384),fill=CREAM,width=2)
        d.arc((108,367,181,413),0,180,fill=CREAM,width=5);d.arc((359,367,432,413),0,180,fill=CREAM,width=5)
    else:
        for y in range(251,422,36):d.line([(124,y),(417,y)],fill=(92,81,63),width=3)
        d.rectangle((124,251,417,422),outline=GOLD,width=4)
        d.text((170,317),'FV',font=font(SERIF,77),fill=CREAM)
    center(d,top,531,font(BOLD,39),GOLD)
    center(d,bottom,585,font(SERIF,57),CREAM)
    # Two-line caption fitting
    if len(sub)>46:
        parts=sub.rsplit(' ',maxsplit=5)
        cut=max([j for j in range(1,len(sub)) if sub[j]==' ' and j < len(sub)*.62],default=0)
        center(d,sub[:cut],711,font(SANS,19),MUTED);center(d,sub[cut:].strip(),740,font(SANS,19),MUTED)
    else:center(d,sub,721,font(SANS,20),MUTED)
    d.line([(62,854),(W-62,854)],fill=(104,91,70),width=2)
    d.text((62,874),'ORIGINAL EDUCATIONAL FILM',font=font(BOLD,13),fill=GOLD)
    d.text((425,874),f'{i+1:02}/06',font=font(BOLD,13),fill=CREAM)
    p=OUT/f'scene-{i+1:02}.png';img.save(p,optimize=True);return p

paths=[render_scene(i,s) for i,s in enumerate(SCENES)]
(OUT/'poster.png').write_bytes(paths[0].read_bytes())
with (OUT/'concat.txt').open('w') as f:
    for p,s in zip(paths,SCENES):
        f.write(f"file '{p.name}'\nduration {s[0]}\n")
    f.write(f"file '{paths[-1].name}'\n")
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(OUT/'concat.txt'),'-vf','fps=12,format=yuv420p','-t','40','-c:v','libx264','-preset','veryfast','-crf','25','-movflags','+faststart',str(OUT/'mcgurk-concept-40s.mp4')],check=True,cwd=OUT)
print('rendered:',OUT/'mcgurk-concept-40s.mp4')
