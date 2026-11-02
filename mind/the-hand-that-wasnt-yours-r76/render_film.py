"""Original 40-second vertical editorial film. No experiment recreation or merchant assets.
Rendering is offline only; never upload to a public site without explicit approval.
Needs Pillow and ffmpeg. Uses system fonts but does not redistribute them.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import subprocess
import math

ROOT = Path(__file__).resolve().parent
W, H, FPS, SECONDS = 540, 960, 12, 40
SERIF = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
SANS = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
GOLD = (218, 180, 124)
WHITE = (245, 237, 222)
SOFT = (189, 182, 171)
INK = (13, 16, 16)

font = lambda size, serif=False: ImageFont.truetype(SERIF if serif else SANS, size)


def center_text(draw, msg, y, size=28, col=WHITE, serif=False, spacing=1.2):
    lines=msg.split('\n')
    f=font(size,serif)
    dy=int(size*spacing)
    for i,line in enumerate(lines):
        width=draw.textbbox((0,0),line,font=f)[2]
        draw.text(((W-width)/2,y+i*dy),line,font=f,fill=col,stroke_width=0)


def paper_base(frame):
    pic=Image.new('RGB',(W,H),INK)
    d=ImageDraw.Draw(pic)
    for y in range(H):
        v=int(7+10*y/H)
        d.line((0,y,W,y), fill=(v+7,v+9,v+9))
    d.rectangle((30,30,W-30,H-30),outline=(83,71,55),width=2)
    d.line((58,124,W-58,124),fill=(84,72,54),width=2)
    d.line((58,826,W-58,826),fill=(84,72,54),width=2)
    d.text((57,60),'F I N A L   V E S T I G E',font=font(17),fill=GOLD)
    d.text((57,94),'MIND / PERCEPTION',font=font(13),fill=SOFT)
    d.text((58,851),'ORIGINAL EDITORIAL ILLUSTRATION  /  2026',font=font(11),fill=SOFT)
    d.text((58,879),'NOT A LIVE EXPERIMENT  •  NOT AN ENDORSEMENT',font=font(10),fill=SOFT)
    return pic,d


def hand(d, origin=(315,450),scale=1.0,glow=False):
    """Original geometric limb motif, not a stock/copyrighted study photograph."""
    x,y=origin
    coords=[(-63,138),(-65,30),(-75,-30),(-65,-69),(-48,-64),(-46,12),(-42,-106),(-26,-130),(-12,-117),(-12,4),
            (-7,-140),(11,-151),(22,-137),(18,2),(29,-118),(46,-125),(56,-110),(46,14),(58,-79),(73,-80),
            (83,-60),(65,48),(70,138)]
    pts=[(int(x+a*scale),int(y+b*scale)) for a,b in coords]
    if glow:
        d.line(pts+[pts[0]],fill=(105,84,57),width=max(5,int(10*scale)),joint='curve')
    d.polygon(pts,fill=(49,49,45),outline=(219,184,127),width=max(2,int(4*scale)))
    for yy in [-55,-20,20,75]:
        d.arc((int(x-39*scale),int(y+yy*scale),int(x+41*scale),int(y+(yy+60)*scale)),190,345,fill=(107,96,78),width=2)


def brush(d,x,y,s=1.0):
    d.line((x-56*s,y-78*s,x,y),fill=GOLD,width=max(3,int(5*s)))
    d.ellipse((x-10*s,y-10*s,x+10*s,y+10*s), fill=(232,220,191))
    for j in [-8,-3,3,8]:
        d.line((x+j*s,y-6*s,x+(j+2)*s,y+8*s),fill=WHITE,width=2)


def scene(d,index,local):
    pulse=math.sin(local*2*math.pi)/2+0.5
    if index==0:
        d.rectangle((77,340,463,650), fill=(22,25,24), outline=(119,98,65),width=2)
        hand(d,(270,495),1.0,True)
        center_text(d,'THE HAND THAT\nWASN\'T YOURS',175,34,WHITE,True,1.26)
        center_text(d,'1998  •  A QUESTION OF OWNERSHIP',700,16,GOLD)
        center_text(d,'Botvinick & Cohen · Nature',740,14,SOFT)
    elif index==1:
        center_text(d,'TWO HANDS.\nTWO BRUSHES.',168,31,WHITE,True)
        hand(d,(175,465),.72)
        hand(d,(370,465),.72)
        d.rectangle((85,400,259,632),outline=(65,65,65),width=3)
        d.rectangle((87,402,257,630),fill=(27,30,28))
        brush(d,175,385+int(10*pulse),.75)
        brush(d,370,385+int(10*pulse),.75)
        center_text(d,'MATCHED IN TIME',700,23,GOLD,True)
        center_text(d,'One hand visible. One hand hidden.',750,15,SOFT)
    elif index==2:
        center_text(d,'WHAT FEELS LIKE\n"MINE"?',169,35,WHITE,True)
        hand(d,(270,465),1.18,True)
        d.arc((110,275,430,640),20,160,fill=GOLD,width=3)
        center_text(d,'Some participants report ownership',702,17,GOLD)
        center_text(d,'Others do not. The reports vary.',738,15,SOFT)
    elif index==3:
        center_text(d,'NOW SHIFT\nTHE TIMING',165,37,WHITE,True)
        hand(d,(185,470),.79)
        hand(d,(370,470),.79)
        brush(d,187,340+int(6*pulse),.8)
        brush(d,372,405-int(7*pulse),.8)
        d.line((180,640,365,640),fill=(170,133,88),width=2)
        center_text(d,'SYNCHRONY  /  ASYNCHRONY',685,17,GOLD)
        center_text(d,'Conditions matter more than anecdotes.',732,15,SOFT)
    elif index==4:
        center_text(d,'TWO STORIES\nIN THE DATA',175,35,WHITE,True)
        d.rounded_rectangle((65,355,259,615),radius=14,fill=(32,36,34),outline=(140,114,72),width=2)
        d.rounded_rectangle((281,355,475,615),radius=14,fill=(32,36,34),outline=(140,114,72),width=2)
        d.text((98,420),'SENSORY',font=font(19),fill=GOLD)
        d.text((107,465),'TIMING',font=font(19),fill=GOLD)
        d.text((304,420),'EXPECTATION',font=font(15),fill=GOLD)
        d.text((311,465),'SUGGESTION',font=font(15),fill=GOLD)
        center_text(d,'Their relative roles are debated.',691,17,SOFT)
        center_text(d,'Lush 2020  /  Slater & Ehrsson 2022',740,13,SOFT)
    else:
        center_text(d,'AN EXPERIENCE\nIS NOT AN\nEXPLANATION.',205,34,WHITE,True,1.36)
        d.ellipse((188,485,352,649),outline=GOLD,width=4)
        center_text(d,'?',515,84,GOLD,True)
        center_text(d,'Follow the evidence, not a promise.',716,17,GOLD)
        center_text(d,'Source notes: see independent investigation.',753,12,SOFT)


def render():
    out=ROOT/'the-hand-that-wasnt-yours-40s.mp4'
    durations=[6,7,7,7,7,6]
    boundary=[]
    t=0
    for seconds in durations:
        boundary.append((t,t+seconds))
        t+=seconds
    assert t==SECONDS
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-crf','24','-preset','veryfast','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
    process=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    poster=None
    for i in range(FPS*SECONDS):
        second=i/FPS
        sc=next(j for j,(a,b) in enumerate(boundary) if a<=second<b)
        start,end=boundary[sc]
        frame,d=paper_base(i)
        scene(d,sc,(second-start)/(end-start))
        # Gentler beginning/end fade improves social crop legibility, without flashing.
        fade=min(1,second/0.55,(SECONDS-second)/0.55)
        if fade<1:
            darkness=Image.new('RGB',(W,H),INK)
            frame=Image.blend(darkness,frame,max(0,fade))
        if i==7:
            poster=frame.copy()
        process.stdin.write(frame.tobytes())
    process.stdin.close()
    if process.wait()!=0:raise RuntimeError('ffmpeg encoding failed')
    assert poster is not None
    poster.save(ROOT/'poster.png',optimize=True)
    return out

if __name__=='__main__':
    print(render())
