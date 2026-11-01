"""Original self-contained silent educational film for FV Mind presell R56.
Dependencies: Pillow, ffmpeg. No external graphics, media, fonts, or network calls.
Output is review-only and not a representation of Zen12 results or scientific experiment.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import subprocess, math, hashlib, json
ROOT=Path(__file__).parent
W,H=540,960
SCENES=[
  (7,"TWELVE MINUTES","A duration is a commitment.\nNot a measured outcome.","Start with the question."),
  (7,"WHY SOUND?","Some people prefer a\nguided voice. Others\nprefer quiet.","Preference is not efficacy."),
  (7,"FOUR FORMATS","Zen12 advertises music,\nnature, white noise,\nand guided audio.","Seller-described features."),
  (7,"THE EVIDENCE GAP","General meditation\nresearch does not test\nthis specific product.","No hour-for-twelve proof."),
  (6,"TRY THE FREE TEST","Choose a quiet spot.\nSet a 12-minute timer.\nRecord what you notice.","No purchase required."),
  (6,"BEFORE YOU BUY","Check consent, privacy,\ncheckout terms and\nwhat you actually need.","Independent guide · FV"),
]
BG=(9,11,12); PANEL=(20,23,22); GOLD=(201,166,108); WHITE=(245,239,226); MUTED=(197,193,181); BORDER=(77,69,55)
font_regular='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font_bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
F_TITLE=ImageFont.truetype(font_bold,40)
F_BODY=ImageFont.truetype(font_regular,30)
F_LABEL=ImageFont.truetype(font_bold,20)
F_FOOT=ImageFont.truetype(font_regular,20)

def center(draw, y, text, font, color):
    box=draw.textbbox((0,0),text,font=font)
    draw.text(((W-(box[2]-box[0]))/2,y),text,font=font,fill=color)

def scene(i, label, body, foot):
    im=Image.new('RGB',(W,H),BG)
    d=ImageDraw.Draw(im)
    # Distinctive source-desk clock dial, not actual moving timepiece demonstration.
    cx,cy=W//2,275
    d.ellipse((cx-145,cy-145,cx+145,cy+145),outline=BORDER,width=4)
    d.ellipse((cx-123,cy-123,cx+123,cy+123),outline=GOLD,width=3)
    for k in range(12):
        ang=(k*math.pi/6)-math.pi/2
        a,b=113,124
        d.line((cx+a*math.cos(ang),cy+a*math.sin(ang),cx+b*math.cos(ang),cy+b*math.sin(ang)),fill=GOLD,width=4)
    pointer=(-1.1+i*0.35)
    d.line((cx,cy,cx+91*math.cos(pointer),cy+91*math.sin(pointer)),fill=WHITE,width=6)
    d.line((cx,cy,cx+49*math.cos(pointer+1.85),cy+49*math.sin(pointer+1.85)),fill=GOLD,width=5)
    d.ellipse((cx-7,cy-7,cx+7,cy+7),fill=WHITE)
    center(d,465,label,F_TITLE,WHITE)
    for j,line in enumerate(body.split('\n')): center(d,555+j*47,line,F_BODY,MUTED)
    d.line((52,771,W-52,771),fill=BORDER,width=2)
    center(d,804,foot,F_LABEL,GOLD)
    d.text((36,44),'FINAL VESTIGE  /  MIND & PERCEPTION',font=F_LABEL,fill=GOLD)
    d.text((36,906),f'EDUCATIONAL REVIEW  •  {i+1:02}/06',font=F_FOOT,fill=MUTED)
    return im

pngs=[]
for i,(_,head,body,foot) in enumerate(SCENES):
    p=ROOT/f'scene-{i+1:02}.png'
    scene(i,head,body,foot).save(p,optimize=True)
    pngs.append(p)
# Poster is exact original frame; a real poster, not a disguised play button.
(ROOT/'poster.png').write_bytes(pngs[0].read_bytes())
with (ROOT/'frames.concat').open('w') as fh:
    for p,(duration,*_) in zip(pngs,SCENES):
        fh.write(f"file '{p.as_posix()}'\nduration {duration}\n")
    fh.write(f"file '{pngs[-1].as_posix()}'\n")
video=ROOT/'twelve-minutes-not-proof-40s.mp4'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-safe','0','-f','concat','-i',str(ROOT/'frames.concat'),'-vf','fps=12,format=yuv420p','-an','-c:v','libx264','-preset','medium','-crf','24','-movflags','+faststart','-t','40',str(video)],check=True)
meta=subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size','-of','json',str(video)],text=True)
print(json.dumps({'video':str(video),'metadata':json.loads(meta),'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'scenes':len(pngs)}))
