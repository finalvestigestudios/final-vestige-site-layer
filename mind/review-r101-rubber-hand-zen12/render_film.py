"""Final Vestige R101 original 40-second silent evidence-first Zen12 explainer.

Standalone reproducible Pillow/FFmpeg renderer. No third-party art or vendor creatives.
Output: evidence-before-audio-r101-40s.mp4, poster.png, contact-sheet.png
This illustrates the guide's epistemic distinction; NOT an efficacy demonstration.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import os
import subprocess

HERE=os.path.dirname(os.path.abspath(__file__))
W,H,FPS=540,960,12
DUR=[6,6,7,7,7,7]
assert sum(DUR)==40
FACE='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
DARK=(12,30,38); MINT=(182,229,205); WHITE=(245,244,231); MUTE=(169,190,185)
scenes=[
 ('TIME IS REAL','TWELVE MINUTES','can fit into a full day.', '12:00'),
 ('CLAIM VS. FORMAT','A SHORT SESSION','is not a measured hour.', '12 ≠ 60'),
 ('WHAT THE SELLER DESCRIBES','LEVELS & STYLES','Different audio formats.','12 / 4'),
 ('WHAT THE EVIDENCE SAYS','STUDIES OF SOUNDS','are not tests of this course.', '≠ PROOF'),
 ('TRY THIS FOR FREE','SILENCE  ·  MUSIC','or a simple spoken guide.', '3 DAYS'),
 ('DECIDE WITHOUT PRESSURE','READ THE SOURCES','Choose what helps you start.', 'EVIDENCE'),
]

def font(path,size):return ImageFont.truetype(path,size)

def centered(d,txt,y,ft,fill,maxw=480):
    x0,y0,x1,y1=d.textbbox((0,0),txt,font=ft)
    x=(W-(x1-x0))/2
    if x<12: raise ValueError('Text overflow: '+txt)
    d.text((x,y),txt,font=ft,fill=fill)

def render(scene,t,full=False):
    im=Image.new('RGB',(W,H),DARK)
    d=ImageDraw.Draw(im)
    # Calm moving rings and thin architectural rules; no flashes or fast motion.
    for i in range(5):
        y=170+i*100
        a=45+6*math.sin(t*.45+i*.8)
        col=(20+int(a/4),65+int(a/3),67+int(a/4))
        d.arc((-150,y-60,670,y+290),0,180,fill=col,width=2)
    d.line((36,80,W-36,80),fill=MINT,width=2)
    d.text((38,38),'FINAL VESTIGE  /  MIND & PERCEPTION',font=font(BOLD,14),fill=MINT)
    # measured segment progress rather than fake merchant countdown
    d.rectangle((38,880,W-38,883),fill=(37,65,68))
    d.rectangle((38,880,38+int((W-76)*min(1,t/40)),883),fill=MINT)
    d.text((38,895),'ORIGINAL EXPLAINER  ·  NOT AN AD OR PRODUCT TRIAL',font=font(FACE,11),fill=MUTE)
    kicker,heading,sub,big=scenes[scene]
    centered(d,kicker,210,font(BOLD,17),MINT)
    centered(d,big,300,font(SERIF,61 if len(big)<11 else 47),WHITE)
    d.line((120,410,W-120,410),fill=MINT,width=3)
    centered(d,heading,465,font(BOLD,27 if len(heading)<21 else 23),WHITE)
    centered(d,sub,530,font(FACE,20 if len(sub)<30 else 18),MUTE)
    d.text((38,815),f'{scene+1:02d} / 06',font=font(BOLD,18),fill=MINT)
    return im

def main():
    out=os.path.join(HERE,'evidence-before-audio-r101-40s.mp4')
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}',
         '-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','28',
         '-pix_fmt','yuv420p','-movflags','+faststart',out]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    frames=[]
    n=0
    for idx,seconds in enumerate(DUR):
        for _ in range(seconds*FPS):
            t=n/FPS
            img=render(idx,t)
            if _ == (seconds*FPS)//2: frames.append(img.copy())
            proc.stdin.write(img.tobytes())
            n+=1
    proc.stdin.close()
    err=proc.stderr.read(); rc=proc.wait()
    if rc:raise RuntimeError(err.decode(errors='replace'))
    render(0,1).save(os.path.join(HERE,'poster.png'))
    sheet=Image.new('RGB',(W*3,H*2),(255,255,255))
    for n,image in enumerate(frames):sheet.paste(image,(n%3*W,n//3*H))
    sheet.resize((810,960),Image.Resampling.LANCZOS).save(os.path.join(HERE,'contact-sheet.png'))
    print(out)

if __name__=='__main__':main()
