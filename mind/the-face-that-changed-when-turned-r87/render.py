#!/usr/bin/env python3
"""Original editorial schematic animation; no borrowed images, no ads, no telemetry.
Usage: python render.py; requires Pillow and ffmpeg. 40s, 540x960, 12fps, H.264.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import subprocess, math, zipfile, shutil
W,H,FPS,DUR=540,960,12,40
BASE=Path(__file__).resolve().parent
BG=(10,11,11); GOLD=(205,170,110); TEXT=(243,235,220); MUTED=(184,175,163)
try:
    FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
    BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    def font(size,bold=False,serif=False):return ImageFont.truetype(SERIF if serif else BOLD if bold else FONT,size)
except OSError:
    def font(size,bold=False,serif=False):return ImageFont.load_default()
scenes=[(0,6,'UPSIDE DOWN','The face seems ordinary.','But the features are already altered.'),
        (6,13,'THE LOCAL PARTS','The eyes and mouth have been','turned inside the same outline.'),
        (13,20,'TURN THE WHOLE','Now the arrangement looks strange.','Nothing inside the image changed.'),
        (20,26,'SAME PARTS. NEW CONTEXT.','What we perceive depends','on how the whole is oriented.'),
        (26,33,'1980 / 2010','Thompson documented the effect.','Wong and colleagues tested other objects.'),
        (33,40,'FOLLOW THE EVIDENCE','The reported experience is real.','Its explanation requires careful testing.')]
def draw_center(d,txt,y,ft,fill=TEXT):
    box=d.textbbox((0,0),txt,font=ft)
    d.text(((W-(box[2]-box[0]))/2,y),txt,font=ft,fill=fill)
def face_art(size=310):
    img=Image.new('RGBA',(size,size+55),(0,0,0,0)); d=ImageDraw.Draw(img)
    cx=size//2;cy=(size+55)//2
    d.ellipse((cx-106,cy-142,cx+106,cy+142),outline=GOLD,width=6,fill=(26,28,28,255))
    # Facial features deliberately locally inverted; an illustration, not an experimental stimulus.
    for ex in (cx-47,cx+47):
        d.arc((ex-29,cy-57,ex+29,cy-14),20,160,fill=TEXT,width=8)
        d.arc((ex-22,cy-61,ex+22,cy-20),190,340,fill=MUTED,width=4)
    d.arc((cx-65,cy+8,cx+65,cy+89),177,359,fill=TEXT,width=9)
    return img
FACE=face_art()
def frame(t):
    i=next(j for j,s in enumerate(scenes) if s[0]<=t<s[1]);a,z,head,l1,l2=scenes[i]
    img=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(img)
    d.rectangle((22,22,W-22,H-22),outline=(104,88,64),width=2)
    d.text((48,49),'FINAL VESTIGE  /  MIND & PERCEPTION',font=font(17,True),fill=GOLD)
    d.line((46,89,W-46,89),fill=(70,63,51),width=2)
    draw_center(d,head,140,font(25,True),GOLD)
    if i in (0,1,2,3):
        # Inverted whole in first half, then returns upright. Local features fixed.
        if i in (0,1):angle=180
        elif i==2: angle=180*(1-min(1,max(0,(t-13)/4.5)))
        else:angle=0
        art=FACE.rotate(angle,resample=Image.Resampling.BICUBIC,expand=False)
        img.paste(art,((W-art.width)//2,256),art)
        d=ImageDraw.Draw(img)
        if i==1:
            d.ellipse((W//2-73,399,W//2+73,465),outline=(167,110,85),width=3)
        if i==3:
            d.text((88,662),'the drawing did not change',font=font(18),fill=MUTED)
    elif i==4:
        d.line((80,360,W-80,360),fill=GOLD,width=4)
        for y,year,title in [(405,'1980','THOMPSON / PERCEPTION'),(515,'2010','WONG ET AL. / PERCEPTION')]:
            d.text((80,y),year,font=font(50,serif=True),fill=GOLD)
            d.text((80,y+65),title,font=font(18,True),fill=TEXT)
    else:
        d.rounded_rectangle((70,322,470,657),radius=9,outline=GOLD,width=3)
        draw_center(d,'SOURCE',380,font(44,serif=True),TEXT)
        draw_center(d,'≠',447,font(52,serif=True),GOLD)
        draw_center(d,'CONCLUSION',528,font(38,serif=True),TEXT)
    d=ImageDraw.Draw(img)
    d.line((48,740,W-48,740),fill=(71,62,48),width=1)
    draw_center(d,l1,771,font(21),TEXT)
    draw_center(d,l2,806,font(19),MUTED)
    d.text((46,903),'ILLUSTRATED, NOT EXPERIMENTAL FOOTAGE',font=font(14),fill=MUTED)
    d.rectangle((48,882,48+(W-96)*(t/DUR),886),fill=GOLD)
    return img

def main():
    mp4=BASE/'the-face-was-always-altered-40s.mp4'
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-vcodec','rawvideo','-s',f'{W}x{H}','-pix_fmt','rgb24','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','24','-pix_fmt','yuv420p','-movflags','+faststart',str(mp4)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    samples=[]
    for i in range(FPS*DUR):
        t=i/FPS;im=frame(t)
        if i in (6*FPS//2,9*FPS,16*FPS,23*FPS,29*FPS,37*FPS):samples.append(im.copy())
        proc.stdin.write(im.tobytes())
    proc.stdin.close();code=proc.wait()
    if code:raise RuntimeError(f'ffmpeg returned {code}')
    im=frame(0);im.save(BASE/'poster.png',optimize=True)
    sheet=Image.new('RGB',(W*3,H*2),BG)
    for n,im in enumerate(samples):sheet.paste(im,((n%3)*W,(n//3)*H))
    sheet.resize((810,960)).save(BASE/'contact-sheet.jpg',quality=82)
    print('Rendered',mp4,mp4.stat().st_size,'bytes')
if __name__=='__main__':main()
