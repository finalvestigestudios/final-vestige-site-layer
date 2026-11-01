"""Render FV Mind R40 original silent 40-second evidence primer.
Source-controlled duplicate for reviewer verification; no product-performance claims.
Requires Pillow and ffmpeg; outputs H.264 540x960 12 fps, no music.
"""
from PIL import Image, ImageDraw, ImageFont
import math, subprocess, pathlib, textwrap

W,H,FPS = 540,960,12
ROOT=pathlib.Path(__file__).parent
OUT=ROOT/'zen12-evidence-40s.mp4'
CUES=[
('01  ATTENTION',7,'In the invisible-gorilla experiment, looking and noticing were not the same thing.'),
('02  A BOUNDARY',7,'That is a finding about attention—not a clinical test of meditation audio.'),
('03  WHAT IS SOLD',7,"Zen12's seller describes twelve-minute sessions and four listening styles."),
('04  WHAT IS NOT PROVEN',7,'A short format is useful to some listeners. Hour-long equivalence is not independently proven.'),
('05  TRY FIRST',7,'Try twelve minutes with a free timer before deciding what audio to buy.'),
('06  AN OPEN DECISION',5,'Review the science. Check the terms. Choose freely.')]
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
font_big=ImageFont.truetype(SERIF,41)
font_mid=ImageFont.truetype(FONT,30)
font_sm=ImageFont.truetype(FONT,20)
font_tiny=ImageFont.truetype(FONT,17)
font_num=ImageFont.truetype(SERIF,85)

def centered(d,y,s,font,fill,max_width=480,spacing=10):
    chunks=[];line=''
    for word in s.split():
        candidate=(line+' '+word).strip()
        if d.textbbox((0,0),candidate,font=font)[2] > max_width and line:
            chunks.append(line);line=word
        else:line=candidate
    if line:chunks.append(line)
    for part in chunks:
        x=(W-d.textbbox((0,0),part,font=font)[2])/2
        d.text((x,y),part,font=font,fill=fill)
        y+=d.textbbox((0,0),part,font=font)[3]+spacing
    return y

def make_frame(scene,local_t,total_t):
    bg=(9,10,10);im=Image.new('RGB',(W,H),bg);d=ImageDraw.Draw(im)
    d.rectangle((19,19,521,941),outline=(92,75,50),width=2)
    d.text((50,58),'FINAL VESTIGE  /  MIND',font=font_tiny,fill=(204,164,103))
    d.line((50,101,490,101),fill=(67,61,52),width=2)
    header,duration,message=CUES[scene]
    centered(d,138,header,font_sm,(213,176,117),spacing=2)
    cx,cy=270,381
    for radius,width,color in [(153,3,(122,102,71)),(127,2,(55,56,52)),(96,1,(55,56,52))]:
        d.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),outline=color,width=width)
    for i in range(12):
        th=i*math.pi/6-math.pi/2
        x1=cx+136*math.cos(th);y1=cy+136*math.sin(th)
        x2=cx+149*math.cos(th);y2=cy+149*math.sin(th)
        d.line((int(x1),int(y1),int(x2),int(y2)),fill=(210,174,114),width=3)
    angle=((total_t*0.14)%1)*2*math.pi-math.pi/2
    d.line((cx,cy,cx+112*math.cos(angle),cy+112*math.sin(angle)),fill=(245,237,223),width=8)
    d.ellipse((cx-8,cy-8,cx+8,cy+8),fill=(210,174,114))
    centered(d,564,message,font_mid,(244,239,230),max_width=455,spacing=17)
    centered(d,820,'THE SOURCE BEFORE THE CLAIM',font_tiny,(197,189,178),spacing=3)
    d.rectangle((51,879,489,885),fill=(49,47,43))
    d.rectangle((51,879,int(51+438*min(1,total_t/40)),885),fill=(203,167,109))
    d.text((52,906),'ORIGINAL EDUCATIONAL FILM • NO PRODUCT TEST',font=font_tiny,fill=(175,166,152))
    return im

def main():
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','-','-c:v','libx264','-pix_fmt','yuv420p','-preset','veryfast','-crf','29','-movflags','+faststart','-t','40',str(OUT)]
    pipe=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    elapsed=0;fnum=0
    for scene,(_,length,_) in enumerate(CUES):
        for n in range(int(length*FPS)):
            im=make_frame(scene,n/FPS,fnum/FPS)
            pipe.stdin.write(im.tobytes());fnum+=1
        elapsed+=length
    pipe.stdin.close();code=pipe.wait()
    if code:raise RuntimeError('ffmpeg failed')
    print(str(OUT),fnum,'frames',elapsed,'seconds')
if __name__=='__main__':main()
