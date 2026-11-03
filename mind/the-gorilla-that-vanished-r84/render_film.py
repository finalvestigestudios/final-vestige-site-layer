"""Original silent 40-second Mind & Perception film for UNPUBLISHED review only.
Build: python render_film.py  (requires Pillow + ffmpeg). No merchant claims."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math, subprocess, hashlib, zipfile

HERE=Path(__file__).resolve().parent
W,H,FPS,SECONDS=540,960,12,40
GOLD=(213,181,120); INK=(9,12,12); WHITE=(244,239,230); GRAY=(185,180,166)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
TITLE=ImageFont.truetype(BOLD,38); LARGE=ImageFont.truetype(BOLD,56)
MED=ImageFont.truetype(FONT,25); SMALL=ImageFont.truetype(FONT,20)
SCENES=[
 (0,6,'COUNT THE','GOLD PASSES','Six shapes. One assignment.'),
 (6,13,'THE TASK','SETS A FILTER','A specific count shapes attention.'),
 (13,20,'THE VISITOR','IS VISIBLE','An unexpected figure crosses the frame.'),
 (20,27,'SOME NEVER','REPORT IT','A report is not a complete inventory.'),
 (27,34,'A SECOND','SURPRISE','Knowing one trick does not reveal all.'),
 (34,40,'READ THE','EVIDENCE','Simons & Chabris 1999 · Simons 2010')]

def centered(draw,text,font,y,fill):
    bbox=draw.textbbox((0,0),text,font=font)
    draw.text(((W-(bbox[2]-bbox[0]))/2,y),text,font=font,fill=fill,stroke_width=0)

def frame(t):
    s=next(i for i,item in enumerate(SCENES) if item[0]<=t<item[1]); start,end,h1,h2,sub=SCENES[s]
    u=(t-start)/(end-start)
    img=Image.new('RGB',(W,H),INK); d=ImageDraw.Draw(img)
    for x in range(0,W,36):
        d.line((x,0,x,H),fill=(17,22,21),width=1)
    for y in range(0,H,36):
        d.line((0,y,W,y),fill=(17,22,21),width=1)
    d.rectangle((24,27,W-24,H-27),outline=(72,63,49),width=2)
    centered(d,'FINAL VESTIGE / MIND ARCHIVE',SMALL,65,GOLD)
    centered(d,f'{s+1:02d}  /  06',MED,139,GRAY)
    # Original schematic illustration, not original gorilla video or recorded experiment.
    if s in (0,1):
        for j in range(6):
            xx=int(95+350*(.5+.45*math.sin(2*math.pi*(u*1.7+j/6))))
            yy=int(290+165*math.sin(j*2.4+u*2.3))
            color=GOLD if j%2==0 else (112,128,120)
            d.ellipse((xx-30,yy-30,xx+30,yy+30),fill=color)
            d.ellipse((xx-34,yy-34,xx+34,yy+34),outline=(220,210,186),width=2)
        d.line((75,530,465,530),fill=(86,79,65),width=3)
    elif s==2:
        for j in range(3):
            d.ellipse((95+j*145,350,145+j*145,400),fill=GOLD)
        x=int(-140+730*u)
        d.ellipse((x,306,x+104,412),fill=(76,96,91))
        d.rounded_rectangle((x-20,395,x+124,570),radius=32,fill=(76,96,91))
        d.rectangle((x+4,555,x+32,633),fill=(76,96,91)); d.rectangle((x+70,555,x+98,633),fill=(76,96,91))
        d.rectangle((100,664,440,670),fill=(118,106,87))
    elif s==3:
        d.ellipse((152,298,388,534),outline=GOLD,width=8)
        centered(d,'?',LARGE,369,WHITE)
        d.arc((114,261,425,573),215,326,fill=(105,121,111),width=8)
    elif s==4:
        d.rectangle((75,290,465,560),fill=(40,56,52) if u<.5 else (87,65,52))
        d.rectangle((75,290,465,560),outline=GOLD,width=4)
        for j in range(3):
            xx=130+j*120
            d.ellipse((xx-20,390,xx+20,430),fill=GOLD if j==1 else (122,143,132))
    else:
        d.rounded_rectangle((74,295,466,560),radius=8,outline=GOLD,width=4)
        centered(d,'1999',LARGE,324,GOLD)
        centered(d,'2010',LARGE,450,WHITE)
    d.rectangle((48,716,492,721),fill=(99,89,72))
    centered(d,h1,TITLE,753,WHITE)
    centered(d,h2,TITLE,802,GOLD)
    # Fit short subtitle to width; all scene sublines inspected in contact sheet.
    centered(d,sub,SMALL,866,GRAY)
    return img

def main():
    output=HERE/'the-visitor-was-visible-40s.mp4'
    args=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','-','-an','-c:v','libx264','-pix_fmt','yuv420p','-crf','28','-movflags','+faststart',str(output)]
    proc=subprocess.Popen(args,stdin=subprocess.PIPE)
    thumbs=[]
    for idx in range(FPS*SECONDS):
        tm=idx/FPS
        img=frame(tm)
        if idx in [0,84,192,276,360,444]:
            thumbs.append(img.copy())
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    assert proc.wait()==0,'ffmpeg failed'
    frame(0).save(HERE/'poster.png',optimize=True)
    sheet=Image.new('RGB',(1080,960),INK)
    for i,im in enumerate(thumbs):
        sheet.paste(im.resize((270,480),Image.Resampling.LANCZOS),(i%4*270,i//4*480))
    sheet.save(HERE/'contact-sheet.png',optimize=True)
    vtt='WEBVTT\n\n'
    for start,end,h1,h2,sub in SCENES:
        def ts(s):return f'00:00:{s:02d}.000'
        vtt+=f'{ts(start)} --> {ts(end)}\n{h1} {h2}. {sub}\n\n'
    (HERE/'captions.vtt').write_text(vtt,encoding='utf8')
    (HERE/'transcript.txt').write_text('\n'.join(f'{a}–{b}s: {c} {d}. {e}' for a,b,c,d,e in SCENES)+ '\nSilence throughout. Original schematic visualization, not laboratory footage.\n',encoding='utf8')
    print('mp4_sha256',hashlib.sha256(output.read_bytes()).hexdigest())
    print('mp4_bytes',output.stat().st_size)
if __name__=='__main__':main()
