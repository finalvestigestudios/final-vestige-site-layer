"""Offline original 40s Final Vestige R32 film. No web, dependencies: Pillow+ffmpeg.
Silent, no flash, 540x960 / 12fps. Captions and transcript in FILM.vtt and FILM-PROTOCOL.md.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import subprocess, argparse
W,H,FPS=540,960,12
SCRIPT = [
    (0,7,'TWO EVENTS','Two targets can cross the same place on a screen within a fraction of a second.'),
    (7,14,'ONE REPORT','Yet in rapid sequences, people often report the first and miss the second.'),
    (14,21,'A NAME','Researchers call this the attentional blink. Timing and task instructions matter.'),
    (21,27,'A LIMIT','It is a laboratory pattern, not a diagnosis of your attention.'),
    (27,34,'THE EVIDENCE','Some meditation research is promising. It does not establish that a commercial audio file works.'),
    (34,40,'THE CHOICE','Try a free practice. Compare the actual package. Read the evidence before you buy.'),
]
BOLD='/usr/share/fonts/truetype/andika/Andika-Bold.ttf'
REG='/usr/share/fonts/truetype/andika/Andika-Regular.ttf'
FONT_BIG=ImageFont.truetype(BOLD,43)
FONT_MID=ImageFont.truetype(REG,31)
FONT_SM=ImageFont.truetype(REG,19)
BG=(9,10,10); CREAM=(244,239,230); GOLD=(201,163,109); MUTE=(194,184,169)
def wrap(draw,text,font,max_width):
    words=text.split(); lines=[]; current=''
    for word in words:
        proposal=(current+' '+word).strip()
        if current and draw.textbbox((0,0),proposal,font=font)[2] > max_width:
            lines.append(current); current=word
        else: current=proposal
    if current: lines.append(current)
    return lines
def frame(t):
    idx=next(i for i,(start,end,_,_) in enumerate(SCRIPT) if start<=t<end)
    start,end,title,body=SCRIPT[idx]
    canvas=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(canvas)
    d.rectangle((0,0,W,8),fill=GOLD)
    d.text((54,108),'FINAL VESTIGE / MIND',font=FONT_SM,fill=GOLD)
    d.line([(54,147),(486,147)],fill=(72,65,55),width=2)
    d.text((54,203),f'{idx+1:02d} / {len(SCRIPT):02d}',font=FONT_SM,fill=MUTE)
    d.text((54,273),title,font=FONT_BIG,fill=CREAM)
    d.rectangle((54,361,486,367),fill=(87,74,56))
    y=417
    for line in wrap(d,body,FONT_MID,432):
        d.text((54,y),line,font=FONT_MID,fill=CREAM); y+=58
    if idx<=3:
        d.rounded_rectangle((54,742,242,821),radius=8,outline=(115,96,70),width=3)
        d.rounded_rectangle((299,742,486,821),radius=8,outline=GOLD,width=3)
        d.text((130,766),'T1',font=FONT_MID,fill=CREAM)
        d.text((374,766),'T2',font=FONT_MID,fill=CREAM)
    else: d.line([(54,790),(486,790)],fill=GOLD,width=2)
    d.text((54,862),'EVIDENCE FIRST. NO GUARANTEES.',font=FONT_SM,fill=MUTE)
    d.rectangle((54,916,486,921),fill=(58,54,48))
    d.rectangle((54,916,54+int(432*(t/40)),921),fill=GOLD)
    return canvas
def render(output):
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','28','-pix_fmt','yuv420p','-movflags','+faststart',str(output)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for i in range(40*FPS):
            image=frame(i/FPS)
            if i==0: image.save(output.parent/'zen12-attention-poster.png',optimize=True)
            p.stdin.write(image.tobytes())
        p.stdin.close(); stderr=p.stderr.read()
        if p.wait()!=0: raise RuntimeError(stderr.decode())
    except Exception: p.kill(); raise
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',default='zen12-attention-40s.mp4');args=ap.parse_args()
    path=Path(args.out);path.parent.mkdir(parents=True,exist_ok=True);render(path)
