#!/usr/bin/env python3
"""Original silent evidence explainer. Requires Pillow + ffmpeg; no web/network/assets.
480 frames @ 12 fps, 540x960 H.264, six source-grounded scenes. Does not
simulate a dichotic-listening trial or claim named-product effectiveness.
"""
from PIL import Image, ImageDraw, ImageFont
from math import sin, pi
from pathlib import Path
import subprocess

SIZE=(540,960); FPS=12; TOTAL=480
OUT=Path(__file__).resolve().parent
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
SERIF='/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf'
WHITE='#F4EFE6'; GOLD='#D7B782'; SILVER='#BDCAC4'; DARK='#0A0D0D'
SCENES=[
 (0,78,('WHAT GETS','THROUGH?'),'The ignored voice does not stop speaking.'),
 (78,156,('TWO VOICES.','ONE TASK.'),'Follow one message. Ignore the other.'),
 (156,234,('A NAME IN','THE OTHER EAR'),'Some listeners notice it.'),
 (234,312,('NOT EVERYONE','HEARD IT.'),'34.6% in one study of 34 undergraduates.'),
 (312,396,('ATTENTION','HAS A COST.'),'Noticing can interrupt the chosen task.'),
 (396,480,('A FORMAT','IS NOT PROOF.'),'Twelve-minute audio does not prove an hour of benefits.'),
]

def font(path,size): return ImageFont.truetype(path,size)
H1=font(SERIF,59); LABEL=font(FONT,16); SUB=font(FONT,20); FOOT=font(FONT,17)

def centered(draw, y, text, ft, fill, max_width=470):
    box=draw.textbbox((0,0),text,font=ft)
    x=(SIZE[0]-(box[2]-box[0]))//2
    if box[2]-box[0]>max_width:
        scale=max_width/(box[2]-box[0])
        ft=font(SERIF if ft is H1 else FONT,max(11,int(ft.size*scale)))
        box=draw.textbbox((0,0),text,font=ft)
        x=(SIZE[0]-(box[2]-box[0]))//2
    draw.text((x,y),text,font=ft,fill=fill)

def scene_frame(i):
    scene=next(s for s in SCENES if s[0]<=i<s[1]); start,end,titles,sub=scene
    time=i/FPS
    im=Image.new('RGB',SIZE,DARK); d=ImageDraw.Draw(im)
    d.rectangle((31,31,509,929),outline='#42392E',width=2)
    d.line((50,109,490,109),fill='#675239',width=2)
    d.text((50,60),'F I N A L  V E S T I G E  /  M I N D',font=LABEL,fill=GOLD)
    d.text((50,869),'INDEPENDENT EVIDENCE  •  40 SECONDS',font=LABEL,fill=GOLD)
    d.line((50,847,490,847),fill='#675239',width=2)
    centered(d,160,titles[0],H1,WHITE)
    centered(d,232,titles[1],H1,GOLD)
    # Two sound channels: one selected, one ordinarily ignored.
    for channel,y,color,phase in [(0,468,SILVER,0),(1,590,GOLD,1.9)]:
        points=[]
        for x in range(65,475,3):
            amp=(20+12*sin(x*.016+time*.6+phase))
            wave=sin(x*.046+time*2.6+phase)*amp
            points.append((x,int(y+wave)))
        d.line(points,fill=color,width=5,joint='curve')
        d.ellipse((55,y-7,69,y+7),fill=color)
        d.ellipse((468,y-7,482,y+7),fill=color)
    d.rounded_rectangle((165,500,375,555),radius=25,fill='#1F302C',outline='#BF9C67',width=2)
    centered(d,511,'NAME' if i>=156 else 'LISTEN',font(FONT,24),WHITE)
    # A concise evidence caution, original art and no imitation of real trials.
    words=sub.split(); lines=[]; cur=''
    for word in words:
        candidate=(cur+' '+word).strip()
        if d.textlength(candidate,font=SUB)>455 and cur:
            lines.append(cur);cur=word
        else:cur=candidate
    if cur:lines.append(cur)
    for j,line in enumerate(lines):centered(d,699+j*31,line,SUB,WHITE)
    d.text((50,806),'SCHEMATIC • NOT A LISTENING TEST',font=FOOT,fill='#A5A49D')
    # Calm visual fade, optional; default film is silent.
    envelope=min(1.0,(i-start)/5,(end-1-i)/5)
    if envelope<1:
        overlay=Image.new('RGB',SIZE,DARK)
        im=Image.blend(overlay,im,max(.18,envelope))
    return im

def main():
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s','540x960','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','26','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'the-name-in-the-other-ear-40s.mp4')]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for i in range(TOTAL):p.stdin.write(scene_frame(i).tobytes())
    finally:p.stdin.close()
    if p.wait()!=0:raise RuntimeError('ffmpeg failed')
    scene_frame(172).save(OUT/'the-name-in-the-other-ear-poster.png')
    print('Rendered',OUT/'the-name-in-the-other-ear-40s.mp4')
if __name__=='__main__':main()
