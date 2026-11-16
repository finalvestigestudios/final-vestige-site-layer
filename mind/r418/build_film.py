#!/usr/bin/env python3
"""Original silent 42s Mind R418 media prototype. Standard Pillow + ffmpeg, no remote assets.
No narration, no merchant links, no prices, no claims of product efficacy.
Production use requires separate founder/QA release approval.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess, json, hashlib
P=Path(__file__).resolve().parent
W,H=960,540
BG=(17,23,27); CARD=(31,41,46); GOLD=(223,184,117); CREAM=(243,237,227); MUTED=(196,205,206)
FONT='/usr/share/fonts/truetype/lato/Lato-Bold.ttf'
NORMAL='/usr/share/fonts/truetype/lato/Lato-Regular.ttf'
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
scenes=[
 ('THE STUDY','A volunteer listened for 10 minutes.','Researchers measured a narrow attention task.','Original experiment ≠ commercial audio'),
 ('THE TASK','Conflicting arrows demanded a response.','Speed and accuracy were measured.','Not an entire workday'),
 ('THE RESULT','Some novices performed better in the lab.','Individual differences mattered.','No Zen12 product was tested'),
 ('THE SALES PAGE','A 12-minute commercial audio makes a bigger promise.','Where is the direct product-specific comparison?','Seller claims ≠ independent proof'),
 ('THE FREE BASELINE','Choose one small task. Set a 12-minute timer.','Record what you actually finished.','Your observations are not a clinical test'),
 ('KEEP THE SOURCE','Read the experiment. Notice its limits.','Keep questions separate from purchase decisions.','Final Vestige / Mind & Perception')]

def font(file,size): return ImageFont.truetype(file,size)
def center(d,y,text,f,fill):
    box=d.textbbox((0,0),text,font=f);d.text(((W-(box[2]-box[0]))/2,y),text,font=f,fill=fill)
for i,(label,headline,sub,footer) in enumerate(scenes):
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
    d.rounded_rectangle((45,42,W-45,H-45),radius=28,fill=CARD,outline=(120,100,72),width=2)
    d.rectangle((82,86,878,91),fill=GOLD)
    center(d,123,f'{i+1:02d} / 06  ·  {label}',font(NORMAL,23),GOLD)
    center(d,209,headline,font(SERIF,31),CREAM)
    center(d,270,sub,font(NORMAL,25),MUTED)
    if i==1:
        for j in range(5):
            x=310+j*82
            pts=[(x,358),(x+50,358),(x+32,343),(x+50,358),(x+32,373)]
            d.line(pts[:2],fill=CREAM,width=7);d.line(pts[2:4],fill=CREAM,width=7);d.line((pts[3],pts[4]),fill=CREAM,width=7)
    elif i==3:
        d.ellipse((440,337,520,417),fill=GOLD)
        center(d,342,'?',font(SERIF,48),BG)
    else:
        d.ellipse((458,350,502,394),outline=GOLD,width=4)
    center(d,443,footer,font(NORMAL,20),CREAM)
    im.save(P/f'scene_{i+1:02d}.png',optimize=True)
concat=P/'scenes.ffconcat'
with concat.open('w') as out:
    out.write('ffconcat version 1.0\n')
    for i in range(1,7):
        out.write(f"file '{(P/f'scene_{i:02d}.png').as_posix()}'\nduration 7.0\n")
    out.write(f"file '{(P/'scene_06.png').as_posix()}'\n")
mp4=P/'r418-original-silent-42s.mp4'
cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-safe','0','-f','concat','-i',str(concat),'-vf','fps=12,format=yuv420p','-t','42','-an','-c:v','libx264','-preset','veryfast','-crf','30','-movflags','+faststart',str(mp4)]
subprocess.run(cmd,check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height,r_frame_rate','-of','json',str(mp4)]))
manifest={'status':'ENCODED LOCAL SILENT PROTOTYPE, NOT COMMITTED MEDIA OR APPROVED RELEASE','source':'build_film.py','file':mp4.name,'sha256':hashlib.sha256(mp4.read_bytes()).hexdigest(),'ffprobe':probe,'scenes':6,'audio':False,'merchant_links':False,'rights':'Original typographic slides, no outside assets; production review pending'}
(P/'prototype_manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
