#!/usr/bin/env python3
"""Offline, reproducible six-scene educational silent film. No network calls or stock art."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import subprocess, zipfile, hashlib, json

OUT = Path(__file__).resolve().parent
W, H = 540, 960
BG = (11, 13, 13)
INK = (244, 239, 230)
GOLD = (201, 166, 109)
MUTED = (184, 173, 155)
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
SERIF = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
regular = ImageFont.truetype(FONT, 27)
small = ImageFont.truetype(FONT, 20)
large = ImageFont.truetype(SERIF, 42)
brand = ImageFont.truetype(FONT, 17)

scenes = [
    ('THE FORBIDDEN IDEA', 'Try not to think of a white bear.', 'An instruction changes the task.', 7),
    ('THE BELL', 'In 1987, volunteers reported their thoughts.', 'They rang a bell when the bear appeared.', 7),
    ('WHAT WE CAN COUNT', 'A bell records a report.', 'It does not reveal every thought.', 7),
    ('AFTER THE EFFORT', 'Later studies often found rebound.', 'Immediate increases were more conditional.', 7),
    ('A DIFFERENT AIM', 'Returning attention is not the same', 'as forcing the mind to go blank.', 6),
    ('EVIDENCE BEFORE PROMISE', 'A preference is not a brainwave test.', 'A seller claim is not a proven result.', 6),
]

def center(draw, y, txt, font, fill, width=W):
    if draw.textlength(txt,font=font)>width-120:
        font=ImageFont.truetype(FONT,max(16,round(font.size*(width-120)/draw.textlength(txt,font=font))))
    box=draw.textbbox((0,0),txt,font=font)
    draw.text(((width-(box[2]-box[0]))//2,y),txt,font=font,fill=fill)

def draw_bear(d, cx, cy, scale=1):
    def box(x1,y1,x2,y2):return [round(cx+x1*scale),round(cy+y1*scale),round(cx+x2*scale),round(cy+y2*scale)]
    d.ellipse(box(-143,-46,84,72),fill=INK)
    d.ellipse(box(42,-87,140,20),fill=INK)
    d.ellipse(box(52,-104,80,-70),fill=INK)
    d.ellipse(box(105,-102,132,-69),fill=INK)
    for x in (-113,-32,55):d.rounded_rectangle(box(x,46,x+30,137),radius=10,fill=INK)
    d.polygon([(round(cx+122*scale),round(cy-38*scale)),(round(cx+160*scale),round(cy-22*scale)),(round(cx+121*scale),round(cy-8*scale))],fill=INK)
    d.ellipse(box(104,-53,112,-45),fill=BG)

def paint(i, item):
    title,line1,line2,duration=item
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
    d.rectangle((33,33,W-33,H-33),outline=(68,61,49),width=2)
    d.line((68,138,W-68,138),fill=GOLD,width=3)
    center(d,82,'F I N A L   V E S T I G E',brand,GOLD)
    center(d,184,title,regular,GOLD)
    if i==0:
        d.ellipse((92,272,448,628),outline=GOLD,width=3);draw_bear(d,255,449,.85)
    elif i==1:
        d.ellipse((200,306,340,444),outline=GOLD,width=7);d.arc((166,298,378,548),30,150,fill=GOLD,width=5);d.polygon([(270,400),(237,505),(303,505)],fill=INK);d.ellipse((249,494,291,532),fill=GOLD)
    elif i==2:
        d.ellipse((110,268,430,588),outline=GOLD,width=5);d.ellipse((184,340,356,512),fill=(36,34,28));d.ellipse((234,388,306,460),fill=GOLD);center(d,598,'OBSERVATION ≠ CAUSE',small,MUTED)
    elif i==3:
        for j in range(6):
            x=115+j*59;y=370+round(90*__import__('math').sin(j*1.2));d.ellipse((x,y,x+28,y+28),fill=GOLD if j%2 else INK)
        d.arc((110,300,450,610),25,300,fill=GOLD,width=8)
    elif i==4:
        d.line((270,305,130,540),fill=GOLD,width=8);d.line((270,305,410,540),fill=INK,width=8);d.ellipse((240,275,300,335),fill=INK)
        d.text((80,570),'FORCE',font=small,fill=GOLD);d.text((333,570),'RETURN',font=small,fill=GOLD)
    else:
        d.ellipse((141,300,399,558),outline=GOLD,width=5)
        center(d,405,'?',large,INK)
        d.line((96,606,444,606),fill=GOLD,width=2)
    center(d,728,line1,regular,INK)
    center(d,773,line2,small,MUTED)
    center(d,880,f'MIND & PERCEPTION   ·   {i+1:02d} / 06',brand,GOLD)
    im.save(OUT/f'scene-{i+1:02d}.png',optimize=True)

for i,s in enumerate(scenes):paint(i,s)
# Concatenated still illustrations deliberately avoid needless 480 individual image files.
concat=OUT/'scene-timings.ffconcat'
with concat.open('w') as f:
    f.write('ffconcat version 1.0\n')
    for i,s in enumerate(scenes):
        f.write(f"file 'scene-{i+1:02d}.png'\nduration {s[3]}\n")
    f.write("file 'scene-06.png'\n")
mp4=OUT/'the-white-bear-40s.mp4'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-safe','0','-f','concat','-i',str(concat),'-vf','fps=12,format=yuv420p','-t','40','-an','-c:v','libx264','-preset','veryfast','-crf','20','-movflags','+faststart',str(mp4)],check=True)
probe=json.loads(subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(mp4)],capture_output=True,text=True,check=True).stdout)
v=probe['streams'][0]
assert v['codec_name']=='h264' and v['width']==540 and v['height']==960
assert abs(float(probe['format']['duration'])-40)<.02 and abs(int(v.get('nb_frames',480))-480)<=1,probe
# Captions match six contiguous scene intervals.
acc=0;vtt=['WEBVTT','']
for i,(title,a,b,dur) in enumerate(scenes):
    def ts(t):return f'00:{t//60:02d}:{t%60:02d}.000'
    vtt.extend([str(i+1),f'{ts(acc)} --> {ts(acc+dur)}',a+' '+b,''])
    acc+=dur
assert acc==40
(OUT/'captions.vtt').write_text('\n'.join(vtt))
# Review player and contact sheet, no telemetry.
(OUT/'review.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Original White Bear Film Review</title><main><h1>Original White Bear Film Review</h1><p>Silent, optional, no autoplay, no analytics or external content.</p><video controls preload="none" poster="scene-01.png" width="360"><source src="the-white-bear-40s.mp4" type="video/mp4"><track kind="captions" srclang="en" label="English captions" src="captions.vtt" default></video><p>Full transcript: the six English caption intervals are in <a href="captions.vtt">captions.vtt</a>.</p></main></html>''')
contact=Image.new('RGB',(W*3,H*2));
for i in range(6):contact.paste(Image.open(OUT/f'scene-{i+1:02d}.png'),((i%3)*W,(i//3)*H))
contact.thumbnail((810,960));contact.save(OUT/'contact-sheet.jpg',quality=85)
zip_path=OUT/'offline-review.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
    for p in [mp4,OUT/'scene-01.png',OUT/'contact-sheet.jpg',OUT/'captions.vtt',OUT/'review.html',Path(__file__)]:z.write(p,arcname=p.name)
with zipfile.ZipFile(zip_path) as z:assert z.testzip() is None
print(json.dumps({'duration':probe['format']['duration'],'frames':v.get('nb_frames'),'dimensions':[v['width'],v['height']],'codec':v['codec_name'],'bytes':mp4.stat().st_size,'sha256':hashlib.sha256(mp4.read_bytes()).hexdigest(),'zip_bytes':zip_path.stat().st_size}))
