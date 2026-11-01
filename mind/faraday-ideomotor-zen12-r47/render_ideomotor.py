#!/usr/bin/env python3
"""Original Final Vestige evidence film. Offline review only; no external media."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import subprocess, math

W,H,FPS,DURATION=540,960,12,40
OUT=Path(__file__).resolve().parent
BGC=(11,13,15); GOLD=(198,161,99); CREAM=(244,236,217); MUTED=(177,179,175); LINE=(67,66,59)
SANS='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
scenes=[
 ('1853 · THE EXPERIMENT','THE TABLE\nMOVED.','London. A table seemed to turn\nwithout anyone intending it.'),
 ('THE CLAIM','AN UNSEEN\nFORCE?','Participants said the table\npulled their hands along.'),
 ('THE INSTRUMENT','A SMALL\nINDICATOR.','Faraday devised a lever to tell\nwhich moved first.'),
 ('THE CONTROL','WATCH THE\nNEEDLE.','With the indicator visible,\nthe movement diminished.'),
 ('THE RESULT','THE HAND\nLED.','Unnoticed pressure appeared\nbefore the table shifted.'),
 ('WHAT WE CAN SAY','FEELING IS\nNOT PROOF.','Movement was real. The claimed\ncause needed a better test.')]

def font(size,serif=False): return ImageFont.truetype(SERIF if serif else SANS,size)

def centered(d,xy,text,f,fill,spacing=10):
 lines=text.split('\n'); y=xy[1]
 for line in lines:
  box=d.textbbox((0,0),line,font=f); width=box[2]-box[0]
  d.text(((W-width)//2,y),line,font=f,fill=fill,stroke_width=0)
  y+=f.size+spacing

def draw_card(idx):
 im=Image.new('RGB',(W,H),BGC); d=ImageDraw.Draw(im)
 d.rectangle((24,25,516,935),outline=(42,44,43),width=2)
 d.text((46,58),'FINAL VESTIGE  /  MIND & PERCEPTION',font=font(16),fill=GOLD)
 d.line((46,93,494,93),fill=LINE,width=2)
 tag,title,explain=scenes[idx]
 d.text((46,141),tag,font=font(19),fill=GOLD)
 centered(d,(0,192),title,font(50,True),CREAM,9)
 # unique conceptual diagram in reserved stage
 if idx in (0,1):
  d.ellipse((113,475,427,533),outline=GOLD,width=5)
  d.line((155,516,165,670),fill=(130,126,110),width=7)
  d.line((377,516,367,670),fill=(130,126,110),width=7)
  d.line((220,460,236,502),fill=CREAM,width=9); d.line((321,460,305,502),fill=CREAM,width=9)
  if idx==1:
   d.arc((150,393,390,572),195,325,fill=GOLD,width=5)
   d.polygon([(382,424),(387,455),(363,441)],fill=GOLD)
 elif idx in (2,3):
  d.ellipse((117,470,423,530),outline=GOLD,width=5)
  d.line((185,495,361,495),fill=CREAM,width=8)
  d.ellipse((259,484,281,506),fill=GOLD)
  d.line((270,495,340 if idx==2 else 280,395),fill=GOLD,width=6)
  d.text((100,607),'HANDS',font=font(19),fill=MUTED)
  d.text((348,607),'TABLE',font=font(19),fill=MUTED)
  d.line((136,590,236,510),fill=LINE,width=3)
  d.line((395,590,341,529),fill=LINE,width=3)
 elif idx==4:
  d.line((105,525,435,525),fill=LINE,width=6)
  d.ellipse((165,485,215,535),fill=GOLD)
  d.ellipse((337,485,387,535),fill=CREAM)
  d.line((235,505,317,505),fill=GOLD,width=5)
  d.polygon([(317,505),(301,493),(301,517)],fill=GOLD)
  d.text((110,583),'HAND  →',font=font(22),fill=GOLD)
  d.text((330,583),'TABLE',font=font(22),fill=CREAM)
 else:
  d.ellipse((205,462,335,592),outline=GOLD,width=5)
  d.text((252,493),'?',font=font(60,True),fill=CREAM)
  d.line((145,635,395,635),fill=GOLD,width=4)
 centered(d,(0,727),explain,font(23),MUTED,11)
 d.text((46,882),'FARADAY, 1853  •  SOURCE-LED EXPLAINER',font=font(13),fill=GOLD)
 return im


def main():
 panels=[draw_card(i) for i in range(6)]
 panels[0].save(OUT/'faraday-film-poster.png',optimize=True)
 process=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','25','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'faraday-40s.mp4')],stdin=subprocess.PIPE)
 try:
  for frame in range(FPS*DURATION):
   idx=min(5,frame*6//(FPS*DURATION)); im=panels[idx].copy(); d=ImageDraw.Draw(im)
   prog=frame/(FPS*DURATION-1)
   d.rounded_rectangle((46,844,494,849),radius=2,fill=(57,56,51))
   d.rounded_rectangle((46,844,46+max(4,int(448*prog)),849),radius=2,fill=GOLD)
   process.stdin.write(im.tobytes())
 finally:
  process.stdin.close()
  if process.wait()!=0:raise RuntimeError('ffmpeg failed')
 print('finished',OUT/'faraday-40s.mp4')
if __name__=='__main__':main()
