"""Original silent 40 s vertical evidence film. Dependencies: pillow, ffmpeg, ffprobe.
Run: python render_film.py. No network, stock imagery, music, product claims or branding borrowed.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math, os, subprocess, tempfile, hashlib
W,H,FPS=540,960,12
ROOT=Path(__file__).resolve().parent
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
REG='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
SCENES=[
 ('THE TREE THAT\nWASN’T MAGNETIZED','PARIS · 1784','A claim meets a controlled question.'),
 ('ONE APRICOT TREE\nWAS TREATED','THE PROPOSED FORCE','The boy waited inside while the operator worked.'),
 ('FOUR OTHER TREES.\nEYES COVERED.','THE TEST','He visited them in sequence, unaware which was treated.'),
 ('AT TREE FOUR,\nHE COLLAPSED.','THE OBSERVATION','Tree four had not been magnetized.'),
 ('WHAT CAUSED\nTHE EXPERIENCE?','THE INFERENCE','A genuine reaction does not identify its cause.'),
 ('FEELING SOMETHING\nIS NOT PROOF.','FINAL VESTIGE · EVIDENCE FIRST','Read the 1785 translation; examine the limits.'),
]

def font(p,s): return ImageFont.truetype(p,s)
def multiline(d,t,x,y,ft,fill,spacing=17):
    for ln in t.split('\n'):
        d.text((x,y),ln,font=ft,fill=fill,stroke_width=0); y+=d.textbbox((0,0),ln,font=ft)[3]+spacing
    return y

def scene_image(i):
    im=Image.new('RGB',(W,H),'#0A0B0B'); d=ImageDraw.Draw(im)
    for y in range(H):
        k=round(7+6*y/H); d.line((0,y,W,y),fill=(k+1,k+2,k+2))
    for x in range(25,W,46): d.line((x,0,x,H),fill='#131513',width=1)
    d.rectangle((25,28,W-25,32),fill='#B8955E')
    d.text((27,51),'FINAL VESTIGE  /  MIND & PERCEPTION',font=font(BOLD,13),fill='#D1B17C')
    d.text((27,103),f'ARCHIVAL FILE  /  0{i+1}',font=font(REG,17),fill='#AAA49A')
    trunk=(259,300,280,510); d.rectangle(trunk,fill='#665039')
    for dx,dy,r in [(-82,312,55),(-25,277,66),(52,295,64),(94,333,46),(-95,359,36),(17,354,78)]:
        d.ellipse((W//2+dx-r,dy-r,W//2+dx+r,dy+r),fill='#2B382C',outline='#5B6545',width=2)
    d.line((40,520,500,520),fill='#78644B',width=3)
    for x in (104,216,327,436):
        d.line((x,540,x,582),fill='#7C6C53',width=3)
    d.ellipse((94+(i%4)*111,545,110+(i%4)*111,560),fill='#B8955E')
    if i==3: d.line((425,540,463,590),fill='#D09A88',width=7)
    d.rectangle((21,601,W-21,916),fill='#111414',outline='#5D4D3D',width=2)
    d.text((41,624),SCENES[i][1],font=font(BOLD,17),fill='#B8955E')
    multiline(d,SCENES[i][0],41,674,font(BOLD,30),'#F4EFE6',11)
    words=SCENES[i][2].split(); lines=[]; line=''; f=font(REG,18)
    for w in words:
        t=(line+' '+w).strip()
        if d.textbbox((0,0),t,font=f)[2]>451:
            lines.append(line); line=w
        else:line=t
    lines.append(line);multiline(d,'\n'.join(lines),42,835,f,'#D8D2C7',8)
    d.text((24,933),'ARCHIVE  /  1784—1785',font=font(REG,14),fill='#A59E93')
    return im

if __name__=='__main__':
    stills=[scene_image(i) for i in range(6)]
    for i,im in enumerate(stills): im.save(ROOT/f'scene-{i+1:02}.png',optimize=True)
    stills[0].save(ROOT/'franklin-tree-poster.png',optimize=True)
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)
        for n in range(480): os.link(ROOT/f'scene-{n//80+1:02}.png',p/f'frame_{n:03}.png')
        cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-framerate',str(FPS),'-i',str(p/'frame_%03d.png'),'-c:v','libx264','-preset','veryfast','-crf','29','-pix_fmt','yuv420p','-movflags','+faststart',str(ROOT/'franklin-tree-40s.mp4')]
        subprocess.run(cmd,check=True)
    print('SHA256',hashlib.sha256((ROOT/'franklin-tree-40s.mp4').read_bytes()).hexdigest())
    subprocess.run(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height,r_frame_rate,nb_frames','-of','default=nw=1',str(ROOT/'franklin-tree-40s.mp4')],check=True)
