#!/usr/bin/env python3
"""Build a silent, original, optional 42-second Zen12 evidence explainer. No seller creatives or tracking."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess

HERE = Path(__file__).resolve().parent
W, H = 1280, 720
BG, GOLD, WHITE, MUTED = '#101a29', '#e4b96d', '#f6f1e9', '#bec7d1'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
REG = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def font(sz, bold=False):
    return ImageFont.truetype(BOLD if bold else REG, sz)

STORY = [
('01 / THE QUESTION', 'Twelve minutes is\na manageable start.', 'A short routine can be convenient. That is a format benefit.'),
('02 / THE DISTINCTION', 'FORMAT DOES\nNOT EQUAL PROOF.', 'A helpful schedule is not scientific evidence of a promised outcome.'),
('03 / THE SELLER', 'Zen12 describes\nshort audio sessions.', 'Its listed levels and listening styles are seller-described features.'),
('04 / THE STUDIES', 'The science is\nmore complicated.', 'Binaural-beat studies are mixed; this is not a Zen12 clinical trial.'),
('05 / THE FREE TEST', 'Try twelve quiet\nminutes for free.', 'Notice whether a short repeatable routine fits your day.'),
('06 / THE DECISION', 'Read the evidence.\nCheck the exact terms.', 'No product link without verified partner authorization.'),
]

def card(i, eyebrow, headline, sub):
    image = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(image)
    for y in range(0,H,6):
        t=y/H
        d.line([(0,y),(W,y)],fill=(int(16+5*t),int(26+7*t),int(41+11*t)),width=6)
    d.rounded_rectangle((55,50,1225,669), radius=34,outline=(70,85,105),width=2)
    d.rectangle((93,112,185,120), fill=GOLD)
    d.text((95,153),eyebrow,font=font(27,True),fill=GOLD)
    if i in (0,4):
        d.ellipse((892,182,1113,403),outline=GOLD,width=12)
        d.line([(1002,292),(1002,222)],fill=WHITE,width=12)
        d.line([(1002,292),(1057,328)],fill=WHITE,width=12)
        d.ellipse((992,282,1012,302),fill=WHITE)
    elif i in (1,3):
        for j in range(4):
            x=875+j*70
            d.rounded_rectangle((x,185+20*j,x+42,420-15*j),radius=18,outline=GOLD,width=6)
        d.line([(858,468),(1140,468)],fill=GOLD,width=6)
    else:
        d.rounded_rectangle((892,173,1138,412),radius=14,fill='#e5dfd1')
        for j in range(5):
            d.line([(917,218+j*38),(1113-j*13,218+j*38)],fill='#687581',width=8)
    y=268
    for line in headline.split('\n'):
        d.text((95,y),line,font=font(59,True),fill=WHITE,stroke_width=1)
        y+=82
    d.rounded_rectangle((95,525,1185,614),radius=11,fill='#243449')
    d.text((118,548),sub,font=font(23),fill=MUTED)
    d.text((97,633),'FINAL VESTIGE STUDIOS  /  EVIDENCE BEFORE CLAIMS',font=font(16,True),fill=GOLD)
    out=HERE/f'card_{i+1:02}.png'
    image.save(out,optimize=True)
    return out

def main():
    cards=[card(i,*v) for i,v in enumerate(STORY)]
    args=['ffmpeg','-y','-hide_banner','-loglevel','error']
    for c in cards:
        args.extend(['-loop','1','-framerate','24','-t','7.5','-i',str(c)])
    filters=[]
    for i in range(6):
        filters.append(f'[{i}:v]format=yuv420p,setsar=1[v{i}]')
    head='v0'
    for i in range(1,6):
        name=f'x{i}'
        filters.append(f'[{head}][v{i}]xfade=transition=fade:duration=0.6:offset={6.9*i:.1f}[{name}]')
        head=name
    out=HERE/'ZEN12_R481_ORIGINAL_42S_SILENT_PREVIEW.mp4'
    args.extend(['-filter_complex',';'.join(filters),'-map',f'[{head}]','-an','-c:v','libx264','-preset','veryfast','-crf','27','-pix_fmt','yuv420p','-r','24','-movflags','+faststart','-threads','2',str(out)])
    subprocess.run(args,check=True)
    print(out)

if __name__=='__main__': main()
