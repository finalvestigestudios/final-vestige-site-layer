"""Create an original, silent educational 40-second visual essay.
Not archival footage, scientific experimental replication, or commercial endorsement.
Requires Python Pillow and ffmpeg. Render locally; never auto-upload or publish.
"""
from PIL import Image, ImageDraw, ImageFont
import subprocess, pathlib, math, zipfile, shutil, json

ROOT = pathlib.Path(__file__).resolve().parent
W,H,FPS,DURATION=540,960,12,40
BG=(9,13,12); GOLD=(220,178,117); CREAM=(247,240,226); MUTED=(169,168,156)
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
SANS='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def font(n,serif=False):return ImageFont.truetype(SERIF if serif else SANS,n)
def text(draw,pos,s,size=32,col=CREAM,serif=False):draw.text(pos,s,fill=col,font=font(size,serif))
def wrapped(draw,x,y,s,size=30,maxw=480,col=CREAM,serif=False):
    words=s.split(); line=''; lines=[]
    for word in words:
        candidate=(line+' '+word).strip()
        if draw.textbbox((0,0),candidate,font=font(size,serif))[2]>maxw and line:lines.append(line);line=word
        else:line=candidate
    if line:lines.append(line)
    for line in lines:text(draw,(x,y),line,size,col,serif);y+=size*1.48
    return y

def scene(n,p):
    im=Image.new('RGB',(W,H),BG);dr=ImageDraw.Draw(im)
    dr.line((32,90,508,90),fill=GOLD,width=2)
    text(dr,(32,36),'FINAL VESTIGE  /  THE MIND ARCHIVE',16,GOLD)
    text(dr,(32,885),'ORIGINAL SCIENCE/HISTORY ILLUSTRATION',13,GOLD)
    dr.line((32,868,508,868),fill=(84,75,58),width=2)
    dr.rectangle((32,823,32+int(476*(n+p)/6),830),fill=GOLD)
    if n==0:
        text(dr,(32,135),'THE GLASS',55,CREAM,True);text(dr,(32,210),"THAT WASN'T",46,CREAM,True);text(dr,(32,279),'THERE',62,GOLD,True)
        dr.line((90,700,200,435),fill=MUTED,width=7);dr.line((450,700,340,435),fill=MUTED,width=7)
        dr.line((270,699,270,452),fill=(70,75,71),width=5)
        text(dr,(183,530),'?',145,GOLD,True)
        wrapped(dr, (32),748,'The accident film contained no broken glass.',23,470)
    elif n==1:
        text(dr,(32,137),'ONE CHANGED',46,CREAM,True);text(dr,(32,204),'WORD',56,GOLD,True)
        dr.rounded_rectangle((42,354,498,463),radius=14,outline=MUTED,width=3)
        text(dr,(193,369),'HIT',67,CREAM,True)
        dr.line((270,482,270,556),fill=GOLD,width=5);dr.polygon([(258,548),(282,548),(270,570)],fill=GOLD)
        dr.rounded_rectangle((42,578,498,687),radius=14,outline=GOLD,width=3)
        text(dr,(104,595),'SMASHED',52,GOLD,True)
        wrapped(dr,32,742,'The question changed. The footage did not.',24,476)
    elif n==2:
        text(dr,(32,135),'A QUESTION',50,CREAM,True);text(dr,(32,202),'AFTER THE',46,GOLD,True);text(dr,(32,266),'EVENT',55,CREAM,True)
        dr.rounded_rectangle((45,420,497,682),radius=18,fill=(20,26,24),outline=(100,90,72),width=3)
        text(dr,(70,456),'DID YOU SEE',32,CREAM);text(dr,(70,509),'BROKEN GLASS?',29,GOLD)
        dr.rounded_rectangle((80,591,122,633),radius=3,outline=CREAM,width=3)
        dr.rounded_rectangle((246,591,288,633),radius=3,outline=CREAM,width=3)
        text(dr,(134,593),'YES',24,MUTED);text(dr,(300,593),'NO',24,MUTED)
        wrapped(dr,32,740,'Some later reported seeing glass.',25,468)
    elif n==3:
        text(dr,(32,135),'INFORMATION',47,CREAM,True);text(dr,(32,205),'HAS A ROUTE',47,GOLD,True)
        boxes=[('EVENT',370),('QUESTION',500),('REPORT',630)]
        for s,y in boxes:
            dr.rounded_rectangle((75,y,463,y+73),radius=6,fill=(22,27,24),outline=MUTED,width=3)
            text(dr,(127,y+14),s,30,CREAM)
            if y<630:dr.line((270,y+74,270,y+115),fill=GOLD,width=4);dr.polygon([(261,y+110),(279,y+110),(270,y+124)],fill=GOLD)
        wrapped(dr,32,763,'Later information can affect recall.',23,470)
    elif n==4:
        text(dr,(32,137),'THREE',56,CREAM,True);text(dr,(32,210),'DIFFERENT',48,GOLD,True);text(dr,(32,278),'QUESTIONS',49,CREAM,True)
        for i,s in enumerate(['WHAT WAS SEEN?','WHAT WAS SAID?','WHAT WAS INFERRED?']):
            y=423+i*104
            dr.rounded_rectangle((39,y,502,y+76),radius=7,outline=GOLD if i==1 else MUTED,width=3)
            text(dr,(60,y+19),s,24,CREAM)
        wrapped(dr,32,765,'Report and mechanism are not identical.',22,470)
    else:
        text(dr,(32,139),'TRACE',62,GOLD,True);text(dr,(32,225),'THE ADDED',48,CREAM,True);text(dr,(32,300),'DETAIL',62,CREAM,True)
        dr.rounded_rectangle((75,450,466,690),radius=6,outline=GOLD,width=3)
        for idx,s in enumerate(['1  ORIGINAL ACCOUNT','2  LATER QUESTION','3  FINAL REPORT']):
            text(dr,(102,484+idx*64),s,22,GOLD if idx==1 else CREAM)
            dr.line((103,524+idx*64,437,524+idx*64),fill=(73,67,59),width=2)
        wrapped(dr,32,748,'Preserve the first account.',27,476)
    return im

def main():
    dest=ROOT/'the-glass-that-wasnt-there-40s.mp4'
    poster=scene(0,0);poster.save(ROOT/'poster.png')
    contact=Image.new('RGB',(1080,1440),BG)
    for i in range(6):contact.paste(scene(i,.5).resize((360,640)),((i%3)*360,(i//3)*720))
    contact.save(ROOT/'contact-sheet.png')
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','pipe:0','-c:v','libx264','-preset','ultrafast','-crf','27','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)]
    pipe=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    assert pipe.stdin
    for i in range(FPS*DURATION):
        secs=i/FPS
        bounds=[0,6,13,20,27,34,40]
        n=next((j for j in range(6) if bounds[j]<=secs<bounds[j+1]),5)
        p=(secs-bounds[n])/(bounds[n+1]-bounds[n])
        im=scene(n,p)
        # Soft scene fade from background, preserving source text legibility.
        if p<.08:im=Image.blend(Image.new('RGB',(W,H),BG),im,p/.08)
        pipe.stdin.write(im.tobytes())
    pipe.stdin.close();rc=pipe.wait()
    if rc:raise RuntimeError('ffmpeg failed '+str(rc))
    print('RENDERED',dest,'bytes',dest.stat().st_size)
if __name__=='__main__':main()
