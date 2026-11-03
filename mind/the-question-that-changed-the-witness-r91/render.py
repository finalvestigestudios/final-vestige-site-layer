#!/usr/bin/env python3
"""R91: original silent 40-second educational animation (not experiment footage).
Requires Pillow and ffmpeg. No proprietary photos, video or font files are distributed.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess, math, os, argparse

W,H,FPS=540,960,12
CUTS=[0,7,14,21,28,34,40]
SCENES=[
 ("THE WITNESS", "The accident is over.\nNow comes the question.", "01 / THE RECORD"),
 ("HIT OR SMASHED?", "Same film.\nDifferent verb.", "02 / THE PROMPT"),
 ("SPEED ESTIMATE", "The wording influenced\nwhat people reported.", "03 / THE RESULT"),
 ("BROKEN GLASS?", "Some later reported glass\nthat wasn't in the film.", "04 / THE DETAIL"),
 ("NOT THE WHOLE STORY", "Later studies confirm an effect.\nThe mechanism is still debated.", "05 / THE LIMIT"),
 ("RECORD IT FIRST", "What did you see, before\nsomeone told you what to see?", "06 / THE QUESTION")]
INK=(15,19,24); PANEL=(26,35,40); GOLD=(223,191,138); WHITE=(251,241,221); MUTED=(176,185,183); RUST=(139,56,47)

def font(sz,bold=False):
 candidates=(["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"] if bold else ["/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"])
 for p in candidates:
  try:return ImageFont.truetype(p,sz)
  except OSError:pass
 return ImageFont.load_default()

def center(draw,xy,text,ft,color,spacing=1.0):
 x,y=xy
 lines=text.split('\n')
 for i,line in enumerate(lines):
  box=draw.textbbox((0,0),line,font=ft)
  draw.text((x-(box[2]-box[0])/2,y+i*ft.size*spacing),line,font=ft,fill=color)

def make_frame(frame):
 t=frame/FPS
 scene=min(5,max(0,next((i for i in range(6) if CUTS[i]<=t<CUTS[i+1]),5)))
 headline,sub,tag=SCENES[scene]
 im=Image.new('RGB',(W,H),INK);d=ImageDraw.Draw(im)
 # Original editorial cover system: rules, road horizon and slowly oscillating marker.
 d.rectangle((0,0,W,22),fill=GOLD)
 d.text((45,52),'FINAL VESTIGE STUDIOS  /  MIND',font=font(18,True),fill=GOLD)
 d.line((45,110,495,110),fill=(105,95,83),width=2)
 center(d,(W/2,164),headline,font(40,True),WHITE)
 d.rectangle((46,269,494,663),fill=PANEL)
 # Road and traffic-sign graphic, entirely original vector shapes.
 d.polygon([(178,660),(242,390),(296,390),(359,660)],fill=(56,65,70))
 for y in range(450,645,51):d.line((270,y,270,y+23),fill=GOLD,width=4)
 sign_x=270+int(12*math.sin(t*.7+scene*.35));sign_y=421+int(7*math.cos(t*.9))
 d.line((sign_x,sign_y+70,sign_x,625),fill=(167,175,172),width=7)
 if scene in (2,3,4):
  d.rounded_rectangle((sign_x-71,sign_y-67,sign_x+71,sign_y+70),radius=12,fill=RUST,outline=WHITE,width=7)
  center(d,(sign_x,sign_y-15),'STOP',font(31,True),WHITE)
 else:
  d.ellipse((sign_x-62,sign_y-62,sign_x+62,sign_y+62),fill=RUST,outline=WHITE,width=7)
  center(d,(sign_x,sign_y-14),'?',font(42,True),WHITE)
 # A visible pair of prompts, not a reenactment of actual original slides.
 if scene in (1,2):
  d.rounded_rectangle((68,575,249,630),radius=8,fill=(51,70,73))
  d.rounded_rectangle((291,575,472,630),radius=8,fill=(91,48,44))
  center(d,(159,589),'HIT',font(22,True),WHITE)
  center(d,(381,589),'SMASHED',font(17,True),WHITE)
 center(d,(W/2,699),sub,font(23),WHITE,1.45)
 d.text((46,825),tag,font=font(17,True),fill=GOLD)
 d.text((46,868),'Illustration  /  not experimental footage',font=font(15),fill=MUTED)
 d.rectangle((45,916,495,923),fill=(76,77,76))
 d.rectangle((45,916,45+int(450*(frame+1)/(FPS*40)),923),fill=GOLD)
 return im

def render(outdir):
 outdir.mkdir(parents=True,exist_ok=True)
 poster=make_frame(0)
 poster.save(outdir/'poster.png',optimize=True)
 movie=outdir/'the-question-arrived-after-the-event-40s.mp4'
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-vcodec','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','26','-pix_fmt','yuv420p','-movflags','+faststart',str(movie)]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 try:
  for frame in range(FPS*40):p.stdin.write(make_frame(frame).tobytes())
  p.stdin.close();err=p.stderr.read().decode();ret=p.wait()
  if ret:raise RuntimeError(err)
 except Exception:
  p.kill();raise
 print(movie)
 print(outdir/'poster.png')

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=Path('r91-film'));render(parser.parse_args().out)
