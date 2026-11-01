"""Render the original silent 40-second portrait short: Loftus & Palmer 1974.
Pillow and FFmpeg required; no external footage, music, SaaS or customer data.
Run from any directory: python render_memory_film.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from subprocess import run
import shutil

BASE = Path(__file__).resolve().parent
DIR = BASE / 'memory_film_stills'
DIR.mkdir(exist_ok=True)
W, H = 540, 960
BG=(10,12,12); PANEL=(20,23,22); PAPER=(244,239,230); GOLD=(199,166,108); MUTED=(199,191,178); LINE=(89,79,62)
SERIF = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
SANS = '/usr/share/fonts/truetype/lato/Lato-Medium.ttf'
BOLD = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'

def font(size, serif=False, bold=False):
    return ImageFont.truetype(SERIF if serif else BOLD if bold else SANS, size)

def text_center(draw, string, y, f, fill=PAPER):
    box=draw.textbbox((0,0),string,font=f)
    draw.text(((W-(box[2]-box[0]))/2,y),string,font=f,fill=fill)

def frame(n):
    im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
    d.rectangle((22,22,W-22,H-22),outline=LINE,width=2)
    d.line((48,112,W-48,112),fill=GOLD,width=2)
    d.text((48,57),'FINAL VESTIGE  /  MIND ARCHIVE',font=font(17,bold=True),fill=GOLD)
    d.text((48,902),'ORIGINAL EVIDENCE NOTE    |    1974',font=font(16),fill=MUTED)
    d.line((48,886,W-48,886),fill=LINE,width=2)
    d.text((48,855),f'PLATE 0{n+1}  /  06',font=font(15),fill=GOLD)
    return im,d

scenes=[]
for i in range(6):
    im,d=frame(i)
    if i==0:
        text_center(d,'THE FILM',271,font(51,serif=True))
        text_center(d,'NEVER CHANGED.',348,font(43,serif=True))
        d.rounded_rectangle((105,506,435,690),radius=6,fill=PANEL,outline=LINE,width=2)
        d.line((144,555,391,555),fill=GOLD,width=2)
        text_center(d,'ONE COLLISION',588,font(24,bold=True),GOLD)
        text_center(d,'TWO QUESTIONS',626,font(24,bold=True),PAPER)
    elif i==1:
        text_center(d,'THE QUESTION DID.',244,font(40,serif=True))
        d.rounded_rectangle((58,350,482,470),radius=5,outline=GOLD,width=2,fill=PANEL)
        text_center(d,'HIT',378,font(62,serif=True))
        d.rounded_rectangle((58,500,482,620),radius=5,outline=GOLD,width=2,fill=PANEL)
        text_center(d,'SMASHED',529,font(51,serif=True))
        text_center(d,'A SINGLE VERB',685,font(22,bold=True),MUTED)
    elif i==2:
        text_center(d,'ONE WEEK LATER',220,font(32,serif=True))
        d.rounded_rectangle((58,330,482,490),radius=5,outline=GOLD,fill=PANEL,width=2)
        text_center(d,'16 / 50',342,font(75,serif=True))
        text_center(d,'S M A S H E D  GROUP',444,font(17,bold=True),GOLD)
        d.rounded_rectangle((58,518,482,678),radius=5,outline=LINE,fill=PANEL,width=2)
        text_center(d,'7 / 50',530,font(75,serif=True))
        text_center(d,'H I T  GROUP',632,font(17,bold=True),GOLD)
        text_center(d,'REPORTED SEEING GLASS',725,font(21,bold=True),PAPER)
    elif i==3:
        text_center(d,'BUT THE FILM',254,font(44,serif=True))
        text_center(d,'SHOWED NONE.',327,font(44,serif=True))
        d.rectangle((92,485,448,689),outline=GOLD,width=2)
        d.line((124,585,416,585),fill=LINE,width=3)
        text_center(d,'NO GLASS',594,font(32,bold=True),GOLD)
        text_center(d,'IN THE ORIGINAL FILM',740,font(20),MUTED)
    elif i==4:
        text_center(d,'A REPORT',242,font(43,serif=True))
        text_center(d,'IS MEASURABLE.',308,font(38,serif=True))
        d.line((80,425,460,425),fill=GOLD,width=2)
        text_center(d,'A REWRITTEN',487,font(41,serif=True))
        text_center(d,'MEMORY IS',553,font(41,serif=True))
        text_center(d,'HARDER TO PROVE.',620,font(35,serif=True))
        text_center(d,'NO UNIVERSAL FAILURE RATE',741,font(18,bold=True),GOLD)
    else:
        text_center(d,'QUESTION',250,font(48,serif=True))
        text_center(d,'THE CLAIM.',325,font(48,serif=True))
        d.line((80,429,460,429),fill=GOLD,width=2)
        text_center(d,'READ THE STUDY.',494,font(33,serif=True),GOLD)
        text_center(d,'AUDIO-PRODUCT BENEFITS',620,font(21,bold=True),PAPER)
        text_center(d,'NEED THEIR OWN PROOF.',658,font(21,bold=True),PAPER)
        text_center(d,'Loftus & Palmer / 1974',770,font(19),MUTED)
    dest=DIR/f'plate-{i+1:02d}.png'; im.save(dest,optimize=True);scenes.append(dest)

durations=[6,6,7,6,8,7]
playlist=DIR/'shots.ffconcat'
playlist.write_text('ffconcat version 1.0\n'+''.join(f"file '{p.as_posix()}'\nduration {sec}\n" for p,sec in zip(scenes,durations))+f"file '{scenes[-1].as_posix()}'\n",encoding='utf-8')
out=BASE/'the-word-came-after-40s.mp4'
run(['ffmpeg','-hide_banner','-loglevel','error','-y','-safe','0','-f','concat','-i',str(playlist),'-vsync','cfr','-r','12','-vf','tpad=stop_mode=clone:stop_duration=0.25','-frames:v','480','-c:v','libx264','-preset','veryfast','-crf','25','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],check=True)
shutil.copy2(scenes[0],BASE/'the-word-came-after-poster.png')
print(out, out.stat().st_size)
