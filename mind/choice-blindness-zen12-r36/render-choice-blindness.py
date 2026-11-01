#!/usr/bin/env python3
"""Original 40-second silent Choice Blindness explainer for Final Vestige.

Pillow + ffmpeg; reproducible offline. Original geometric portraits, no stock.
The text intentionally does not claim that Zen12 treats, alters, or controls minds.
"""
from pathlib import Path
import math, os, subprocess, hashlib, tempfile
from PIL import Image, ImageDraw, ImageFont

W,H,FPS,SECS=540,960,12,40
OUT=Path(__file__).parent
GOLD=(198,162,109); GOLD_L=(231,201,155)
BG=(11,14,14); PAPER=(20,25,24); WHITE=(241,235,222)
SANS='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
FONT={s:ImageFont.truetype(BOLD if s>=26 else SANS,s) for s in [13,15,17,20,21,24,26,30,35,39,42]}
SERIF_F={s:ImageFont.truetype(SERIF,s) for s in [33,40,50]}
CAPTIONS=[
(0,6.5,'You choose a photograph. A moment later, someone hands it back.'),
(6.5,13.5,'But researchers sometimes exchanged it for the picture you rejected.'),
(13.5,20.5,'Some people did not notice. They still explained why they chose it.'),
(20.5,27.5,'The experiment is called choice blindness. It is not proof of mind control.'),
(27.5,34.5,'A persuasive explanation is different from an independent record.'),
(34.5,40.0,'Keep the evidence. Then examine the story. Final Vestige.'),
]
HEADS=[('YOU CHOOSE','ONE FACE'),('THE RETURN','WAS SWITCHED'),('THE REASON','STILL ARRIVES'),('CHOICE','BLINDNESS'),('AN ACCOUNT','IS NOT A LOG'),('KEEP','THE RECORD')]
SUBS=[('Two portraits.','One choice.'),('A quiet exchange','changes the outcome.'),('A reason can be','convincing, but wrong.'),('An experiment,','not mind control.'),('Compare the original','with the explanation.'),('Science before','the story.')]

def lines(draw,text,font,max_width):
    words=text.split(); out=[]; cur=''
    for word in words:
        trial=(cur+' '+word).strip()
        if cur and draw.textbbox((0,0),trial,font=font)[2]>max_width:
            out.append(cur);cur=word
        else:cur=trial
    if cur:out.append(cur)
    return out

