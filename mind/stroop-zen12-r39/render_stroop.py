#!/usr/bin/env python3
"""Original offline Stroop/suggestion explainer film for Final Vestige.
No purchased assets, no audio, no external requests; 6 scenes, exactly 40s @12fps.
Requires Pillow and ffmpeg. Educational schematic, not an original Stroop trial
and not scientific evidence of Zen12 effectiveness.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess, math, hashlib, json

OUTPUT_DIR = Path(__file__).resolve().parent
W, H, FPS = 540, 960, 12
SEGMENTS = [6,7,8,7,6,6]
BKG = (11,16,22)
PANEL = (21,29,38)
GOLD = (229,192,135)
WHITE = (248,237,223)
MUTED = (193,202,204)
BLUE = (72,134,182)
RUST = (217,141,106)
FONT_SANS = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONT_SERIF = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
FONT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def font(size, face=FONT_SANS):
    return ImageFont.truetype(face, size)

def lines(text, max_width, typeface):
    result=[]
    for paragraph in text.split('\n'):
        if not paragraph.strip():
            result.append('');continue
        words=paragraph.split(); cur=''
        for word in words:
            trial = (cur+' '+word).strip()
            if ImageDraw.Draw(Image.new('RGB',(1,1))).textbbox((0,0),trial,font=typeface)[2] <= max_width:
                cur=trial
            else:
                if cur: result.append(cur)
                cur=word
        if cur: result.append(cur)
    return result

def center(draw, text, y, fnt, fill=WHITE, spacing=9, max_width=444):
    ls=lines(text,max_width,fnt)
    for i,l in enumerate(ls):
        box=draw.textbbox((0,0),l,font=fnt)
        draw.text(((W-(box[2]-box[0]))/2, y+i*(fnt.size+spacing)),l,font=fnt,fill=fill,stroke_width=0)
    return y+len(ls)*(fnt.size+spacing)

def baseline(draw, number, source):
    draw.line([(46,84),(W-46,84)],fill=(86,92,95),width=1)
    draw.text((48,42),'F I N A L   V E S T I G E',font=font(19,FONT_BOLD),fill=GOLD)
    draw.text((48,H-105),'MIND / PERCEPTION',font=font(17,FONT_BOLD),fill=GOLD)
    draw.text((48,H-72),source,font=font(15),fill=MUTED)
    draw.text((W-98,H-105),f'{number} / 6',font=font(17,FONT_BOLD),fill=GOLD)
    draw.line([(46,H-125),(W-46,H-125)],fill=(86,92,95),width=1)

def scene1(d,phase):
    center(d,'THE WORD / THE INK',162,font(30,FONT_SERIF),GOLD)
    center(d,'BLUE',338,font(106,FONT_SERIF),RUST,max_width=500)
    d.line([(110,482),(430,482)],fill=GOLD,width=2)
    center(d,'The word says one thing.',531,font(27,FONT_SERIF),WHITE)
    center(d,'The ink asks another.',591,font(27,FONT_SERIF),WHITE)
    d.text((57,744),'Actual ink here: rust orange',font=font(18),fill=MUTED)

def scene2(d,phase):
    center(d,'TWO RESPONSES',169,font(31,FONT_SERIF),GOLD)
    d.rounded_rectangle((46,289,494,427),radius=10,fill=(29,43,52),outline=(87,117,125),width=2)
    center(d,'READ THE WORD',303,font(18,FONT_BOLD),MUTED)
    center(d,'BLUE',353,font(46,FONT_SERIF),WHITE)
    d.rounded_rectangle((46,465,494,603),radius=10,fill=(39,32,31),outline=(151,113,95),width=2)
    center(d,'NAME THE INK',478,font(18,FONT_BOLD),MUTED)
    center(d,'ORANGE',527,font(40,FONT_SERIF),RUST)
    center(d,'A practiced reading habit can interfere.',659,font(24,FONT_SERIF),WHITE,max_width=430)

def scene3(d,phase):
    center(d,'SELECTED LABORATORY TASKS',162,font(29,FONT_SERIF),GOLD)
    center(d,'2002  ·  2005',274,font(46,FONT_SERIF),WHITE)
    d.rounded_rectangle((70,371,470,584),radius=12,fill=PANEL,outline=(119,112,97),width=2)
    center(d,'HIGH SUGGESTIBILITY',401,font(21,FONT_BOLD),GOLD)
    center(d,'Some participants showed less interference after a suggestion.',466,font(25,FONT_SERIF),WHITE,max_width=350)
    center(d,'The result depends on the people and task.',640,font(24,FONT_SERIF),MUTED,max_width=420)

def scene4(d,phase):
    center(d,'THE INDUCTION QUESTION',165,font(30,FONT_SERIF),GOLD)
    center(d,'2006',266,font(57,FONT_SERIF),WHITE)
    d.line([(122,380),(418,380)],fill=GOLD,width=2)
    d.rounded_rectangle((45,397,255,529),radius=8,fill=(27,40,52),outline=(90,131,146),width=2)
    d.rounded_rectangle((285,397,495,529),radius=8,fill=(41,34,34),outline=(152,115,93),width=2)
    f=font(18,FONT_BOLD)
    for x1,x2,labels in [(45,255,['With hypnosis','induction']),(285,495,['Without formal','induction'])]:
        for j,txt in enumerate(labels):
            bb=d.textbbox((0,0),txt,font=f)
            tx=x1+(x2-x1-(bb[2]-bb[0]))/2
            d.text((tx,428+j*32),txt,font=f,fill=WHITE)
    center(d,'Suggestion effects were reported in both conditions.',622,font(23,FONT_SERIF),WHITE,max_width=420)

def scene5(d,phase):
    center(d,'EVIDENCE HAS LIMITS',179,font(30,FONT_SERIF),GOLD)
    d.rounded_rectangle((57,316,483,528),radius=12,fill=(47,34,33),outline=RUST,width=3)
    center(d,'STROOP TASK',347,font(26,FONT_BOLD),WHITE)
    center(d,'≠',405,font(50,FONT_SERIF),RUST)
    center(d,'COMMERCIAL AUDIO PROOF',466,font(21,FONT_BOLD),WHITE,max_width=360)
    center(d,'No study here tested Zen12 or an hour-in-twelve claim.',598,font(25,FONT_SERIF),WHITE,max_width=415)

def scene6(d,phase):
    center(d,'FOLLOW THE SOURCES',183,font(32,FONT_SERIF),GOLD)
    d.ellipse((205,350,335,480),outline=(217,167,107),width=5)
    d.line([(270,382),(270,417),(298,437)],fill=(237,213,165),width=5)
    center(d,'TRY A FREE',533,font(26,FONT_BOLD),MUTED)
    center(d,'12-MINUTE',583,font(43,FONT_SERIF),WHITE)
    center(d,'ATTENTION PRACTICE',649,font(28,FONT_SERIF),WHITE)
    center(d,'No purchase. No guaranteed outcome.',757,font(20),MUTED)

DRAW_SCENES=[scene1,scene2,scene3,scene4,scene5,scene6]
SRC=['ORIGINAL SCHEMATIC, NOT EXPERIMENT FOOTAGE',
     'STROOP TASK / COLOR-WORD CONFLICT',
     'RAZ ET AL. 2002 AND 2005',
     'RAZ ET AL. 2006 / CONTROL CONDITIONS',
     'PRODUCT SPECIFIC EVIDENCE REQUIRED',
     'FREE REFLECTION / FINALVESTIGE.COM']

def draw_frame(idx,progress,fade):
    frame=Image.new('RGB',(W,H),BKG);d=ImageDraw.Draw(frame)
    for y in range(H):
        t=y/H
        # Very subtle vertically graded, high contrast background.
        tone=(int(BKG[0]+6*t),int(BKG[1]+9*t),int(BKG[2]+12*t))
        d.line([(0,y),(W,y)],fill=tone)
    # Non-flashing, no strobes, no images of people.
    baseline(d,idx+1,SRC[idx]);DRAW_SCENES[idx](d,progress)
    if fade<1:
        frame=Image.blend(Image.new('RGB',(W,H),BKG),frame,fade)
    return frame

def main():
    total=sum(SEGMENTS)*FPS
    out=OUTPUT_DIR/'stroop-suggestion-40s.mp4'
    command=['ffmpeg','-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','25','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
    proc=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    frameNo=0
    try:
        for ix,sec in enumerate(SEGMENTS):
            n=sec*FPS
            for fr in range(n):
                fade=min(1,fr/5) # fade in from dark over ~0.4 s (no flash)
                frame=draw_frame(ix,fr/n,fade)
                proc.stdin.write(frame.tobytes())
                frameNo+=1
        proc.stdin.close();rc=proc.wait()
        if rc!=0:raise RuntimeError(proc.stderr.read().decode(errors='replace'))
    finally:
        if proc.poll() is None:proc.kill()
    assert frameNo==total==480
    poster=draw_frame(0,0.5,1)
    poster.save(OUTPUT_DIR/'stroop-suggestion-poster.png', optimize=True)
    stat=out.stat()
    print(json.dumps({'file':str(out),'bytes':stat.st_size,'frames':frameNo,'duration_expected':40,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()},indent=2))

if __name__=='__main__':main()
