from PIL import Image, ImageDraw, ImageFont
import math, subprocess, textwrap, pathlib, random
W,H,FPS,SECONDS = 540,960,12,40
DIR=pathlib.Path(__file__).resolve().parent
BG=(11,12,12); GOLD=(196,161,102); WHITE=(240,232,219); MUTED=(185,175,157); LINE=(62,57,48)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
f_small=ImageFont.truetype(FONT,17);f_body=ImageFont.truetype(FONT,24);f_caption=ImageFont.truetype(FONT,21);f_head=ImageFont.truetype(SERIF,38);f_big=ImageFont.truetype(SERIF,52)
slides=[
 (0,6.5,'THE PENDULUM','A pendulum swings while your fingers seem still.'),
 (6.5,13.2,'1852 — CARPENTER','In 1852, William Carpenter proposed that expectation could guide small movements without a conscious decision.'),
 (13.2,19.8,'MAKE IT MEASURABLE','More than a century later, scientists measured the effect.'),
 (19.8,26.3,'AN EXPLANATION, NOT A SPELL','Small finger motions can build a visible swing. That doesn\'t make the experience imaginary. It makes the explanation testable.'),
 (26.3,33.2,'NOT PRODUCT EVIDENCE','And the same evidence rule applies to meditation audio: a convincing experience isn\'t proof of a promised neurological outcome.'),
 (33.2,40,'EVIDENCE BEFORE EXPLANATION','Start with what is actually measured.')]
base=Image.new('RGB',(W,H),BG);bd=ImageDraw.Draw(base)
for y in range(H):
    v=int(4*math.sin(y/H*math.pi))
    bd.line((0,y,W,y), fill=(BG[0]+v,BG[1]+v,BG[2]+v))
# subtle bordered editorial frame
bd.rectangle([24,24,W-24,H-24],outline=LINE,width=1)
bd.line([55,90,W-55,90],fill=GOLD,width=2)
bd.line([55,H-132,W-55,H-132],fill=LINE,width=2)

def center(draw,text,y,font,color):
    box=draw.textbbox((0,0),text,font=font)
    draw.text(((W-(box[2]-box[0]))/2,y),text,font=font,fill=color)

def multiline(draw,text,x,y,font,color,width=39,line_height=37):
    words=text.split(); lines=[]; row=''
    for word in words:
        tentative=(row+' '+word).strip()
        if draw.textbbox((0,0),tentative,font=font)[2]>W-2*x and row:
            lines.append(row);row=word
        else:row=tentative
    if row:lines.append(row)
    for line in lines:
        draw.text((x,y),line,font=font,fill=color);y+=line_height
    return y

def pendulum(draw,t,cy=350,small=False):
    pivot=(W//2,cy)
    L=240 if not small else 120
    angle=0.17*math.sin((t+0.6)*2.25)
    bob=(pivot[0]+int(L*math.sin(angle)),pivot[1]+int(L*math.cos(angle)))
    draw.ellipse((pivot[0]-5,pivot[1]-5,pivot[0]+5,pivot[1]+5),fill=GOLD)
    draw.line((pivot,bob),fill=GOLD,width=3)
    r=38 if not small else 26
    draw.ellipse([bob[0]-r,bob[1]-r,bob[0]+r,bob[1]+r],fill=(116,90,52),outline=(224,188,117),width=3)
    draw.ellipse([bob[0]-r+9,bob[1]-r+7,bob[0]-r+22,bob[1]-r+20],fill=(227,200,143))

def render(t):
    im=base.copy();d=ImageDraw.Draw(im)
    idx=next((i for i,s in enumerate(slides) if s[0]<=t<s[1]),5)
    start,end,heading,copy=slides[idx]
    d.text((55,53),'FINAL VESTIGE    /    MIND & PERCEPTION',font=f_small,fill=GOLD)
    center(d,str(idx+1).zfill(2)+' / 06',113,f_small,MUTED)
    if idx==0:
        center(d,heading,161,f_head,WHITE);pendulum(d,t,312)
    elif idx==1:
        center(d,'1852',180,f_big,GOLD)
        d.rectangle((68,290,W-68,530),outline=LINE,width=2)
        center(d,'WILLIAM BENJAMIN',331,f_body,WHITE)
        center(d,'CARPENTER',374,f_head,WHITE)
        center(d,'Expectation → subtle movement',455,f_small,MUTED)
    elif idx==2:
        center(d,heading,167,f_head,WHITE)
        d.line((73,346,467,346),fill=LINE,width=2)
        d.line((73,516,467,516),fill=LINE,width=2)
        d.text((75,315),'FINGERTIP MOTION / SMALL',font=f_small,fill=GOLD)
        d.text((75,485),'PENDULUM SWING / VISIBLE',font=f_small,fill=GOLD)
        for x in range(75,468,2):
            ax=(x-75)/392
            d.point((x,346+int(8*math.sin(ax*4*math.pi+t*.3))),fill=MUTED)
            d.point((x,516+int(32*math.sin(ax*4*math.pi+t*.3))),fill=GOLD)
    elif idx==3:
        center(d,'OBSERVATION',182,f_head,GOLD)
        center(d,'IS NOT CAUSATION',240,f_head,WHITE)
        pendulum(d,t,335,small=True)
        d.line((93,650,447,650),fill=LINE,width=2)
    elif idx==4:
        center(d,'THE RESEARCH TEST',171,f_head,WHITE)
        d.rectangle((60,300,480,555),outline=LINE,width=2)
        center(d,'PENDULUM STUDIES',354,f_body,GOLD)
        center(d,'≠',401,f_big,WHITE)
        center(d,'ZEN12 PRODUCT TRIAL',488,f_body,GOLD)
    else:
        center(d,'THE MIND IS',235,f_big,WHITE)
        center(d,'AN UNRELIABLE',308,f_big,WHITE)
        center(d,'WITNESS.',381,f_big,GOLD)
        d.line((107,518,433,518),fill=GOLD,width=2)
        center(d,'Sources: Carpenter 1852 / Cantergi 2021',572,f_small,MUTED)
        center(d,'No commercial efficacy claim',610,f_small,MUTED)
    d.rectangle((39,675,W-39,837),fill=(18,19,18),outline=LINE,width=1)
    multiline(d,copy,55,689,f_caption,WHITE,line_height=29)
    d.text((55,841),'ORIGINAL EXPLAINER • SILENT WITH CAPTIONS',font=f_small,fill=MUTED)
    d.line((55,886,55+int((W-110)*t/SECONDS),886),fill=GOLD,width=4)
    d.text((55,903),'SOURCES + FULL TRANSCRIPT IN GUIDE',font=f_small,fill=MUTED)
    return im

# Poster at midpoint of first segment; not a misleading media player.
render(2.2).save(DIR/'chevreul-40s-poster.png', optimize=True)
output=DIR/'chevreul-40s.mp4'
args=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','medium','-crf','26','-pix_fmt','yuv420p','-movflags','+faststart',str(output)]
p=subprocess.Popen(args,stdin=subprocess.PIPE)
try:
    for frame in range(FPS*SECONDS):
        p.stdin.write(render(frame/FPS).tobytes())
    p.stdin.close();status=p.wait()
finally:
    if p.stdin and not p.stdin.closed:p.stdin.close()
if status:raise SystemExit(f'ffmpeg failed {status}')
print(output,'bytes',output.stat().st_size)
