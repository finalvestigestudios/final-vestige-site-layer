#!/usr/bin/env python3
"""Original 42-second silent Mind/Zen12 independent-decision explainer.
Reproducible; Python3 + Pillow and local ffmpeg; no fonts are redistributed.
Writes MP4 and PNG poster into the chosen output directory. Not for deployment.
"""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import math,os,shutil,subprocess,tempfile
W,H,FPS=960,540,12
DURATION=42
SCENES=[
('A TIMER IS NOT A RESULT','Twelve minutes is a duration, not a guarantee.'),
('FIRST, PICK ONE TASK','An ordinary, non-clinical comparison.'),
('ZEN12 SELLS AN AUDIO LIBRARY','Twelve-minute sessions are a feature.'),
('ONE HOUR IN TWELVE MINUTES?','That is the seller’s claim, not established proof.'),
('AN EEG SIGNAL IS NOT A PURCHASE RESULT','Measured brain activity differs from useful performance.'),
('START WITH A FREE TIMER','Try a simple routine before choosing paid audio.'),
('YOUR CHOICE. YOUR EVIDENCE.','Check the exact terms. There is no pressure to buy.')]

def font(size,bold=False):
  folders=['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf']
  for p in folders:
    if os.path.isfile(p): return ImageFont.truetype(p,size)
  return ImageFont.load_default()
TITLE=font(40,True); SUB=font(24); SMALL=font(18,True); MICRO=font(16)
COLORS={'bg':(10,13,15),'white':(241,237,228),'gold':(218,191,135),'muted':(184,176,163),'panel':(23,26,28)}

def frame(sec):
  scene=min(6,int(sec//6)); phase=(sec%6)/6
  im=Image.new('RGB',(W,H),COLORS['bg']);d=ImageDraw.Draw(im)
  d.rectangle((44,38,916,502),outline=(76,68,55),width=2)
  d.text((75,67),'FINAL VESTIGE STUDIOS  /  MIND & PERCEPTION',font=SMALL,fill=COLORS['gold'])
  d.text((75,108),'INDEPENDENT BUYER RESEARCH  •  UNPUBLISHED',font=MICRO,fill=COLORS['muted'])
  cx=490;cy=278
  for n,rad in enumerate([134,166,196]):
    d.arc((cx-rad,cy-rad,cx+rad,cy+rad),int((sec*11+n*70)%360),int((sec*11+n*70)%360)+205,fill=(69+n*11,66+n*8,56+n*5),width=2)
  # Visible but low-motion background ornament, not flashing
  a=sec*.24
  d.ellipse((cx+int(146*math.cos(a))-5,cy+int(146*math.sin(a))-5,cx+int(146*math.cos(a))+5,cy+int(146*math.sin(a))+5),fill=COLORS['gold'])
  def centered(s,fo,y,color):
    box=d.textbbox((0,0),s,font=fo)
    d.text(((W-(box[2]-box[0]))/2,y),s,font=fo,fill=color)
  title,sub=SCENES[scene]
  size=34 if len(title)>29 else 40
  fo=font(size,True)
  centered(title,fo,222,COLORS['white'])
  centered(sub,SUB,296,COLORS['muted'])
  d.text((75,448),'42 SEC  •  ORIGINAL SILENT EXPLAINER',font=SMALL,fill=COLORS['gold'])
  d.text((698,448),f'00:{int(sec):02d} / 00:42',font=SMALL,fill=COLORS['gold'])
  d.rounded_rectangle((75,480,885,486),radius=3,fill=(54,51,43))
  d.rounded_rectangle((75,480,75+int(810*(sec/42)),486),radius=3,fill=COLORS['gold'])
  return im

def main():
  target=Path(os.environ.get('FV_FILM_OUT','/mnt/data')); target.mkdir(exist_ok=True,parents=True)
  poster=target/'fv_mind_r285_poster.png';frame(0).save(poster)
  with tempfile.TemporaryDirectory(prefix='fv-film-r285-') as work:
    for i in range(DURATION*FPS):frame(i/FPS).save(Path(work)/f'f_{i:04d}.png',compress_level=1)
    out=target/'fv_mind_r285_42s_silent.mp4'
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate',str(FPS),'-i',str(Path(work)/'f_%04d.png'),'-c:v','libx264','-preset','medium','-crf','26','-pix_fmt','yuv420p','-movflags','+faststart','-an',str(out)]
    subprocess.run(cmd,check=True)
    print(out, 'bytes',out.stat().st_size)
    subprocess.run(['ffprobe','-v','error','-show_entries','format=duration,size','-of','default=noprint_wrappers=1',str(out)],check=True)
if __name__=='__main__':main()
