#!/usr/bin/env python3
"""Original 40-second silent infographic film, not a psychology test or product demonstration."""
from pathlib import Path
import subprocess, zipfile, json, hashlib, math
from PIL import Image, ImageDraw, ImageFont

OUT=Path('/mnt/data/fv_mind_r79');OUT.mkdir(parents=True,exist_ok=True)
W,H,FPS=540,960,12
BG=(10,13,14); GOLD=(191,158,99); WHITE=(247,240,222); MUTED=(182,183,173); DIM=(58,66,66)
SCENES=[
 ('WHAT YOU NOTICE', 'A FIELD EXPERIMENT IN ATTENTION', 7),
 ('COUNT THE SIGNALS', 'YOUR TASK CHANGES THE PICTURE', 7),
 ('AN UNEXPECTED VISITOR', 'A LARGE SHAPE CAN STILL BE MISSED', 7),
 ('1999 · ORIGINAL STUDY', '46% MISSED THE UNEXPECTED EVENT', 7),
 ('2023 · AN IMPORTANT LIMIT', 'FAST MOTION CAN ATTRACT ATTENTION', 6),
 ('WHAT IS YOUR QUESTION?', 'LOOK FOR THE EVIDENCE, NOT A PROMISE', 6),
]
assert sum(s[2] for s in SCENES)==40
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font_b='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
F=lambda p,s:ImageFont.truetype(p,s)

def center(draw,txt,y,font,fill):
 x0,y0,x1,y1=draw.textbbox((0,0),txt,font=font)
 draw.text(((W-(x1-x0))//2,y),txt,font=font,fill=fill)

def gorilla(draw,x,y,alpha=1):
 c=(48,59,58) if alpha>0.5 else (31,39,39)
 draw.ellipse((x-36,y-42,x+36,y+30),fill=c)
 draw.ellipse((x-26,y-84,x+26,y-32),fill=c)
 draw.rounded_rectangle((x-55,y-17,x-29,y+82),radius=10,fill=c)
 draw.rounded_rectangle((x+29,y-17,x+55,y+82),radius=10,fill=c)
 draw.line((x-19,y+26,x-22,y+109),fill=c,width=23)
 draw.line((x+19,y+26,x+22,y+109),fill=c,width=23)


def frame(scene,t):
 im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
 d.rectangle((24,25,W-24,H-25),outline=DIM,width=2)
 d.line((46,92,494,92),fill=GOLD,width=2)
 d.text((47,46),'FINAL VESTIGE / MIND',font=F(font_b,16),fill=GOLD)
 d.text((390,46),'FIELD FILM 079',font=F(font,12),fill=MUTED)
 title,sub,_=SCENES[scene]
 center(d,title,142,F(font_b,26),WHITE)
 center(d,sub,196,F(font,16),MUTED)
 d.rounded_rectangle((72,278,468,687),radius=13,outline=(82,79,65),width=2)
 d.line((90,482,452,482),fill=(28,39,41),width=2)
 if scene in (0,1,2,3):
  for j in range(4):
   phase=t*1.6+j*.22
   x=106+int((phase*96 + j*74)%325)
   y=350+(j%2)*170+int(19*math.sin(t*2+j))
   d.ellipse((x-16,y-16,x+16,y+16),fill=GOLD if j%2==0 else (90,103,105))
  if scene==2:gorilla(d,320+int(t*7),475)
  if scene==3:gorilla(d,322,465)
 elif scene==4:
  for j in range(9):
   x=132+(j%3)*135;y=369+(j//3)*91
   d.ellipse((x-21,y-21,x+21,y+21),outline=(89,115,112),width=4)
  d.line((120,350,425,620),fill=GOLD,width=8)
 elif scene==5:
  d.arc((134,352,410,626),0,330,fill=GOLD,width=16)
  d.line((276,360,276,445),fill=GOLD,width=14)
  d.ellipse((268,468,285,485),fill=GOLD)
 center(d,'ILLUSTRATION · NOT AN EXPERIMENT',730,F(font_b,15),GOLD)
 center(d,'No individual outcome is implied.',770,F(font,16),MUTED)
 d.line((47,854,493,854),fill=DIM,width=2)
 center(d,'Primary research: Simons & Chabris (1999); Wallisch et al. (2023)',876,F(font,12),MUTED)
 return im

frames=OUT/'frames';frames.mkdir(exist_ok=True)
idx=0;vtt=['WEBVTT','']
now=0
for j,(title,sub,seconds) in enumerate(SCENES):
 for k in range(seconds*FPS):
  im=frame(j,k/FPS)
  im.save(frames/f'{idx:04}.png',compress_level=1)
  idx+=1
 a=now;b=now+seconds
 vtt.extend([f'00:00:{a:02}.000 --> 00:00:{b:02}.000',f'{title} {sub}.',''])
 now=b
(OUT/'film-captions.vtt').write_text('\n'.join(vtt),encoding='utf8')
frame(0,0).save(OUT/'poster.png')
cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate',str(FPS),'-i',str(frames/'%04d.png'),'-c:v','libx264','-pix_fmt','yuv420p','-preset','veryfast','-crf','31','-movflags','+faststart',str(OUT/'the-visible-gorilla-40s.mp4')]
subprocess.run(cmd,check=True)
subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1',str(OUT/'the-visible-gorilla-40s.mp4')],check=True)
html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Offline FV Film Review</title><body style="background:#0a0d0e;color:#f7f0de;font:17px/1.5 system-ui;max-width:600px;margin:auto;padding:16px"><h1>What You Notice</h1><p>Independent educational illustration. No merchant endorsement.</p><video controls preload="none" playsinline width="540" height="960" style="max-width:100%;height:auto" poster="poster.png"><source src="the-visible-gorilla-40s.mp4" type="video/mp4"><track kind="captions" label="English" srclang="en" src="film-captions.vtt" default></video><details><summary>Complete transcript</summary><ol>'''+''.join('<li><strong>'+a+'</strong> — '+b+'</li>' for a,b,_ in SCENES)+'''</ol></details><p>References: <a href="https://doi.org/10.1068/p281059">Simons &amp; Chabris (1999)</a>; <a href="https://doi.org/10.1073/pnas.2214930120">Wallisch et al. (2023)</a>.</p></body></html>'''
(OUT/'offline-player.html').write_text(html,encoding='utf8')
(OUT/'README.txt').write_text('Review-only media. Original illustration (not an empirical test, experiment footage, or Zen12 performance demonstration). Offline video is not hosted on finalvestige.com. All media released only by explicit founder authorization.\n',encoding='utf8')
with zipfile.ZipFile(OUT/'offline-review.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
 for name in ['the-visible-gorilla-40s.mp4','poster.png','film-captions.vtt','offline-player.html','README.txt']:
  z.write(OUT/name,name)
 with z.open('script-source-reference.txt','w') as f:f.write(b'Original generator supplied to reviewer as /mnt/data/build_r79_media.py, see script.\n')
with zipfile.ZipFile(OUT/'offline-review.zip') as z: assert z.testzip() is None
print(json.dumps({p.name: {'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [OUT/'the-visible-gorilla-40s.mp4',OUT/'poster.png',OUT/'offline-review.zip']},indent=2))
