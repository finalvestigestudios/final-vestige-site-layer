"""FV Mind R66 — original silent 40-second six-scene educational film.
No copyrighted experiment footage, no third-party media, no merchant creative.
Requires Pillow and ffmpeg; writes PNG stills and a captioned-source MP4 (captions separate VTT).
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess, textwrap

OUT=Path(__file__).resolve().parent
W,H=540,960
CREAM=(240,233,217); GOLD=(229,192,124); INK=(12,22,26)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'

def font(size,bold=False,serif=False):
    return ImageFont.truetype(SERIF if serif else BOLD if bold else FONT,size)

def center(d,text,y,size,color=CREAM,bold=False,serif=False):
    f=font(size,bold,serif)
    box=d.textbbox((0,0),text,font=f)
    d.text(((W-box[2])/2,y),text,font=f,fill=color)

def person(d,x,y,color):
    d.ellipse((x-17,y-70,x+17,y-36),fill=color)
    d.rounded_rectangle((x-21,y-31,x+21,y+70),radius=18,fill=color)
    d.line((x-14,y+57,x-27,y+108),fill=color,width=13)
    d.line((x+14,y+57,x+27,y+108),fill=color,width=13)

def frame(i):
    im=Image.new('RGB',(W,H),INK);d=ImageDraw.Draw(im)
    d.rectangle((20,20,W-20,H-20),outline=(112,116,107),width=2)
    d.rounded_rectangle((49,91,491,640),radius=15,fill=(24,43,47),outline=(184,156,99),width=3)
    d.rectangle((65,122,475,562),fill=(47,75,81))
    d.rectangle((65,122,177,562),fill=(104,53,60))
    d.rectangle((363,122,475,562),fill=(104,53,60))
    d.line((65,250,475,250),fill=(70,89,88),width=3)
    center(d,'FINAL VESTIGE STUDIOS',45,16,GOLD,True)
    msgs=[('ONE TASK','Count the passes.'),('THE SURPRISE','You know what to expect.'),('BEHIND THE SCENE','The curtain changes.'),('ANOTHER ABSENCE','A player walks away.'),('ATTENTION SELECTS','A second look needs a new question.'),('THE OTHER CHANGE','Evidence before certainty.')]
    headline,sub=msgs[i]
    if i in (0,1,2,3):
        for x,y,c in ((190,260,(215,213,194)),(330,300,(220,210,188)),(252,418,(207,225,205))): person(d,x,y,c)
        d.ellipse((250,302,292,344),fill=(222,180,95))
    if i==1:
        d.ellipse((244,161,296,214),fill=(22,31,31))
        d.rounded_rectangle((236,207,305,355),radius=28,fill=(22,31,31))
    if i==2:
        d.rectangle((65,122,177,562),fill=(188,149,70))
        for y in range(136,549,31): d.line((81,y,164,y),fill=(205,175,102),width=1)
    if i==3:
        d.polygon([(333,264),(374,264),(418,328),(374,393),(333,393)],fill=(33,54,59))
        d.line((315,249,315,490),fill=(235,202,143),width=6)
        d.line((305,477,326,490),fill=(235,202,143),width=6)
    if i==4:
        for x,y in ((150,190),(350,190),(150,430),(350,430)):
            d.ellipse((x-35,y-35,x+35,y+35),outline=(117,163,161),width=5)
        d.ellipse((225,257,320,352),outline=GOLD,width=9)
        d.line((225,305,320,305),fill=GOLD,width=6)
    if i==5:
        d.rectangle((96,169,444,489),fill=(20,45,44),outline=GOLD,width=2)
        for n,(t,col) in enumerate((('LOOK',CREAM),('CHECK',GOLD),('REVISIT',CREAM))):
            center(d,t,215+n*85,48,col,True)
    center(d,headline,681,31,GOLD,True)
    wrapped=textwrap.wrap(sub,width=31)
    for n,line in enumerate(wrapped):center(d,line,741+n*39,25,CREAM,serif=True)
    center(d,f'0{i+1} / 06  •  ORIGINAL EDUCATIONAL FILM',892,13,(178,191,178),True)
    return im

for i in range(6):frame(i).save(OUT/f'scene-{i+1:02}.png',optimize=True)
frame(0).save(OUT/'poster.png',optimize=True)
with (OUT/'concat.txt').open('w') as f:
    for i,duration in enumerate([7,7,6,7,7,6],1):
        f.write(f"file 'scene-{i:02}.png'\nduration {duration}\n")
    f.write("file 'scene-06.png'\n")
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-safe','0','-f','concat','-i',str(OUT/'concat.txt'),'-vf','fps=12,format=yuv420p','-r','12','-t','40','-c:v','libx264','-preset','veryfast','-crf','27','-movflags','+faststart',str(OUT/'the-other-change-40s.mp4')],check=True)
