#!/usr/bin/env python3
"""Original silent 40-second Final Vestige Zen12 science-integrity pilot.

No paid assets, external downloads, trackers or text from merchant ads.
Uses Pillow, ffmpeg and locally installed fonts. Output is a preview artifact;
it must not be deployed or embedded until release approval.
"""
import math, subprocess, sys, shutil, argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SCENES = [
 (0,8,  ["THE SECOND HAND", "HESITATES."], ["Your sense of time can stretch", "when you shift your gaze."]),
 (8,16, ["EXPERIENCE IS NOT", "A STOPWATCH."], ["Chronostasis is a measured", "perceptual illusion."]),
 (16,25,["ZEN12 SELLS", "12-MINUTE AUDIOS."], ["The vendor describes three tiers", "and four listening styles."]),
 (25,34,["TWELVE IS", "NOT SIXTY."], ["An hour's meditation benefits are", "not independently proven for Zen12."]),
 (34,40,["TRY TWELVE", "FOR FREE FIRST."], ["Read the independent evidence guide.", "Decide for yourself."])
]

def make(out, width=540, height=960, fps=12):
    assert 0 < width <= 1080 and height * 9 == width * 16, "portrait 9:16 only"
    assert fps in (10,12,15,24)
    if not shutil.which('ffmpeg'):
        raise RuntimeError('ffmpeg required')
    f_serif = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
    f_sans  = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    f_bold  = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    sf = ImageFont.truetype(f_serif, round(width * .076))
    bf = ImageFont.truetype(f_bold, round(width * .023))
    pf = ImageFont.truetype(f_sans, round(width * .030))
    sf_small = ImageFont.truetype(f_serif, round(width * .066))
    bg = Image.new('RGB', (width,height), '#0B0D0D')
    gd = ImageDraw.Draw(bg)
    for y in range(height):
        t = y / height
        r=int(11+14*math.sin(math.pi*t)**2)
        g=int(13+12*math.sin(math.pi*t)**2)
        b=int(13+7*math.sin(math.pi*t)**2)
        gd.line((0,y,width,y), fill=(r,g,b))
    def middle(draw,y,s,font,color,spacing=1):
        bb=draw.textbbox((0,0),s,font=font,stroke_width=0)
        draw.text(((width-(bb[2]-bb[0]))/2,y),s,font=font,fill=color)
    cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{width}x{height}','-framerate',str(fps),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','26','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
    p=subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for fr in range(40*fps):
            sec=fr/fps
            idx=next(i for i,(a,b,_,__) in enumerate(SCENES) if a<=sec<b)
            start,end,title,sub=SCENES[idx]
            im=bg.copy()
            d=ImageDraw.Draw(im)
            # Slowly moving original geometric timepiece; not a diagnostic demo.
            cx,cy=width//2,int(height*.325)
            R=int(width*.275)
            d.arc((cx-R,cy-R,cx+R,cy+R),0,360,fill='#735F42',width=2)
            d.arc((cx-R+10,cy-R+10,cx+R-10,cy+R-10),-90,-90+360*((sec%12)/12),fill='#C7A66C',width=4)
            theta=2*math.pi*((sec%12)/12)-math.pi/2
            x=int(cx+(R-10)*math.cos(theta));y=int(cy+(R-10)*math.sin(theta))
            d.ellipse((x-5,y-5,x+5,y+5),fill='#E4CB9C')
            d.line((cx,cy,cx+int(R*.55*math.cos(theta)),cy+int(R*.55*math.sin(theta))),fill='#E4CB9C',width=3)
            d.ellipse((cx-5,cy-5,cx+5,cy+5),fill='#E4CB9C')
            middle(d,int(height*.06),'FINAL VESTIGE  /  MIND & PERCEPTION',bf,'#C7A66C')
            d.line((width*.11,height*.12,width*.89,height*.12),fill='#695A47',width=2)
            d.text((width*.11,height*.56),f'0{idx+1} / 05  ·  EVIDENCE FIRST',font=bf,fill='#C7A66C')
            title_font=sf if all(len(k)<21 for k in title) else sf_small
            for k,line in enumerate(title):
                d.text((int(width*.11),int(height*.625+k*height*.07)),line,font=title_font,fill='#F4EFE6')
            for k,line in enumerate(sub):
                d.text((int(width*.11),int(height*.795+k*height*.044)),line,font=pf,fill='#D9D2C4')
            d.rectangle((int(width*.11),int(height*.917),int(width*.89),int(height*.923)),fill='#4A4238')
            d.rectangle((int(width*.11),int(height*.917),int(width*(.11+.78*(fr+1)/(40*fps))),int(height*.923)),fill='#C7A66C')
            middle(d,int(height*.944),'UNPUBLISHED RESEARCH FILM  ·  SILENT',bf,'#B8A995')
            p.stdin.write(im.tobytes())
    except BrokenPipeError:
        raise RuntimeError('ffmpeg terminated unexpectedly')
    finally:
        try:p.stdin.close()
        except Exception:pass
    code=p.wait()
    if code:raise RuntimeError(f'ffmpeg failed: {code}')
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',default='zen12-evidence-40s.mp4');ap.add_argument('--width',type=int,default=540);ap.add_argument('--fps',type=int,default=12)
    a=ap.parse_args(); make(Path(a.out),a.width,a.width*16//9,a.fps)
    print(a.out)
