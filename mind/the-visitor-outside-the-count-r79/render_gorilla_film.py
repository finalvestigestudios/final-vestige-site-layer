#!/usr/bin/env python3
"""Original silent 40s educational short, no copied footage, claims, or ads."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math, subprocess, hashlib, zipfile

HERE=Path(__file__).resolve().parent
W,H,FPS,DURATION=540,960,12,40
BG=(9,10,10); SURFACE=(19,21,20); GOLD=(199,166,108); TEXT=(244,239,230); MUTED=(175,166,150); GREEN=(122,161,139)
SANS='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
font=lambda sz,bold=False:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else SANS,sz)
serif=lambda sz:ImageFont.truetype(SERIF,sz)
STAGES=[
 (0,6,'THE INVISIBLE','VISITOR','A task can narrow what you notice.'),
 (6,13,'COUNT THE','LIGHT PASSES','Your attention has a job.'),
 (13,19,'AN UNEXPECTED','FIGURE','A new object crosses the scene.'),
 (19,26,'SOME OBSERVERS','MISS IT','That is inattentional blindness.'),
 (26,33,'EVEN EXPERTS','CAN MISS','A task changes what gets priority.'),
 (33,40,'A REPORT IS','NOT A CAMERA','Ask what the task allowed them to see.'),
]

def centered(d,text,y,f,fill,spacing=5):
 bb=d.textbbox((0,0),text,font=f,stroke_width=0)
 x=(W-(bb[2]-bb[0]))//2
 d.text((x,y),text,font=f,fill=fill,spacing=spacing)

def frame(t):
 idx=next(i for i,(a,b,*_) in enumerate(STAGES) if a<=t<b)
 a,b,l1,l2,caption=STAGES[idx]
 im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
 d.rectangle((34,34,W-34,H-34),outline=(59,54,47),width=2)
 d.line((65,110,W-65,110),fill=GOLD,width=2)
 centered(d,'FINAL VESTIGE  /  MIND & PERCEPTION',67,font(17,True),GOLD)
 d.text((65,156),f'FIELD NOTE   {idx+1:02d} / 06',font=font(17,True),fill=GOLD)
 # Abstract original visual: six moving circular counters, a separate surprising diamond.
 cy=425
 for j in range(6):
  cx=110+j%3*160+int(16*math.sin(t*1.7+j))
  yy=335+j//3*165+int(21*math.cos(t*1.3+j*1.8))
  bright = j%2==0
  fill=GOLD if bright else (65,79,83)
  d.ellipse((cx-35,yy-35,cx+35,yy+35),fill=fill)
  d.text((cx-7,yy-17),'●' if bright else '·',font=font(22,True),fill=BG if bright else TEXT)
 if idx>=2:
  progress=max(0,min(1,(t-13)/13))
  x=-60+progress*660
  y=cy+int(12*math.sin(t))
  diamond=[(x,y-63),(x+52,y),(x,y+63),(x-52,y)]
  d.polygon(diamond,outline=GREEN,width=5)
  if idx>=3:
   centered(d,'OUTSIDE THE COUNT',628,font(15,True),GREEN)
 else:
  centered(d,'FOLLOW THE GOLD COUNTERS',628,font(15,True),GOLD)
 centered(d,l1,689,serif(42),TEXT)
 centered(d,l2,742,serif(43),GOLD)
 centered(d,caption,820,font(15),MUTED)
 d.rectangle((65,877,65+int((W-130)*(t/DURATION)),881),fill=GOLD)
 return im

def make():
 mp4=HERE/'the-visitor-outside-the-count-40s.mp4'
 proc=subprocess.Popen(['ffmpeg','-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','ultrafast','-crf','29','-pix_fmt','yuv420p','-movflags','+faststart',str(mp4)],stdin=subprocess.PIPE)
 for n in range(FPS*DURATION):
  proc.stdin.write(frame(n/FPS).tobytes())
 proc.stdin.close()
 if proc.wait(): raise RuntimeError('ffmpeg failed')
 frame(0).save(HERE/'poster.png')
 sheet=Image.new('RGB',(540*3,960*2),BG)
 for i,(a,_,*_) in enumerate(STAGES):sheet.paste(frame(a+2),(i%3*W,i//3*H))
 sheet.thumbnail((810,960))
 sheet.save(HERE/'contact-sheet.png')
 print(mp4.name,mp4.stat().st_size,'SHA256',hashlib.sha256(mp4.read_bytes()).hexdigest())

if __name__=='__main__':make()
