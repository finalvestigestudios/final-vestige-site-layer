#!/usr/bin/env python3
"""Original, silent forty-second Final Vestige Necker-cube research film.
Only Pillow and an installed ffmpeg executable required. No external assets.
Usage: python render_film.py [output-directory]
"""
import math, os, sys, subprocess, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FPS, W, H, TOTAL = 12, 540, 960, 480
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent
OUT.mkdir(parents=True, exist_ok=True)
BG=(8,17,21); GOLD=(216,184,125); PAPER=(244,235,220); MUTED=(183,201,201); BORDER=(45,70,73)
FONTS='/usr/share/fonts/truetype/dejavu/'
def font(n, bold=False, serif=False):
    stem='DejaVuSerif' if serif else 'DejaVuSans'
    return ImageFont.truetype(FONTS+stem+('-Bold' if bold else '')+'.ttf',n)
HEAD=font(45,True,True); LABEL=font(17,True); CAP=font(23); BRAND=font(13,True); SMALL=font(17)
SCENES=[
    (0,72,'WHICH FACE\nIS CLOSER?','You are watching a cube.\nDecide which square is nearest?'),
    (72,156,'DID THE\nCUBE FLIP?','For some observers, the\napparent depth reverses.'),
    (156,240,'THE LINES\nDID NOT MOVE','The ink never moved.\nYour interpretation did.'),
    (240,324,'GENEVA\n1832','Necker described a\nreversible figure in 1832.'),
    (324,408,'CONTROL\nHAS LIMITS','Eye movements and intention\ncan matter. Neither\nexplains everything.'),
    (408,480,'TEST THE\nEXPLANATION','Experience is evidence of\nexperience. Test the explanation.')
]
BACK=[(99,316),(335,316),(335,552),(99,552)]
FRONT=[(170,387),(406,387),(406,623),(170,623)]

def multiline_center(draw,xy,text,face,fill,spacing=10):
    draw.multiline_text(xy,text,font=face,fill=fill,spacing=spacing,align='center',anchor='ma')

def render_frame(i):
    sidx=next(k for k,s in enumerate(SCENES) if i < s[1])
    begin,end,title,caption=SCENES[sidx]
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
    for y in range(0,H,24):
        c=(12+int(3*y/H),24+int(2*y/H),29+int(3*y/H))
        d.line((0,y,W,y),fill=c,width=1)
    d.rounded_rectangle((24,22,W-24,H-22),radius=8,outline=BORDER,width=2)
    d.text((49,56),'FIELDNOTE    /    094',font=LABEL,fill=GOLD)
    d.line((49,91,W-49,91),fill=BORDER,width=2)
    d.multiline_text((W//2,142),title,font=HEAD,fill=PAPER,anchor='ma',align='center',spacing=6,stroke_width=0)
    # Immutable Necker-cube geometry: the same coordinates in all 480 frames.
    for quad in [BACK,FRONT]:
        d.line(quad+[quad[0]],fill=GOLD,width=6,joint='curve')
    for a,b in zip(BACK,FRONT):d.line((a[0],a[1],b[0],b[1]),fill=GOLD,width=6)
    d.text((W//2,673),'ONE DRAWING   /   TWO READINGS',font=SMALL,fill=MUTED,anchor='mm')
    d.line((50,721,W-50,721),fill=BORDER,width=2)
    d.multiline_text((W//2,753),caption,font=CAP,fill=PAPER,anchor='ma',align='center',spacing=10)
    d.text((W//2,895),'FINAL VESTIGE  /  MIND & PERCEPTION',font=BRAND,fill=GOLD,anchor='mm')
    return im

def produce():
    vid=OUT/'the-cube-never-moved-40s.mp4'
    cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-pix_fmt','yuv420p','-preset','fast','-crf','23','-movflags','+faststart',str(vid)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for i in range(TOTAL):p.stdin.write(render_frame(i).tobytes())
        p.stdin.close();err=p.stderr.read();code=p.wait()
        if code:raise RuntimeError(err.decode('utf8','replace'))
    except Exception:
        p.kill();raise
    render_frame(0).save(OUT/'poster.png')
    frames=[render_frame(n).resize((216,384)) for n in [35,110,192,275,360,444]]
    contact=Image.new('RGB',(216*3,384*2),(3,8,12))
    for ix,im in enumerate(frames):contact.paste(im,((ix%3)*216,(ix//3)*384))
    contact.save(OUT/'contact-sheet.png')
    print(vid)
if __name__=='__main__':produce()
