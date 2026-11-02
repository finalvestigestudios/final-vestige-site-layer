#!/usr/bin/env python3
"""Generate the silent, original 40s FV door-study educational film.
All figures are schematic. No researcher/participant photographs or footage.
Requires Pillow and ffmpeg. No network, external content or third-party assets.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess, zipfile, shutil, hashlib, json, textwrap
ROOT=Path(__file__).resolve().parent
W,H,FPS=540,960,12
BG=(9,12,12); FG=(243,236,220); GOLD=(205,165,104); MUTED=(187,181,168)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
DURATIONS=[6,6,7,7,7,7]
SCENES=[
('A QUESTION','A map. A stranger.\nAn ordinary request.', 'map'),
('AN INTERRUPTION','Two workers carry a door\nbetween the speakers.', 'door'),
('A DIFFERENT PERSON','The first questioner leaves.\nAnother takes his place.', 'swap'),
('THE SAME STORY','The directions continue.\nThe identity has changed.', 'map2'),
('SEVEN OF FIFTEEN','In the initial field condition,\n7 of 15 reported noticing.', 'dots'),
('THE EVIDENCE','What was reported?\nWhat actually changed?', 'question')]
font=lambda size,serif=False: ImageFont.truetype(SERIF if serif else FONT,size)
def multiline(draw,xy,s,f,fill,spacing=14,anchor='mm'):
    draw.multiline_text(xy,s,font=f,fill=fill,spacing=spacing,align='center',anchor=anchor)
def person(d,x,y,color,head=36,offset=0):
    d.ellipse((x-head,y-head,x+head,y+head),outline=color,width=7)
    d.arc((x-72,y+34,x+72,y+223),185,355,fill=color,width=9)
    d.line((x,y+165,x,y+225),fill=color,width=5)
def create_scene(idx,title,desc,art):
    im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
    for y in range(0,H,10):
        if y%30==0: d.line((44,y,496,y),fill=(19,22,21),width=1)
    d.rectangle((32,36,508,924),outline=(71,65,54),width=2)
    d.text((55,61),'FINAL VESTIGE  /  MIND ARCHIVE',font=font(17),fill=GOLD)
    d.line((55,100,485,100),fill=GOLD,width=2)
    multiline(d,(270,155),title,font(30),FG)
    cy=395
    if art=='map':
        person(d,175,350,GOLD);person(d,375,350,MUTED)
        d.polygon([(220,425),(270,410),(320,425),(320,516),(270,502),(220,517)],outline=FG)
        d.line((270,413,270,500),fill=FG,width=3)
    elif art=='door':
        person(d,145,365,GOLD);person(d,395,365,MUTED)
        d.rectangle((224,275,318,566),fill=(70,51,35),outline=GOLD,width=5)
        d.ellipse((295,420,300,425),fill=FG)
    elif art=='swap':
        person(d,160,355,GOLD);person(d,370,355,(142,181,165))
        d.line((233,440,295,440),fill=GOLD,width=6)
        d.polygon([(296,425),(323,440),(296,455)],fill=GOLD)
    elif art=='map2':
        person(d,170,350,(142,181,165));person(d,370,350,MUTED)
        d.polygon([(220,425),(270,410),(320,425),(320,516),(270,502),(220,517)],outline=FG)
        d.line((270,413,270,500),fill=FG,width=3)
    elif art=='dots':
        for i in range(15):
            x=88+(i%5)*90;y=305+(i//5)*90
            d.ellipse((x,y,x+47,y+47),fill=GOLD if i<7 else (53,58,53),outline=FG,width=2)
        multiline(d,(270,620),'7  /  15',font(48,True),GOLD)
    else:
        d.arc((145,278,395,520),205,325,fill=GOLD,width=12)
        multiline(d,(270,419),'?',font(130,True),FG)
        d.line((145,560,395,560),fill=GOLD,width=3)
    multiline(d,(270,703),desc,font(25),FG,spacing=13)
    multiline(d,(270,831),'Original schematic illustration\nNot experimental footage',font(15),MUTED,spacing=8)
    d.text((55,883),f'{idx+1:02} / 06',font=font(18),fill=GOLD)
    path=ROOT/f'scene-{idx+1:02}.png';im.save(path)
    return path
paths=[create_scene(i,*row) for i,row in enumerate(SCENES)]
shutil.copy2(paths[0],ROOT/'poster.png')
# Fixed-duration, frame-accurate source: concat of static stills, no third-party video.
lines=['ffconcat version 1.0']
for name,dur in zip(paths,DURATIONS):
    lines += [f"file '{name.as_posix()}'",f'duration {dur}']
lines += [f"file '{paths[-1].as_posix()}'"]
(ROOT/'scenes.ffconcat').write_text('\n'.join(lines)+'\n')
cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-safe','0','-f','concat','-i',str(ROOT/'scenes.ffconcat'),'-vf',f'fps={FPS},format=yuv420p','-frames:v',str(FPS*sum(DURATIONS)),'-c:v','libx264','-preset','veryfast','-crf','24','-movflags','+faststart',str(ROOT/'the-person-behind-the-door-40s.mp4')]
subprocess.run(cmd,check=True)
# Captions echo the scene labels; screen text does not replace real subtitle support.
def stamp(s):return f'{s//3600:02d}:{(s%3600)//60:02d}:{s%60:02d}.000'
caption=['WEBVTT','']
now=0
for i,(title,desc,_) in enumerate(SCENES):
    end=now+DURATIONS[i]
    caption.extend([str(i+1),f'{stamp(now)} --> {stamp(end)}',f'{title}. {desc.replace(chr(10)," ")}', ''])
    now=end
(ROOT/'film-captions.vtt').write_text('\n'.join(caption)+'\n')
html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>The Person Behind the Door — Offline Reviewer</title><style>html{background:#0a0d0c;color:#f4efe6;font:18px/1.6 system-ui}main{max-width:780px;margin:auto;padding:20px}video{display:block;width:100%;max-height:80vh;border:1px solid #b8955e;background:#000}a{color:#d8b577}a:focus-visible,video:focus-visible{outline:3px solid white;outline-offset:4px}li{margin:12px 0}</style><main><h1>The Person Behind the Door</h1><p>Original 40-second educational animation; silent; not experimental footage, not a Zen12 demonstration.</p><video controls preload="none" playsinline poster="poster.png"><source src="the-person-behind-the-door-40s.mp4" type="video/mp4"><track src="film-captions.vtt" kind="captions" srclang="en" label="English captions" default>Your browser cannot play the video; use the full transcript below.</video><h2>Complete transcript</h2><ol>'''+''.join(f'<li>{t}. {s.replace(chr(10)," ")}</li>' for t,s,_ in SCENES)+'''</ol><p>Illustrative scenes only. Main manuscript citation: Simons &amp; Levin (1998), DOI 10.3758/BF03208840. No merchant link or visitor tracking.</p></main></html>'''
(ROOT/'offline-review.html').write_text(html)
# Contact sheet for human visual inspection.
contact=Image.new('RGB',(W*3,H*2),(0,0,0))
for i,p in enumerate(paths):contact.paste(Image.open(p),((i%3)*W,(i//3)*H))
contact.save(ROOT/'contact-sheet.png')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height,avg_frame_rate,nb_frames','-of','json',str(ROOT/'the-person-behind-the-door-40s.mp4')]))
assert abs(float(probe['format']['duration'])-40.0)<0.001,probe
assert probe['streams'][0]['codec_name']=='h264'
assert probe['streams'][0]['width']==540 and probe['streams'][0]['height']==960
assert int(probe['streams'][0]['nb_frames'])==480
assert len(paths)==6 and sum(DURATIONS)==40
files=['the-person-behind-the-door-40s.mp4','poster.png','contact-sheet.png','film-captions.vtt','render_door_film.py','scenes.ffconcat','offline-review.html']
with zipfile.ZipFile(ROOT/'offline-review.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
    for f in files:z.write(ROOT/f,arcname=f)
with zipfile.ZipFile(ROOT/'offline-review.zip') as z: assert z.testzip() is None
print(json.dumps({'duration':probe['format']['duration'],'frames':probe['streams'][0]['nb_frames'],'codec':probe['streams'][0]['codec_name'],'video_bytes':int(probe['format']['size']),'zip_bytes':(ROOT/'offline-review.zip').stat().st_size,'sha256_mp4':hashlib.sha256((ROOT/files[0]).read_bytes()).hexdigest(),'sha256_script_git_blob':subprocess.check_output(['git','hash-object',str(ROOT/'render_door_film.py')],text=True).strip()},indent=2))
