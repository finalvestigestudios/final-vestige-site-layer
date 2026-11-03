#!/usr/bin/env python3
"""Original, silent Mind R90 educational animation; no experiment footage or product promotion."""
from PIL import Image, ImageDraw, ImageFont
import math, os, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parent
W,H,FPS,DURATION=540,960,12,40
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
SANS='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
GOLD=(212,178,123); IVORY=(244,235,219); MUTE=(179,173,159)
SCENES=[
 (0,7,['A HAND','IS NOT','YOUR HAND.'],'Two hands; one is hidden.'),
 (7,14,['TWO TOUCHES.','ONE MOMENT.'],'A pair of brushes move in time.'),
 (14,21,['SOME FEEL','OWNERSHIP.'],'The report can shift.'),
 (21,28,['VISION.','TOUCH.','POSITION.'],'Three channels, one proposed cause.'),
 (28,34,['BUT WHAT','WAS EXPECTED?'],'Expectations affect reports.'),
 (34,40,['A REPORT','IS NOT','A CAUSE.'],'Follow the evidence.')
]
def font(size,serif=False):return ImageFont.truetype(SERIF if serif else SANS,size)
def centered(draw,text,y,f,fill):
    b=draw.textbbox((0,0),text,font=f)
    draw.text(((W-(b[2]-b[0]))/2,y),text,font=f,fill=fill)
def draw_frame(seconds):
    scene=next((i for i,(a,b,*_) in enumerate(SCENES) if a<=seconds<b),5)
    a,b,lines,note=SCENES[scene]; p=(seconds-a)/(b-a)
    im=Image.new('RGB',(W,H),(9,13,15));d=ImageDraw.Draw(im)
    for y in range(H):
        q=y/H; d.line((0,y,W,y),fill=(int(10+8*q),int(14+10*q),int(15+9*q)))
    d.rectangle((42,40,498,922),outline=(67,63,55),width=2)
    d.line((46,118,494,118),fill=GOLD,width=2)
    d.text((60,65),'FINAL VESTIGE  /  MIND',font=font(17),fill=GOLD)
    centered(d,'ILLUSION / EVIDENCE',154,font(17),MUTE)
    sway=math.sin(seconds*2.3)*11
    # Two original schematic hand shapes: not photographed or copied study stimuli
    for idx,x in enumerate((142,310)):
        yy=int(370+sway*(1 if idx==0 else -1)); color=(120,118,107) if idx==0 else (190,160,113)
        # palm and fingers
        d.rounded_rectangle((x,yy,x+84,yy+174),radius=24,fill=color)
        for k,dh in enumerate((40,16,4,22)):
            px=x+5+k*20;d.rounded_rectangle((px,yy-56+dh,px+15,yy+50),radius=8,fill=color)
        d.ellipse((x-16,yy+65,x+15,yy+130),fill=color)
    if scene in (1,2,3):
        for x in (184,352):
            rr=38+int(p*65)
            d.ellipse((x-rr,400-rr,x+rr,400+rr),outline=GOLD,width=3)
    d.line((270,310,270,610),fill=(97,82,60),width=2)
    for j,line in enumerate(lines):
        centered(d,line,615+j*54,font(38,True),IVORY)
    centered(d,note,827,font(16),MUTE)
    d.rectangle((60,899,60+int(420*seconds/DURATION),905),fill=GOLD)
    d.text((65,930),f'{seconds:05.1f} / 40.0',font=font(12),fill=MUTE)
    return im

def main():
    poster=draw_frame(17.1);poster.save(ROOT/'poster.png')
    proc=subprocess.Popen(['ffmpeg','-loglevel','error','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','25','-pix_fmt','yuv420p','-movflags','+faststart',str(ROOT/'the-hand-did-not-move-40s.mp4')],stdin=subprocess.PIPE)
    for i in range(DURATION*FPS):
        proc.stdin.write(draw_frame(i/FPS).tobytes())
    proc.stdin.close(); rc=proc.wait()
    if rc:raise RuntimeError(f'ffmpeg exited {rc}')
if __name__=='__main__':main()
