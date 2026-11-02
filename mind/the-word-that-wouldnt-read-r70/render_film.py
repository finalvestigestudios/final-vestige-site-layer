#!/usr/bin/env python3
"""Original silent R70 educational short. No commercial endorsements, network, tracking, or external assets.
Requires Pillow, ffmpeg and local DejaVu fonts. Output exact 40s 540x960 @ 12fps H264.
"""
from pathlib import Path
import math, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
W,H,FPS,SECONDS=540,960,12,40
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
if not Path(FONT).exists(): FONT='/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf'
if not Path(BOLD).exists(): BOLD=FONT
if not Path(SERIF).exists(): SERIF=FONT
GOLD=(204,166,106);CREAM=(245,240,229);MUTED=(187,181,169);RED=(220,94,87);BLUE=(89,155,221)
SCENES=[
 (0,6, 'THE WORD', 'Your eyes see letters.\nYour mind has learned to read.'),
 (6,13, 'THE COLOR', 'Now name the ink,\nnot the written word.'),
 (13,20, 'THE CONFLICT', 'Two answers compete.\nThe delay can be measured.'),
 (20,27, 'THE SUGGESTION', 'A carefully chosen instruction\nchanged some performances.'),
 (27,34, 'THE COMPARISON', 'Not everyone responded\nin the same way.'),
 (34,40, 'THE LIMIT', 'A laboratory effect is not\na product promise.')
]

def font(size,bold=False,serif=False): return ImageFont.truetype(SERIF if serif else BOLD if bold else FONT,size)

def text_center(draw,text,y,ft,fill,spacing=11):
    draw.multiline_text((W/2,y),text,font=ft,fill=fill,anchor='ma',align='center',spacing=spacing)

def frame(index):
    t=index/FPS
    im=Image.new('RGB',(W,H),(12,14,15));d=ImageDraw.Draw(im,'RGBA')
    for y in range(H):
        distance=abs(y/H-.4)
        warm=int(9*(1-distance))
        d.line((0,y,W,y),fill=(16+warm,17+warm//2,17,255))
    d.rectangle((34,35,W-35,H-35),outline=(204,166,106,110),width=2)
    d.rectangle((45,46,W-45,H-46),outline=(204,166,106,20),width=1)
    d.text((63,85),'FINAL VESTIGE   /   MIND',font=font(17,True),fill=GOLD)
    sc=next((n,s,e,title,desc) for n,(s,e,title,desc) in enumerate(SCENES) if s<=t<e)
    n,s,e,title,desc=sc
    local=(t-s)/(e-s)
    alpha=max(0.25,min(1,local*5,(1-local)*5))
    d.text((63,171),f'EXPERIMENT NOTE  /  0{n+1}',font=font(17),fill=MUTED)
    slide=round((1-alpha)*22)
    if n in (0,1,2):
        if n==0:
            d.text((W/2,410+slide),'BLUE',font=font(112,True),fill=RED,anchor='mm')
            d.line((78,476,W-78,476),fill=GOLD,width=5)
        elif n==1:
            d.text((W/2,360+slide),'GREEN',font=font(90,True),fill=BLUE,anchor='mm')
            d.text((W/2,480+slide),'RED',font=font(112,True),fill=(97,198,143),anchor='mm')
        else:
            d.text((W/2,390+slide),'RED',font=font(115,True),fill=BLUE,anchor='mm')
            d.line((78,492,W-78,492),fill=(112,106,93),width=2)
            d.text((W/2,522),'WORD  /  INK',font=font(22),fill=MUTED,anchor='mm')
    elif n==3:
        d.rounded_rectangle((78,330,W-78,555),radius=7,outline=GOLD,width=2,fill=(18,20,20,255))
        d.text((W/2,391+slide),'READ DIFFERENTLY',font=font(25,True),fill=CREAM,anchor='mm')
        d.text((W/2,456),'INSTRUCTION ≠ PROOF',font=font(17),fill=GOLD,anchor='mm')
    elif n==4:
        for label,y,length,color in [('HIGH RESPONSE',370,308,GOLD),('LOW RESPONSE',480,165,MUTED)]:
            d.text((88,y-35),label,font=font(19,True),fill=CREAM)
            d.rounded_rectangle((88,y,88+length, y+23),radius=5,fill=color)
        d.text((W/2,570),'A diagram, not study data',font=font(18),fill=MUTED,anchor='mm')
    else:
        d.text((W/2,370),'EVIDENCE',font=font(71,True),fill=GOLD,anchor='mm')
        d.line((86,421,W-86,421),fill=RED,width=5)
        text_center(d,'NOT A GUARANTEE',490,font(30,True),CREAM)
    d.text((63,654),title,font=font(27,True),fill=GOLD)
    d.multiline_text((63,710),desc,font=font(24,serif=True),fill=CREAM,spacing=14)
    d.line((63,866,W-63,866),fill=(204,166,106,130),width=1)
    d.text((63,889),'EDUCATIONAL / NO PRODUCT ENDORSEMENT',font=font(13),fill=MUTED)
    # Accurate timeline and no bouncing / rapid flashing.
    d.rectangle((0,952,round(W*(t/SECONDS)),960),fill=GOLD)
    return im

if __name__=='__main__':
    with tempfile.TemporaryDirectory(prefix='fv-r70-') as directory:
        p=Path(directory)
        for idx in range(FPS*SECONDS): frame(idx).save(p/f'{idx:04d}.png',compress_level=1)
        output=ROOT/'the-word-and-the-ink-40s.mp4'
        cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate',str(FPS),'-i',str(p/'%04d.png'),'-an','-c:v','libx264','-preset','veryfast','-pix_fmt','yuv420p','-movflags','+faststart','-r',str(FPS),str(output)]
        subprocess.run(cmd,check=True)
    frame(0).save(ROOT/'poster.png')
    contact=Image.new('RGB',(W*2,H*3),(10,10,10))
    for idx,(start,*_) in enumerate(SCENES): contact.paste(frame(start*FPS+2),(idx%2*W,idx//2*H))
    contact.save(ROOT/'contact-sheet.jpg',quality=86)
    print('Rendered:',output)
