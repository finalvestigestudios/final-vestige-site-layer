#!/usr/bin/env python3
"""Original six-scene Troxler video, 40s silent; educational schematic, no efficacy claims.
Uses Pillow and ffmpeg; generate still segments instead of storing 480 frame files.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import subprocess, textwrap

ROOT = Path(__file__).parent
W, H = 540, 960
BG = (17, 27, 32)
PANEL = (36, 55, 62)
CREAM = (245, 239, 224)
GOLD = (234, 203, 148)
MUTED = (210, 218, 208)
MINT = (162, 208, 183)
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
ft = lambda size, bold=False: ImageFont.truetype(BOLD if bold else FONT, size)
SCENES = [
    ('THE DOT DID NOT MOVE', 'Look at the pale dot while keeping your eyes at the center.', 6, 0),
    ('THE APPEARANCE FADES', 'Sometimes a peripheral shape fades, though the image remains in place.', 7, 1),
    ('THE CONDITIONS MATTER', 'Contrast, position, adaptation and eye movements can influence fading.', 7, 2),
    ('TWO DIFFERENT QUESTIONS', 'What changed in experience? What remained on the page?', 7, 3),
    ('A CLAIM IS NOT A TRIAL', 'Twelve-minute audio is a format. An hour of benefits needs product-specific evidence.', 7, 4),
    ('LOOK FOR THE EVIDENCE', 'Try a free short practice. Ask what was actually measured.', 6, 5),
]

def centered(draw, text, y, font, fill, max_width=474, spacing=11):
    lines=[]
    for part in text.split('\n'):
        words=part.split(); line=''
        for word in words:
            trial=(line+' '+word).strip()
            if line and draw.textbbox((0,0),trial,font=font)[2] > max_width:
                lines.append(line);line=word
            else:line=trial
        if line:lines.append(line)
    height=font.size+spacing
    for row in lines:
        left=(W-draw.textbbox((0,0),row,font=font)[2])/2
        draw.text((left,y),row,font=font,fill=fill)
        y+=height
    return y

def make_scene(i,title,body,variant):
    im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
    d.rounded_rectangle((26,190,514,644),radius=24,fill=PANEL,outline=(98,120,117),width=2)
    # Decorative but genuinely authored fixed cross + peripheral disc.
    cx,cy=250,399
    d.line((cx-27,cy,cx+27,cy),fill=GOLD,width=6)
    d.line((cx,cy-27,cx,cy+27),fill=GOLD,width=6)
    if variant in (0,1,2,3):
        alpha=[220,95,180,200][variant]
        glow=Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(glow)
        gd.ellipse((389,361,460,432),fill=(*MINT,alpha))
        im=Image.alpha_composite(im.convert('RGBA'),glow).convert('RGB'); d=ImageDraw.Draw(im)
    elif variant==4:
        d.rounded_rectangle((85,491,455,570),radius=16,fill=(47,69,75),outline=GOLD,width=2)
        centered(d,'12 MIN ≠ 60 MIN OF PROVEN BENEFIT',506,ft(18,True),CREAM,340,6)
    else:
        d.ellipse((391,361,459,429),outline=MINT,width=5)
        d.line((414,397,429,411,458,374),fill=GOLD,width=6,joint='curve')
    centered(d,title,60,ft(30,True),CREAM,500,10)
    centered(d,body,684,ft(26),CREAM,450,14)
    d.line((52,866,488,866),fill=(131,118,94),width=2)
    centered(d,'FINAL VESTIGE  |  MIND & PERCEPTION',884,ft(16,True),MUTED,490)
    out=ROOT/f'scene{i:02d}.png'; im.save(out,optimize=True)
    return out

def render():
    paths=[]
    for i,(title,body,duration,variant) in enumerate(SCENES):paths.append((make_scene(i,title,body,variant),duration))
    seq=ROOT/'sequence.ffconcat'
    def q(p):return p.as_posix().replace("'","'\\''")
    seq.write_text('ffconcat version 1.0\n'+''.join(f"file '{q(p)}'\nduration {dur}\n" for p,dur in paths)+f"file '{q(paths[-1][0])}'\n")
    dst=ROOT/'troxler-evidence-40s.mp4'
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(seq),'-vf','fps=12,format=yuv420p','-c:v','libx264','-preset','veryfast','-crf','24','-movflags','+faststart','-t','40',str(dst)],check=True)
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(dst),'-ss','00:00:03.0','-frames:v','1',str(ROOT/'troxler-film-poster.png')],check=True)
    print(dst)

if __name__=='__main__':render()
