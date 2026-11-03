#!/usr/bin/env python3
"""Original 40-second McGurk history explainer, NOT an audiovisual perception experiment.
Run: python render.py. Requires Pillow and ffmpeg. No borrowed images, audio, trackers or ads.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math, subprocess
OUT=Path(__file__).resolve().parent
W,H,FPS,DURATION=540,960,12,40
BG=(10,13,15); GOLD=(206,167,103); IVORY=(245,239,229); SMOKE=(189,185,178)
F='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
B='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
S='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
def font(size,face=F):return ImageFont.truetype(face,size)
def middle(d,words,y,size,face=F,color=IVORY):
    f=font(size,face);bbox=d.textbbox((0,0),words,font=f)
    d.text(((W-(bbox[2]-bbox[0]))/2,y),words,font=f,fill=color)
SCENES=[(0,6,'THE SOUND YOU SAW','A film carried two conflicting clues.','McGurk and MacDonald / 1976'),
(6,13,'VISIBLE /ga/','The illustrated lips formed ga.','This is schematic, not a lab stimulus.'),
(13,20,'RECORDED /ba/','The soundtrack was ba.','The sound itself did not say da.'),
(20,27,'REPORTED /da/','Some listeners heard a third syllable.','Others may experience it differently.'),
(27,34,'NOT UNIVERSAL','People differ in susceptibility.','A clip cannot diagnose your hearing.'),
(34,40,'SOURCE  ≠  CAUSE','Experience and evidence are distinct.','Discover the original 1976 record.')]
def frame(t):
    scene=next(i for i,(start,end,*_) in enumerate(SCENES) if start<=t<end)
    _,_,title,sub,tag=SCENES[scene]
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
    d.rectangle((24,24,W-24,H-24),outline=(94,74,51),width=2)
    d.text((45,46),'FINAL VESTIGE  /  THE MIND ARCHIVE',font=font(16,B),fill=GOLD)
    d.line((44,89,W-44,89),fill=(74,61,46),width=2)
    middle(d,title,150,26,B,GOLD)
    # Schematic signal diagram: waveform and lip shape are educational symbols.
    if scene in (0,1,2,3):
        d.ellipse((152,286,388,547),outline=GOLD,width=6)
        d.arc((190,348,350,478),195,347,fill=IVORY,width=10)
        d.line((90,619,450,619),fill=(78,88,92),width=2)
        for x in range(90,450,4):
            q=(x-90)/360
            amp=16+34*math.sin(math.pi*q)**2
            yy=619+amp*math.sin((x-90)*.095 + t*3)
            d.line((x,619,x,yy),fill=(198,165,108),width=2)
        middle(d,['SEE  +  HEAR','LIPS /ga/','AUDIO /ba/','PERCEPT /da/'][scene],674,24,B)
        if scene==3:middle(d,'not the recorded sound',715,18,color=SMOKE)
    elif scene==4:
        for n,x in enumerate((120,205,290,375,440)):
            radius=[21,28,13,34,16][n]
            d.ellipse((x-radius,370-radius,x+radius,370+radius),fill=GOLD if n%2 else SMOKE)
        middle(d,'individual responses differ',535,19)
    else:
        d.rounded_rectangle((78,325,462,594),outline=GOLD,width=3,radius=14)
        middle(d,'REPORT',389,37,S)
        middle(d,'≠',459,55,S,GOLD)
        middle(d,'EXPLANATION',538,29,S)
    d.line((46,756,W-46,756),fill=(82,68,51),width=1)
    middle(d,sub,785,18,color=IVORY)
    middle(d,tag,817,16,color=SMOKE)
    d.rectangle((46,881,46+round((W-92)*t/DURATION),885),fill=GOLD)
    d.text((43,902),'ILLUSTRATION — NOT EXPERIMENTAL FOOTAGE',font=font(13),fill=SMOKE)
    return im
def main():
    dest=OUT/'the-sound-you-saw-40s.mp4'
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','ultrafast','-crf','30','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for n in range(FPS*DURATION):p.stdin.write(frame(n/FPS).tobytes())
    p.stdin.close()
    if p.wait():raise RuntimeError('ffmpeg failed')
    frame(0).save(OUT/'poster.png',optimize=True)
    print(dest,dest.stat().st_size,'bytes')
if __name__=='__main__':main()
