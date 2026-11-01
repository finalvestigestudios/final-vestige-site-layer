#!/usr/bin/env python3
"""Reproducible original 40s silent FV McGurk explanatory film. Not a true McGurk stimulus.
Requires Pillow, ffmpeg/ffprobe. Outputs only offline review MP4; never uploads to WordPress.
"""
import argparse
import io
import math
import subprocess
from PIL import Image, ImageDraw, ImageFont

W,H,FPS,SECONDS=540,960,12,40
TIMES=[0,6,13,20,27,34,40]
HEADS=[
    ("The syllable","you heard","What did the soundtrack contain?"),
    ("One sound.","Two signals.","1976: voice BA. Visible lips GA."),
    ("The third","syllable","Some reported DA. Soundtrack still BA."),
    ("No universal","reaction","The clip and the question matter."),
    ("Experience","is evidence","An explanation still needs a test."),
    ("Check the","original study","Read the sources. Final Vestige.")
]
CAPTIONS=[
"You heard a syllable. But what did the soundtrack contain?",
"In 1976, a voice said BA while a film showed lips forming GA.",
"Some listeners reported DA. The audio was still BA.",
"Not everyone hears the same thing. The clip and question matter.",
"Perception is evidence of an experience—not proof of every proposed explanation.",
"Ask what the original study tested. Read the sources. Final Vestige."
]
BG=(9,10,10); GOLD=(205,168,104); INK=(244,239,230); MUTED=(189,182,170); FRAME=(74,65,50)
def font(size,bold=False,serif=False):
    family="DejaVuSerif" if serif else "DejaVuSans"
    suffix="-Bold.ttf" if bold else ".ttf"
    p="/usr/share/fonts/truetype/dejavu/"+family+suffix
    try:return ImageFont.truetype(p,size)
    except OSError:return ImageFont.load_default()
def wrap(draw,txt,f,max_width):
    result=[]; current=""
    for w in txt.split():
        trial=(current+" "+w).strip()
        if draw.textbbox((0,0),trial,font=f)[2]>max_width and current:
            result.append(current);current=w
        else:current=trial
    if current:result.append(current)
    return result
def centered(draw,txt,y,f,fill,max_width=460,spacing=12):
    lines=wrap(draw,txt,f,max_width)
    for line in lines:
        bb=draw.textbbox((0,0),line,font=f)
        draw.text(((W-(bb[2]-bb[0]))/2,y),line,font=f,fill=fill)
        y+=(bb[3]-bb[1])+spacing
    return y
def scene_index(t):
    return next(i for i in range(6) if TIMES[i]<=t<TIMES[i+1])
def frame(t):
    i=scene_index(t);local=t-TIMES[i];span=TIMES[i+1]-TIMES[i]
    im=Image.new("RGB",(W,H),BG);d=ImageDraw.Draw(im)
    d.rounded_rectangle((25,25,515,935),radius=3,outline=FRAME,width=2)
    d.text((53,57),"F I N A L  V E S T I G E",font=font(17,True),fill=GOLD)
    d.text((53,93),"MIND / PERCEPTION / EVIDENCE",font=font(14),fill=MUTED)
    d.line((53,126,486,126),fill=FRAME,width=2)
    d.text((53,156),f"0{i+1} / 06",font=font(18,True),fill=GOLD)
    head1,head2,small=HEADS[i]
    centered(d,head1,211,font(39,serif=True),INK)
    centered(d,head2,269,font(47,serif=True),INK)
    # Schematic centre; only this graphic is animated, not any real mouth or sound.
    cx,cy=270,509
    if i==0:
        d.rounded_rectangle((72,400,468,623),radius=22,outline=GOLD,width=2)
        d.text((114,430),"SOUND ≠ REPORT",font=font(22,True),fill=GOLD)
        for j in range(18):
            x=106+j*19
            amp=18*math.sin(j*.85+t*2)
            d.line((x,551-amp,x,551+amp),fill=INK,width=3)
    elif i in (1,2):
        d.rounded_rectangle((61,400,244,631),radius=13,outline=GOLD,width=2)
        d.rounded_rectangle((296,400,479,631),radius=13,outline=GOLD,width=2)
        d.text((91,424),"AUDIO",font=font(20,True),fill=MUTED)
        d.text((325,424),"VISUAL",font=font(20,True),fill=MUTED)
        centered(d,"BA",490,font(64,serif=True),INK) if False else None
        d.text((107,499),"BA",font=font(61,serif=True),INK)
        d.text((341,499),"GA",font=font(61,serif=True),INK)
        if i==2:
            d.rounded_rectangle((167,583,374,663),radius=15,fill=(42,34,24),outline=GOLD,width=2)
            d.text((186,596),"some: DA",font=font(28,True),INK)
    elif i==3:
        for j,(x,label) in enumerate([(69,"BA"),(197,"DA"),(325,"OTHER")]):
            d.rounded_rectangle((x,445,x+114,572),radius=13,outline=GOLD if j==1 else FRAME,width=2)
            d.text((x+12,484),label,font=font(22,True),INK)
        d.text((68,612),"Different viewers; different reports.",font=font(16),MUTED)
    elif i==4:
        d.rounded_rectangle((57,408,483,645),radius=14,outline=GOLD,width=2)
        d.text((82,444),"OBSERVED",font=font(22,True),GOLD)
        d.text((82,482),"A listener reports DA.",font=font(19),INK)
        d.line((82,524,455,524),fill=FRAME,width=2)
        d.text((82,543),"INFERRED",font=font(22,True),GOLD)
        d.text((82,580),"Which mechanism caused it?",font=font(18),INK)
    else:
        d.rounded_rectangle((59,423,482,632),radius=14,outline=GOLD,width=2)
        centered(d,"McGurk & MacDonald",454,font(24,True),INK)
        centered(d,"Nature · 1976",502,font(22),GOLD)
        centered(d,"doi:10.1038/264746a0",548,font(18),MUTED)
    d.line((53,707,486,707),fill=FRAME,width=2)
    centered(d,small,735,font(21),INK,430,12)
    centered(d,CAPTIONS[i],815,font(15),MUTED,430,7)
    d.text((53,899),"SCHEMATIC · NOT A PERCEPTION TEST",font=font(13,True),GOLD)
    # tiny progress line, no blinking/flashing
    d.rectangle((53,918,53+round(434*t/SECONDS),922),fill=GOLD)
    return im
def render(output):
    cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-an","-c:v","libx264","-preset","medium","-crf","29","-pix_fmt","yuv420p","-movflags","+faststart",output]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for k in range(FPS*SECONDS):
            p.stdin.write(frame(k/FPS).tobytes())
        p.stdin.close()
        if p.wait()!=0:raise RuntimeError("ffmpeg failed")
    finally:
        if p.poll() is None:p.kill()
    print("Rendered",output,"frames",FPS*SECONDS,"seconds",SECONDS)
if __name__=="__main__":
    ar=argparse.ArgumentParser()
    ar.add_argument("--out",default="fv-mcgurk-40s.mp4")
    args=ar.parse_args()
    render(args.out)
