#!/usr/bin/env python3
"""Offline-only original explanatory animation; no third-party footage or audio."""
from PIL import Image, ImageDraw, ImageFont
import math, os, subprocess
W,H,FPS,DURATION=540,960,12,40
OUT=os.path.dirname(os.path.abspath(__file__))
COLORS={"ink":(8,16,31),"gold":(242,191,111),"white":(244,246,251),"teal":(97,229,217),"muted":(165,182,204)}
SCENES=[
 (0,7,"TWO TONES",["One sound in each ear.","A beat appears between them."],"The percept is real."),
 (7,14,"THE PHANTOM BEAT",["Different frequencies can", "produce a rhythmic impression."],"Perception is not a diagnosis."),
 (14,20,"1973 / GERALD OSTER",["A strange auditory effect", "became a scientific probe."],"Not a wellness trial."),
 (20,27,"DOES THE BRAIN FOLLOW?",["A heard rhythm does not", "prove global EEG entrainment."],"That is a separate hypothesis."),
 (27,34,"14 STUDIES / 2023",["Five supported entrainment.","Eight did not. One mixed."],"Methods varied considerably."),
 (34,40,"ASK FOR THE TEST",["What was measured?", "Was the named audio tested?"],"A promise is not a finding.")]
REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font=lambda p,n:ImageFont.truetype(p,n)
TITLE=font(BOLD,38); MAIN=font(BOLD,33); BODY=font(REG,26); SMALL=font(REG,19)

def frame(i):
 t=i/FPS
 im=Image.new('RGB',(W,H),COLORS['ink']); d=ImageDraw.Draw(im)
 for y in range(H):
  c=(8+int(5*y/H),16+int(4*y/H),31+int(13*y/H))
  d.line((0,y,W,y),fill=c)
 for j in range(27):
  x=(j*127+61)%W; y=(j*223+73)%H
  d.ellipse((x,y,x+2,y+2),fill=(42,66,85))
 idx=next(k for k,s in enumerate(SCENES) if s[0]<=t<s[1])
 start,end,title,body,foot=SCENES[idx]
 local=(t-start)/(end-start)
 d.rounded_rectangle((34,53,506,98),radius=20,outline=COLORS['gold'],width=2)
 d.text((W/2,76),'FINAL VESTIGE / MIND ARCHIVE',anchor='mm',font=SMALL,fill=COLORS['gold'])
 d.text((W/2,183),title,anchor='mm',font=TITLE,fill=COLORS['white'])
 d.line((60,226,480,226),fill=(68,94,114),width=2)
 # Two tones move independently, while dashed center line represents a perceived beat.
 for ch,base in [(0,328),(1,427)]:
  pts=[]
  for x in range(54,487,3):
   phase=x*(.064 if ch==0 else .073)-t*(3.2 if ch==0 else 3.5)
   pts.append((x,int(base+39*math.sin(phase))))
  d.line(pts,fill=COLORS['teal'] if ch==0 else COLORS['gold'],width=4)
  d.text((56,base-68),'L' if ch==0 else 'R',font=SMALL,fill=COLORS['muted'])
 for x in range(70,480,20):
  amp=11+16*(0.5+0.5*math.sin(x*.017-t*2.5))
  d.line((x,544-amp,x,544+amp),fill=(72,117,143),width=2)
 d.text((W/2,609),'PERCEIVED PATTERN ≠ PROVEN EFFECT',anchor='mm',font=SMALL,fill=COLORS['muted'])
 for k,line in enumerate(body):
  d.text((W/2,682+k*48),line,anchor='mm',font=BODY,fill=COLORS['white'])
 d.text((W/2,826),foot,anchor='mm',font=SMALL,fill=COLORS['teal'])
 d.rounded_rectangle((35,882,505,895),radius=6,fill=(46,63,81))
 d.rounded_rectangle((35,882,35+int(470*(i+1)/(FPS*DURATION)),895),radius=6,fill=COLORS['gold'])
 d.text((W/2,929),'Original illustration  •  no sound  •  source in transcript',anchor='mm',font=font(REG,15),fill=COLORS['muted'])
 return im

if __name__=='__main__':
 poster=frame(0);poster.save(os.path.join(OUT,'poster.png'))
 shots=[]
 for a,b,*_ in SCENES: shots.append(frame(int((a+b)*FPS/2)))
 sheet=Image.new('RGB',(W*3,H*2))
 for z,im in enumerate(shots):sheet.paste(im,((z%3)*W,(z//3)*H))
 sheet.resize((810,960)).save(os.path.join(OUT,'contact-sheet.jpg'),quality=86)
 target=os.path.join(OUT,'the-phantom-beat-40s.mp4')
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','30','-pix_fmt','yuv420p','-movflags','+faststart',target]
 with subprocess.Popen(cmd,stdin=subprocess.PIPE) as proc:
  for i in range(FPS*DURATION):proc.stdin.write(frame(i).tobytes())
  proc.stdin.close();ret=proc.wait()
  if ret:raise RuntimeError(f'ffmpeg exited {ret}')
 print(target)
