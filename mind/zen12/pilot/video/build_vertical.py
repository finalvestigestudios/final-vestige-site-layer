#!/usr/bin/env python3
"""Original 9:16 large-type 40-second companion to the 16:9 Zen12 evidence film.
No audio, product footage, external artwork, science simulations or paid assets.
"""
import argparse, math, subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
W,H,FPS,DURATION=540,960,15,40
BG='#090b0b';WHITE='#f4efe6';GOLD='#c7a66c';TEXT='#d8d2c7';MUTED='#aaa49a';PANEL='#181a18'
REG='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
def f(p,s):return ImageFont.truetype(p,s)
def center(d,s,y,size,color=WHITE,face=SERIF):
 font=f(face,size);b=d.textbbox((0,0),s,font=font)
 d.text(((W-b[2]+b[0])/2,y),s,font=font,fill=color)
def frame(t):
 im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
 d.rectangle((20,24,W-20,H-24),outline='#534631',width=2)
 d.text((40,52),'FINAL VESTIGE',fill=GOLD,font=f(BOLD,20))
 d.text((40,86),'MIND / FIELD STUDY',fill=MUTED,font=f(REG,16))
 d.line((40,126,500,126),fill='#574c3d',width=1)
 d.rectangle((40,142,40+int(460*t/40),146),fill=GOLD)
 if t<8:
  center(d,'THE HOUR',250,48)
  center(d,'YOU NEVER FIND',326,44,GOLD)
  center(d,'An impossible schedule',470,26,face=REG)
  center(d,'is not a practice.',512,26,face=REG)
  for i in range(12):
   x=61+(i%6)*75;y=637+(i//6)*51
   d.rounded_rectangle((x,y,x+53,y+29),radius=8,fill=GOLD if i>9 else '#38342d')
  center(d,'What could fit today?',777,28,face=REG)
 elif t<16:
  center(d,'TWELVE',220,60,GOLD)
  center(d,'MINUTES',302,60,GOLD)
  center(d,'IS STILL TIME',402,43)
  phase=(t-8)/8
  for i in range(12):
   a=-math.pi/2+i*math.pi/6;x=270+147*math.cos(a);y=619+147*math.sin(a)
   r=14 if i<=round(phase*11) else 9
   d.ellipse((x-r,y-r,x+r,y+r),fill=GOLD if i<=round(phase*11) else '#4a4339')
  center(d,'Shorter is not proof',812,24,face=REG)
  center(d,'of equivalent effects.',850,24,face=REG)
 elif t<24:
  center(d,'TRY THIS',246,60)
  center(d,'NOTICE',350,59,GOLD)
  center(d,'WANDER',439,59,GOLD)
  center(d,'RETURN',528,59,GOLD)
  q=(t-16)/8*math.pi*2;r=78+9*math.sin(q*2)
  d.ellipse((270-r,725-r,270+r,725+r),outline=GOLD,width=5)
  d.ellipse((260,715,280,735),fill=WHITE)
  center(d,'No score. Begin for free.',847,23,face=REG)
 elif t<32:
  center(d,'ZEN12',197,60)
  center(d,'12 LEVELS',279,46,GOLD)
  center(d,'4 LISTENING STYLES',349,32)
  labels=['GUIDED','MUSIC','NATURE','WHITE NOISE']
  for i,label in enumerate(labels):
   y=457+i*91
   d.rounded_rectangle((61,y,479,y+69),radius=12,fill=PANEL,outline='#66573d',width=2)
   center(d,label,y+18,30,face=BOLD)
  center(d,'Formats: seller-described.',852,22,face=REG)
  center(d,'Benefits: unverified.',883,22,GOLD,face=REG)
 else:
  center(d,'FOLLOW THE',194,44)
  center(d,'EVIDENCE',265,57,GOLD)
  center(d,'BEFORE THE',367,44)
  center(d,'PROMISE',436,57,GOLD)
  d.line((113,544,427,544),fill=GOLD,width=3)
  center(d,'Sources. Limits.',581,28,face=REG)
  center(d,'Free alternatives.',628,28,face=REG)
  center(d,'No active purchasing link.',721,24,face=REG)
  center(d,'Future qualifying links',773,22,GOLD,face=REG)
  center(d,'may earn a commission.',809,22,GOLD,face=REG)
 d.text((40,917),'Original illustration; not a product test',font=f(REG,16),fill=MUTED)
 return im

def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--poster',type=Path,required=True)
 a=p.parse_args();a.out.parent.mkdir(parents=True,exist_ok=True);a.poster.parent.mkdir(parents=True,exist_ok=True)
 frame(34).save(a.poster,optimize=True)
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','-','-c:v','libx264','-preset','fast','-crf','27','-pix_fmt','yuv420p','-movflags','+faststart','-an',str(a.out)]
 x=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 try:
  for i in range(DURATION*FPS):x.stdin.write(frame(i/FPS).tobytes())
  x.stdin.close();s=x.wait(timeout=120)
  if s:raise RuntimeError('ffmpeg '+str(s))
 finally:
  if x.poll() is None:x.kill()
 print(a.out,a.out.stat().st_size,a.poster,a.poster.stat().st_size)
if __name__=='__main__':main()
