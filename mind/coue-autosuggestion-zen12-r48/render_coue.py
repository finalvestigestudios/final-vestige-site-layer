#!/usr/bin/env python3
"""Original silent film: six evidence-oriented scenes, exactly 40 seconds at 12 fps.
Requires Pillow and ffmpeg. Offline editorial preview; never a merchant testimonial.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import subprocess, hashlib, json

BASE = Path(__file__).resolve().parent
SIZE = (540, 960)
BG = '#0b0e0d'
GOLD = '#d2ad72'
INK = '#f3eadb'
MUTED = '#c3bbab'
SCENES = [
    (6, 'NANCY, FRANCE', ['A practice counted', 'by hand.'], 'A small object, a large promise.'),
    (7, 'TWENTY REPETITIONS', ['Morning.', 'And night.'], 'Coué described the ritual in 1922.'),
    (7, 'COUNTING IS NOT PROOF', ['The knots measured', 'words spoken.'], 'They did not measure recovery.'),
    (7, 'CLAIM  /  COMPARISON', ['Testimony tells us', 'what was reported.'], 'A control can help test a cause.'),
    (7, 'NOT THE SAME EXPERIMENT', ['Modern values-', 'affirmation differs.'], 'Its results are not Coué trials.'),
    (6, 'THE LAST KNOT', ['What does repetition', 'actually change?'], 'Read the original evidence trail.'),
]

def font(size, serif=False):
    paths = ['/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf' if serif else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
             '/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf' if serif else '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf']
    for path in paths:
        try: return ImageFont.truetype(path, size)
        except OSError: continue
    return ImageFont.load_default()

def center(draw, text, y, f, color):
    box = draw.textbbox((0, 0), text, font=f)
    draw.text(((SIZE[0] - (box[2] - box[0]))/2, y), text, font=f, fill=color)

def render(n, header, lines, sub):
    img=Image.new('RGB',SIZE,BG)
    d=ImageDraw.Draw(img)
    d.rectangle((22,24,518,936), outline='#665641', width=2)
    d.line((44,96,496,96),fill='#574933',width=2)
    d.text((44,46),'FINAL VESTIGE   /   MIND',font=font(16),fill=GOLD)
    d.text((44,132),f'0{n+1}  /  06',font=font(19),fill=MUTED)
    center(d,header,220,font(21),GOLD)
    # an original knotted string diagram; length changes to highlight the scene
    coords=[(255 + int(39*__import__('math').sin(i*.6)),350+i*17) for i in range(20)]
    d.line(coords,fill='#e7dece',width=4,joint='curve')
    for i,(x,y) in enumerate(coords):
        c=GOLD if i <= (n+1)*3 else '#6d5840'
        d.ellipse((x-6,y-6,x+6,y+6),fill=c,outline='#f3ddad' if i == n*3 else c,width=2)
    for k,line in enumerate(lines): center(d,line,741+k*59,font(32,True),INK)
    center(d,sub,873,font(15),MUTED)
    d.line((44,920,496,920),fill='#574933',width=2)
    img.save(BASE/f'scene-{n+1:02}.png',optimize=True)
    return img

for i,(seconds,header,lines,sub) in enumerate(SCENES): render(i,header,lines,sub)
# Local review poster is a frame from the actual original render, not a screenshot of third-party art.
Image.open(BASE/'scene-01.png').save(BASE/'twenty-knots-poster.png')
concat = BASE/'frames.ffconcat'
concat.write_text('ffconcat version 1.0\n'+''.join(f"file 'scene-{i+1:02}.png'\nduration {sec}\n" for i,(sec,*_) in enumerate(SCENES)) + "file 'scene-06.png'\n",encoding='utf-8')
mp4=BASE/'twenty-knots-original-40s.mp4'
cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-safe','0','-f','concat','-i',str(concat),'-r','12','-frames:v','480','-an','-c:v','libx264','-pix_fmt','yuv420p','-movflags','+faststart','-crf','23',str(mp4)]
subprocess.run(cmd,check=True)
meta=subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=codec_name,width,height,r_frame_rate,nb_frames:format=duration,size','-of','json',str(mp4)],text=True)
info=json.loads(meta)
assert abs(float(info['format']['duration'])-40)<.01, info
assert info['streams'][0]['nb_frames']=='480',info
assert info['streams'][0]['codec_name']=='h264',info
print(json.dumps({'video':str(mp4),'poster':str(BASE/'twenty-knots-poster.png'),'sha256':hashlib.sha256(mp4.read_bytes()).hexdigest(),'metadata':info},indent=2))
