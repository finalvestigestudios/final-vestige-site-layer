"""Original Final Vestige 40s choice-blindness educational short; no external media.
Requires Pillow and ffmpeg. Does not claim to reenact an experimental session.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import subprocess, math, shutil, hashlib
W,H,FPS,DURATION=540,960,12,40
OUT=Path(__file__).resolve().parent
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONT_B='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
COLOR_BG=(12,15,15); BRONZE=(212,174,112); WHITE=(244,236,220); MUTED=(174,170,155); PANEL=(35,42,40)
scenes=[(0,6,['YOU CHOSE','CARD A'], 'THE DECISION'),(6,12,['THE OUTCOME','WAS SWITCHED'], '2005 / RESEARCH DESIGN'),(12,19,['NOW YOU','SEE CARD B'], 'THE PRESENTED RESULT'),(19,26,['SOME PEOPLE','MISSED IT'], 'A REPORTED EXPLANATION'),(26,33,['A REASON IS','NOT A RECORD'], 'EXPERIENCE ≠ CAUSE'),(33,40,['CHECK THE','ORIGINAL CHOICE'], 'DOI: 10.1126/science.1111709')]

def font(size,bold=False):return ImageFont.truetype(FONT_B if bold else FONT,size)

def center(draw,t,y,size,color,bold=True):
    f=font(size,bold); box=draw.textbbox((0,0),t,font=f); draw.text(((W-(box[2]-box[0]))//2,y),t,font=f,fill=color)

def card(draw,x,y,label,highlight=False):
    draw.rounded_rectangle((x,y,x+186,y+258),radius=9,outline=BRONZE if highlight else (115,103,83),width=5,fill=PANEL)
    draw.ellipse((x+50,y+49,x+136,y+135),outline=MUTED,width=4)
    draw.arc((x+32,y+91,x+154,y+209),start=190,end=350,fill=MUTED,width=5)
    draw.text((x+82,y+209),label,font=font(32),fill=BRONZE)

def frame(i):
    t=i/FPS; si=next(j for j,(s,e,_,__) in enumerate(scenes) if s<=t<e)
    s,e,lines,kicker=scenes[si]
    im=Image.new('RGB',(W,H),COLOR_BG);d=ImageDraw.Draw(im)
    d.rounded_rectangle((22,22,W-22,H-22),radius=11,outline=(96,83,61),width=2)
    center(d,'FINAL VESTIGE / MIND',53,18,BRONZE)
    d.line((65,102,W-65,102),fill=(83,75,61),width=2)
    center(d,kicker,146,19,MUTED)
    for j,line in enumerate(lines):center(d,line,200+j*69,44,WHITE)
    pulse=math.sin(2*math.pi*(t-s)/(e-s))*4
    if si in (0,1,2):
        card(d,64,426,'A',si==0)
        card(d,290,426,'B',si==2)
        if si==1:
            d.line((250,523,283,523),fill=BRONZE,width=6);d.polygon([(277,509),(301,523),(277,537)],fill=BRONZE)
        if si==0:d.rounded_rectangle((65,717,476,779),radius=12,outline=BRONZE,width=3);center(d,'RECORDED CHOICE: A',729,22,BRONZE)
        elif si==2:center(d,'PRESENTED RESULT: B',750,21,BRONZE)
        else:center(d,'A  ≠  B',749,34,BRONZE)
    elif si==3:
        d.rounded_rectangle((68,470,472,692),radius=20,outline=BRONZE,width=4,fill=PANEL)
        center(d,'“Why did you pick B?”',509,25,WHITE)
        center(d,'A sincere explanation',587,22,BRONZE)
        center(d,'is not a choice log.',625,22,BRONZE)
    elif si==4:
        for j,title in enumerate(('OBSERVED','PRESENTED','EXPLAINED')):
            y=445+j*105;d.rounded_rectangle((65,y,475,y+77),radius=7,outline=BRONZE,width=3);center(d,title,y+20,26,WHITE)
    else:
        center(d,'READ THE ORIGINAL STUDY',478,23,BRONZE)
        center(d,'NOT PRODUCT EVIDENCE',545,24,WHITE)
        d.line((76,642,465,642),fill=BRONZE,width=2)
    d.text((52,859),'EDUCATIONAL ILLUSTRATION · NOT LAB FOOTAGE',font=font(15),fill=MUTED)
    d.text((52,890),f'{si+1:02d}/06',font=font(18),fill=BRONZE)
    # slow progress bar, no flashing
    d.rectangle((52,926,488,931),fill=(47,54,50));d.rectangle((52,926,52+int(436*i/(FPS*DURATION)),931),fill=BRONZE)
    return im

def main():
    raw=OUT/'frames.rgb';f=open(raw,'wb');
    try:
        for i in range(FPS*DURATION):f.write(frame(i).tobytes())
    finally:f.close()
    mp4=OUT/'the-reason-after-the-choice-40s.mp4'
    cmd=['ffmpeg','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i',str(raw),'-an','-c:v','libx264','-pix_fmt','yuv420p','-crf','24','-preset','veryfast','-movflags','+faststart',str(mp4)]
    subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    raw.unlink()
    frame(0).save(OUT/'poster.png')
    print('MP4',mp4,mp4.stat().st_size,hashlib.sha256(mp4.read_bytes()).hexdigest())
if __name__=='__main__':main()
