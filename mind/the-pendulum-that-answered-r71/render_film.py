#!/usr/bin/env python3
"""Final Vestige R71 original offline educational short. Python/Pillow + local FFmpeg."""
from PIL import Image, ImageDraw, ImageFont
from math import sin, cos, pi
import subprocess, pathlib, sys
OUT=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else pathlib.Path('.')
OUT.mkdir(parents=True,exist_ok=True)
W,H,FPS,SECONDS=540,960,12,40
BG=(11,15,16); CREAM=(243,234,218); GOLD=(211,176,109); MUTED=(183,174,158)
FONTS="/usr/share/fonts/truetype/dejavu/"
serif=ImageFont.truetype(FONTS+"DejaVuSerif.ttf",24)
big=ImageFont.truetype(FONTS+"DejaVuSerif.ttf",35)
sans=ImageFont.truetype(FONTS+"DejaVuSans.ttf",19)
small=ImageFont.truetype(FONTS+"DejaVuSans.ttf",13)
SCENES=[
("THE QUESTION","A small weight hangs\nfrom a thread.\nYou think of a circle.",0,7),
("THE MOVEMENT","It begins to move.\nYou never felt a command.",7,14),
("THE AMPLIFIER","A tiny muscle adjustment\nbecomes a visible swing.",14,21),
("THE INTERPRETATION","Motion is observable.\nIts meaning is a hypothesis.",21,28),
("THE TEST","Change the conditions.\nCompare answers with guesses.",28,35),
("THE LIMIT","A pendulum can move\nwithout knowing.",35,40)
]
def center_lines(d,lines,y,font,color,spacing=18):
    for line in lines.split('\n'):
        box=d.textbbox((0,0),line,font=font)
        d.text(((W-box[2])/2,y),line,font=font,fill=color)
        y+=box[3]-box[1]+spacing
def frame(n):
    t=n/FPS
    idx=next((i for i,s in enumerate(SCENES) if s[2]<=t<s[3]),5)
    title,words,start,end=SCENES[idx]
    im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
    # Fine archival grid, no external assets or fonts distributed
    for x in range(40,W,46):d.line([(x,0),(x,H)],fill=(27,29,27),width=1)
    for y in range(30,H,46):d.line([(0,y),(W,y)],fill=(27,29,27),width=1)
    d.line([(35,80),(W-35,80)],fill=(112,94,58),width=2)
    center_lines(d,"F I N A L  V E S T I G E",39,small,GOLD,4)
    d.text((36,108),"M I N D  &  P E R C E P T I O N",font=small,fill=GOLD)
    center_lines(d,title,180,big,CREAM,20)
    # The moving pendulum is an illustration rather than instrument data
    origin=(W//2,335)
    amplitude=(0.04 if idx==0 else (.25 if idx<4 else .15))
    angle=amplitude*sin(t*2.5+0.35)
    length=248
    tip=(round(origin[0]+length*sin(angle)),round(origin[1]+length*cos(angle)))
    d.ellipse((origin[0]-4,origin[1]-4,origin[0]+4,origin[1]+4),fill=GOLD)
    d.line((origin,tip),fill=GOLD,width=3)
    d.ellipse((tip[0]-22,tip[1]-22,tip[0]+22,tip[1]+22),fill=GOLD,outline=CREAM,width=3)
    d.arc((origin[0]-120,origin[1]+130,origin[0]+120,origin[1]+370),25,155,fill=(94,80,54),width=2)
    d.line([(55,663),(485,663)],fill=(116,98,68),width=1)
    center_lines(d,words,699,serif,CREAM,13)
    d.text((35,884),"ILLUSTRATION · NOT EXPERIMENTAL FOOTAGE",font=small,fill=MUTED)
    d.rectangle((35,916,505,923),fill=(56,54,44))
    d.rectangle((35,916,35+int(470*(n+1)/(FPS*SECONDS)),923),fill=GOLD)
    d.text((35,932),f"{int(t):02d} / 40 SEC  ·  EDUCATIONAL SHORT",font=small,fill=MUTED)
    return im
poster=frame(36)
poster.save(OUT/"poster.png",optimize=True)
cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24',
     '-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','-','-c:v','libx264','-preset','ultrafast',
     '-pix_fmt','yuv420p','-crf','28','-movflags','+faststart','-an',str(OUT/"pendulum-that-answered-40s.mp4")]
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
for n in range(FPS*SECONDS):
    proc.stdin.write(frame(n).tobytes())
proc.stdin.close()
if proc.wait()!=0:raise RuntimeError("ffmpeg rendering failed")
print(f"Rendered {FPS*SECONDS} frames ({SECONDS}s) at {W}x{H}.")
