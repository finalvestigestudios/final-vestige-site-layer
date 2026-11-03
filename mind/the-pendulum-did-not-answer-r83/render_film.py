"""Original 40-second educational pendulum short. Requires Pillow and ffmpeg.
No third-party images or audio, no scientific data simulation. Film is an illustration.
"""
from PIL import Image, ImageDraw, ImageFont
import math, os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, SECONDS = 540, 960, 12, 40
GOLD=(227,194,127); CREAM=(240,238,225); MUTED=(168,189,188)
FONT='/usr/share/fonts/truetype/lato/Lato-Medium.ttf'
BOLD='/usr/share/fonts/truetype/lato/Lato-Heavy.ttf'
if not os.path.exists(BOLD): BOLD=FONT

def ft(px,bold=False): return ImageFont.truetype(BOLD if bold else FONT,px)
F44=ft(44,True); F33=ft(33,True); F26=ft(26,True); F23=ft(23); F19=ft(19); F16=ft(16)
scene_titles=[
 'THE WEIGHT','THE EXPECTATION','THE MOVEMENT','THE OLD QUESTION',
 'THE TEST','THE DISTINCTION'
]
lines=[
 ['A pendulum can move','without a deliberate push.'],
 ['Picture a circle.','Does a thought move a muscle?'],
 ['Motion can be real','and still feel unchosen.'],
 ['In 1852, Carpenter studied','suggestion and muscular action.'],
 ['Measure what changes.','Do not assume the cause.'],
 ['MOVEMENT IS AN OBSERVATION.','CAUSE REQUIRES EVIDENCE.']
]
cuts=[0,6,13,19,26,33,40]

# Single source matte: a dark scholarly field with warm haze, no external texture.
base=Image.new('RGB',(W,H)); bp=base.load()
for y in range(H):
 for x in range(W):
  dx=(x-W*.5)/W; dy=(y-300)/H
  glow=max(0.,1.-math.sqrt(dx*dx*1.7+dy*dy*1.4)*1.65)
  noise=1.5*math.sin((x*3+y*2)/97)
  bp[x,y]=(int(9+16*glow+noise),int(22+26*glow+noise),int(30+30*glow+noise))

def center(draw,y,string,font,color=CREAM):
 box=draw.textbbox((0,0),string,font=font); draw.text(((W-(box[2]-box[0]))/2,y),string,fill=color,font=font)

def frame(t):
 idx=next(i for i in range(6) if cuts[i]<=t<cuts[i+1]); local=(t-cuts[idx])/(cuts[idx+1]-cuts[idx]);
 im=base.copy();d=ImageDraw.Draw(im)
 # Architecture and a continuous optical baseline.
 d.line((48,84,492,84),fill=(80,108,111),width=2)
 center(d,104,'FINAL VESTIGE  /  MIND',F19,GOLD)
 center(d,171,scene_titles[idx],F33)
 d.line((70,230,470,230),fill=(61,85,91),width=1)
 if idx in (0,1,2,3):
  pivot=(270,294); length=295
  # Visual pendulum motion is conceptual, deliberately not experimental data.
  theta=(0.008*math.sin(t*4) if idx==0 else (0.055*math.sin(t*2.3) if idx==1 else (0.11+0.20*local)*math.sin(t*2.4) if idx==2 else 0.15*math.sin(t*1.3)))
  bob=(pivot[0]+math.sin(theta)*length,pivot[1]+math.cos(theta)*length)
  d.ellipse((pivot[0]-7,pivot[1]-7,pivot[0]+7,pivot[1]+7),fill=GOLD)
  if idx==1:
   # idea path is not an actual measured arc
   for deg in range(0,360,22):
    aa=math.radians(deg);x=270+120*math.cos(aa);y=585+34*math.sin(aa)
    d.ellipse((x-2,y-2,x+2,y+2),fill=(96,119,120))
   center(d,664,'IMAGINED DIRECTION',F16,MUTED)
  if idx==2:
   for a in [-.31,-.22,-.13,0,.13,.22,.31]:
    x=pivot[0]+math.sin(a)*length;y=pivot[1]+math.cos(a)*length
    d.ellipse((x-2,y-2,x+2,y+2),fill=(94,120,122))
  d.line((*pivot,*bob),fill=GOLD,width=3)
  d.ellipse((bob[0]-21,bob[1]-21,bob[0]+21,bob[1]+21),fill=GOLD,outline=(255,226,166),width=2)
  if idx==3:
   center(d,634,'CARPENTER  /  1852',F26,GOLD)
   center(d,669,'HISTORICAL RECORD, NOT FOOTAGE',F16,MUTED)
 elif idx==4:
  # Schematic trajectory, expressly not recorded experimental values.
  d.rounded_rectangle((76,307,464,627),radius=15,outline=(82,111,114),width=2)
  d.line((116,575,432,575),fill=MUTED,width=1)
  d.line((116,356,116,575),fill=MUTED,width=1)
  points=[]
  for j in range(150):
   xx=116+j*316/149; yy=467-math.sin(j/149*math.pi*3.2)*(16+27*j/149)
   points.append((xx,yy))
  d.line(points,fill=GOLD,width=4)
  center(d,642,'SCHEMATIC ONLY — NO STUDY DATA',F16,MUTED)
 else:
  d.rounded_rectangle((57,335,483,575),radius=16,outline=(185,158,101),width=2)
  center(d,371,'THE PENDULUM MOVED',F26,GOLD)
  d.line((102,432,438,432),fill=(104,132,132),width=1)
  center(d,464,'WHY IT MOVED',F26,CREAM)
  center(d,511,'IS A DIFFERENT QUESTION',F19,MUTED)
 # Shared educational statement, never marketed as a product effect.
 d.line((55,718,485,718),fill=(83,104,111),width=2)
 for n,ln in enumerate(lines[idx]):
  center(d,745+n*39,ln,F23 if idx!=5 else F19,CREAM if n==0 else GOLD)
 center(d,875,'EDUCATIONAL ILLUSTRATION · NOT AN EXPERIMENT',F16,MUTED)
 d.line((48,919,492,919),fill=(80,108,111),width=2)
 return im

if __name__=='__main__':
 poster=frame(2.6); poster.save(os.path.join(HERE,'poster.png'))
 args=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-vcodec','rawvideo','-s',f'{W}x{H}','-pix_fmt','rgb24','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','24','-pix_fmt','yuv420p','-movflags','+faststart',os.path.join(HERE,'the-hand-below-the-pendulum-40s.mp4')]
 proc=subprocess.Popen(args,stdin=subprocess.PIPE)
 try:
  for n in range(FPS*SECONDS):
   proc.stdin.write(frame(n/FPS).tobytes())
 except BrokenPipeError as exc:
  raise RuntimeError('ffmpeg pipe failed') from exc
 finally:
  proc.stdin.close()
 if proc.wait()!=0: raise RuntimeError('ffmpeg render returned failure')
 print('Rendered:',FPS*SECONDS,'frames')