def center_lines(draw,txt,y,font,fill,max_w=440,space=11):
    l=lines(draw,txt,font,max_w)
    step=font.size+space
    for line in l:
        bbox=draw.textbbox((0,0),line,font=font)
        draw.text(((W-(bbox[2]-bbox[0]))//2,y),line,font=font,fill=fill)
        y+=step
    return y

def portrait(draw,x,y,tone,reverse=False):
    # Deliberately abstract portraits: these are not real participant photographs.
    draw.rounded_rectangle((x,y,x+184,y+238),radius=9,fill=(25,43,42) if not reverse else (48,36,44),outline=GOLD,width=3)
    draw.ellipse((x+48,y+35,x+136,y+122),fill=tone)
    draw.rounded_rectangle((x+22,y+126,x+162,y+214),radius=35,fill=tone)
    if reverse:
        draw.line((x+62,y+76,x+82,y+79),fill=(55,42,43),width=4)
        draw.line((x+108,y+80,x+128,y+73),fill=(55,42,43),width=4)
        draw.arc((x+73,y+84,x+112,y+111),0,180,fill=(55,42,43),width=3)
    else:
        draw.ellipse((x+72,y+74,x+78,y+80),fill=(55,42,43))
        draw.ellipse((x+108,y+74,x+114,y+80),fill=(55,42,43))
        draw.arc((x+79,y+88,x+106,y+112),0,180,fill=(55,42,43),width=3)

def frame(t):
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
    d.rounded_rectangle((22,18,518,942),radius=10,fill=PAPER,outline=(102,85,62),width=2)
    d.text((48,54),'FINAL VESTIGE',fill=GOLD_L,font=FONT[20])
    d.text((48,92),'MIND / PERCEPTION',fill=(163,151,132),font=FONT[13])
    i=next((k for k,(a,b,_) in enumerate(CAPTIONS) if a<=t<b),5)
    h0,h1=HEADS[i]
    d.text((48,155),h0,fill=WHITE,font=SERIF_F[50]);d.text((48,221),h1,fill=WHITE,font=SERIF_F[40])
    shift=math.sin(t*2.2)*3
    if i in (0,1,2):
        portrait(d,63,331+shift,(173,167,147))
        portrait(d,293,331-shift,(154,141,157),True)
        d.text((128,587),'A',font=FONT[24],fill=GOLD_L)
        d.text((360,587),'B',font=FONT[24],fill=GOLD_L)
        if i==0:
            d.rounded_rectangle((55,632,245,677),radius=6,outline=GOLD,width=3)
            d.text((97,643),'CHOICE A',font=FONT[20],fill=WHITE)
        elif i==1:
            d.line((237,448,298,448),fill=GOLD,width=6)
            d.polygon([(286,436),(304,448),(286,460)],fill=GOLD)
            d.text((125,638),'RETURN B',font=FONT[24],fill=GOLD_L)
        else:
            d.text((70,632),'“I CHOSE B...”',font=FONT[21],fill=GOLD_L)
    elif i==3:
        portrait(d,177,351,(173,167,147))
        d.text((72,632),'JOHANSSON ET AL. / 2005',font=FONT[17],fill=GOLD_L)
        d.text((72,664),'DOI 10.1126/science.1111709',font=FONT[15],fill=(216,204,184))
    elif i==4:
        d.rectangle((52,361,248,642),outline=GOLD,width=3)
        d.rectangle((289,361,485,642),outline=GOLD,width=3)
        d.text((69,389),'RECORD',font=FONT[24],fill=GOLD_L)
        d.text((309,389),'STORY',font=FONT[24],fill=GOLD_L)
        d.text((70,470),'PICKED',font=FONT[21],fill=WHITE)
        d.text((70,510),'CARD A',font=FONT[21],fill=WHITE)
        d.text((308,470),'DEFENDS',font=FONT[21],fill=WHITE)
        d.text((308,510),'CARD B',font=FONT[21],fill=WHITE)
    else:
        d.ellipse((152,359,390,597),outline=GOLD,width=5)
        d.text((216,429),'FV',font=SERIF_F[50],fill=WHITE)
        d.text((105,638),'THE EVIDENCE ENDURES.',font=FONT[21],fill=GOLD_L)
    y=710
    for s in SUBS[i]:
        d.text((48,y),s,font=FONT[24],fill=(212,201,181));y+=37
    d.rounded_rectangle((31,805,509,904),radius=6,fill=(6,9,9),outline=(85,76,62),width=1)
    center_lines(d,CAPTIONS[i][2],819,FONT[20],WHITE,max_w=448,space=6)
    d.line((31,920,509,920),fill=(60,57,48),width=3)
    d.line((31,920,31+int(478*t/40),920),fill=GOLD,width=3)
    return im

def main():
    output=OUT/'choice-blindness-40s.mp4'
    ffmpeg=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-vcodec','libx264','-preset','veryfast','-crf','29','-pix_fmt','yuv420p','-movflags','+faststart',str(output)]
    p=subprocess.Popen(ffmpeg,stdin=subprocess.PIPE)
    for n in range(FPS*SECS):p.stdin.write(frame(n/FPS).tobytes())
    p.stdin.close()
    rc=p.wait()
    if rc:raise SystemExit(f'ffmpeg failed {rc}')
    frame(4).save(OUT/'choice-blindness-poster.png')
    print('video',output,output.stat().st_size,hashlib.sha256(output.read_bytes()).hexdigest())
    print('poster',OUT/'choice-blindness-poster.png')

if __name__=='__main__':main()
