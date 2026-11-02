#!/usr/bin/env python3
"""Original 40-second Final Vestige Mind archive history film. Local Python/Pillow + ffmpeg."""
from PIL import Image, ImageDraw, ImageFont
from math import sin, cos, pi
import pathlib, subprocess, sys
OUT=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else pathlib.Path('.')
OUT.mkdir(parents=True,exist_ok=True)
W,H,FPS,SECONDS=540,960,12,40
BG=(10,18,22); CREAM=(244,235,216); GOLD=(218,186,118); MUTED=(191,181,158)
FONTS='/usr/share/fonts/truetype/dejavu/'
serif=ImageFont.truetype(FONTS+'DejaVuSerif.ttf',23)
big=ImageFont.truetype(FONTS+'DejaVuSerif.ttf',31)
sans=ImageFont.truetype(FONTS+'DejaVuSans.ttf',17)
small=ImageFont.truetype(FONTS+'DejaVuSans.ttf',12)
SCENES=[
('THE RESPONSE','A striking response appears.\nThe operator calls it magnetism.',0,7),
('THE QUESTION','Braid asks: could attention\nand circumstances explain it?',7,14),
('THE DISTINCTION','The experience can be real.\nIts cause is still a hypothesis.',14,21),
('THE COMPARISON','Move the conditions.\nMeasure what actually changes.',21,28),
('THE LABORATORY','Modern studies test specific\nsuggestions—not universal powers.',28,35),
('THE STANDARD','Separate the event, the cause,\nand the promise being sold.',35,40)
]
def lines(d,txt,y,font,color,space=15):
 for line in txt.split('\n'):
  box=d.textbbox((0,0),line,font=font)
  d.text(((W-(box[2]-box[0]))/2,y),line,font=font,fill=color)
  y+=box[3]-box[1]+space

def frame(n):
 t=n/FPS;idx=next((i for i,s in enumerate(SCENES) if s[2]<=t<s[3]),5)
 title,subtitle,_,_=SCENES[idx]
 im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
 for x in range(28,W,40):d.line((x,0,x,H),fill=(24,34,35),width=1)
 for y in range(23,H,40):d.line((0,y,W,y),fill=(24,34,35),width=1)
 d.line((38,83,W-38,83),fill=(121,101,66),width=2)
 lines(d,'F I N A L  V E S T I G E',38,small,GOLD,4)
 d.text((38,107),'M I N D   /   H I S T O R Y  O F  S U G G E S T I O N',font=small,fill=GOLD)
 lines(d,title,178,big,CREAM,18)
 # Concentric historical observation field with a changing luminous fixation point
 center=(270,459)
 for r in (132,100,70):
  color=(66,68,60) if r==132 else (96,79,52) if r==100 else (154,119,62)
  d.ellipse((center[0]-r,center[1]-r,center[0]+r,center[1]+r),outline=color,width=2)
 a=t*.45
 px=round(center[0]+35*sin(a));py=round(center[1]+35*cos(a))
 d.ellipse((px-10,py-10,px+10,py+10),fill=GOLD,outline=CREAM,width=2)
 if idx>=2:
  d.line([(center[0]-130,622),(center[0]+130,622)],fill=GOLD,width=1)
  for j,label in enumerate(['EVENT','CAUSE','PROMISE']):
   x=94+175*j
   d.ellipse((x-8,612,x+8,628),outline=GOLD,width=2)
   d.text((x-34,648),label,font=small,fill=MUTED)
 d.line((45,692,495,692),fill=(124,100,64),width=1)
 lines(d,subtitle,721,serif,CREAM,13)
 d.text((36,876),'ORIGINAL ILLUSTRATION  /  NOT HISTORIC FOOTAGE',font=small,fill=MUTED)
 d.rectangle((36,916,504,924),fill=(56,55,48))
 d.rectangle((36,916,36+round(468*(n+1)/(FPS*SECONDS)),924),fill=GOLD)
 d.text((36,934),f'{int(t):02d} / 40 SEC   /   EDUCATIONAL SHORT',font=small,fill=MUTED)
 return im
frame(24).save(OUT/'poster.png',optimize=True)
cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24',
 '-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','-','-c:v','libx264','-preset','ultrafast',
 '-pix_fmt','yuv420p','-crf','27','-movflags','+faststart','-an',str(OUT/'the-hypnotist-left-40s.mp4')]
p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
for n in range(FPS*SECONDS):p.stdin.write(frame(n).tobytes())
p.stdin.close()
if p.wait()!=0:raise RuntimeError('ffmpeg render failure')
print(f'Original history film rendered: {FPS*SECONDS} frames, {SECONDS}.000 seconds')
