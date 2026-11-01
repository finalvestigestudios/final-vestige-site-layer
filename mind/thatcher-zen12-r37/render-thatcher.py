#!/usr/bin/env python3
"""Original editorial microfilm, not a clinical or research stimulus.
Requires Pillow and FFmpeg. Output is silent 40-second H.264 portrait video.
"""
import math, pathlib, subprocess
from PIL import Image, ImageDraw, ImageFont
OUT=pathlib.Path(__file__).resolve().parent
W,H,FPS,SEC=540,960,12,40
BG='#101927'; CREAM='#f3e7cd'; GOLD='#d4a967'; MUTED='#aebcca'; CYAN='#86c3c3'
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font_b='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def ft(s,b=False): return ImageFont.truetype(font_b if b else font,s)
scenes=[
 ('THE FACE THAT\nCHANGED WHEN\nYOU TURNED IT','Peter Thompson • 1980',0,7),
 ('AN UPSIDE-DOWN\nFACE CAN HIDE\nAN ODD DETAIL','The Thatcher illusion',7,14),
 ('TURN IT UPRIGHT.\nTHE ALTERATION\nBECOMES CLEARER.','Eyes and mouth are rotated within the face.',14,21),
 ('THIS IS NOT\nA MAGIC TRICK.','Orientation changes how features are processed.',21,28),
 ('A REAL EFFECT.\nA LIMITED CLAIM.','A schematic is not a controlled lab demonstration.',28,34),
 ('FOLLOW\nTHE EVIDENCE.','Read the sources at Final Vestige • Mind & Perception',34,40)]
def center(draw,lines,y,size,color=CREAM,bold=True,space=13):
    for line in lines.split('\n'):
        draw.text((W/2,y),line,fill=color,font=ft(size,bold),anchor='ma',stroke_width=0)
        y+=size+space

def face(draw,ox,oy,scale,wrong=False,angle=0):
    # Deliberately schematic original artwork: not licensed photography, not empirical stimuli.
    ww=int(178*scale); hh=int(217*scale)
    layer=Image.new('RGBA',(ww+60,hh+60),(0,0,0,0)); d=ImageDraw.Draw(layer)
    box=(30,28,ww+30,hh+28)
    d.ellipse(box,outline=GOLD,width=5)
    for x in [int(ww*.30),int(ww*.70)]:
        if wrong: d.arc((x-16,78,x+16,107),180,360,fill=CYAN,width=5)
        else: d.arc((x-16,78,x+16,107),0,180,fill=CYAN,width=5)
    d.line([(ww/2+30,113),(ww/2+23,141),(ww/2+41,143)], fill=MUTED,width=3)
    if wrong: d.arc((int(ww*.30),157,int(ww*.70),185),180,360,fill=GOLD,width=6)
    else: d.arc((int(ww*.30),157,int(ww*.70),185),0,180,fill=GOLD,width=6)
    img=layer.rotate(angle,expand=True,resample=Image.Resampling.BICUBIC)
    return img

def render_frame(t):
    im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
    d.line((42,60,W-42,60),fill=GOLD,width=2)
    d.text((42,80),'FINAL VESTIGE  /  RESEARCH DESK',fill=MUTED,font=ft(17,True))
    ix=next(i for i,(_,_,a,b) in enumerate(scenes) if a<=t<b)
    title,small,_,_=scenes[ix]
    # large original illustration, never misrepresented as a controlled demonstration
    if ix in (1,2,3,4):
        wrong= ix in (1,2,4)
        ang=180 if ix==1 else 0
        layer=face(d,0,0,1.25,wrong,ang)
        im.paste(layer,(int((W-layer.width)/2),205),layer)
        d=ImageDraw.Draw(im)
    else:
        d.ellipse((171,245,369,443),outline=GOLD,width=4)
        d.arc((205,270,335,400),12,155,fill=CYAN,width=7)
        d.line((270,275,270,406),fill=MUTED,width=2)
    center(d,title,540,36 if ix in(0,5) else 34,space=12)
    center(d,small,765,18,MUTED,False,space=8)
    d.text((W/2,879),'ILLUSTRATION • NOT A CLINICAL TEST',fill=CYAN,font=ft(14),anchor='ma')
    d.line((42,910,W-42,910),fill=GOLD,width=2)
    d.rectangle((42,913,42+int((W-84)*t/SEC),917),fill=CYAN)
    return im

def main():
    output=OUT/'thatcher-original-40s.mp4'
    args=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-vcodec','rawvideo','-s',f'{W}x{H}','-pix_fmt','rgb24','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','28','-pix_fmt','yuv420p','-movflags','+faststart',str(output)]
    p=subprocess.Popen(args,stdin=subprocess.PIPE)
    try:
        for n in range(FPS*SEC): p.stdin.write(render_frame(n/FPS).tobytes())
    finally: p.stdin.close()
    if p.wait()!=0: raise RuntimeError('ffmpeg encoding failed')
    render_frame(14).save(OUT/'thatcher-film-poster.png')
    print(output,output.stat().st_size)
if __name__=='__main__': main()
