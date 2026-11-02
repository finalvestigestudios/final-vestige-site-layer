"""Render an original educational 40.0s silent 540x960 film; no copyrighted face photographs.
Requires Pillow and ffmpeg. All media offline review only. No network calls.
Run: python render_film.py [output_directory]
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import subprocess, sys, math

DEST = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("film-preview")
DEST.mkdir(parents=True, exist_ok=True)
W,H = 540,960
INK=(237,226,204); GOLD=(209,169,103); MUTED=(166,158,146); BG=(13,16,17)
FONTP="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
try:
    FONT=ImageFont.truetype(FONTP,25)
    BIG=ImageFont.truetype(FONTP,37)
    SMALL=ImageFont.truetype(FONTP,18)
except OSError:
    FONT=BIG=SMALL=ImageFont.load_default()
STAGES=[
    ("THE FACE","A face feels familiar","before its parts are counted.",0),
    ("WHOLE IMAGE","Turn the whole picture","upside down.",1),
    ("INNER PARTS","Turn eyes and mouth","inside the face.",2),
    ("SAME PIXELS","One relationship becomes","harder to judge.",3),
    ("TEST THE FRAME","Change orientation.","Test another explanation.",4),
    ("THE LIMIT","An illusion is not proof","of a product's claims.",5)
]
DURATIONS=[6,7,7,7,7,6]
def centered(draw,y,value,font,color):
    box=draw.textbbox((0,0),value,font=font)
    draw.text(((W-(box[2]-box[0]))/2,y),value,font=font,fill=color)
def face(im,kind):
    d=ImageDraw.Draw(im)
    x0,x1=133,407;y0,y1=245,592
    d.ellipse((x0,y0,x1,y1),outline=GOLD,width=6)
    d.arc((x0+28,y0+24,x1-28,y1-24),195,345,fill=(91,81,65),width=2)
    for x in (205,334):
        cy=378 if kind!=1 else 460
        d.ellipse((x-19,cy-19,x+19,cy+19),outline=INK,width=4)
        d.ellipse((x-7,cy-7,x+7,cy+7),fill=GOLD)
    if kind==2:
        d.arc((210,449,335,520),180,355,fill=INK,width=7)
        d.arc((207,330,333,370),0,180,fill=GOLD,width=5)
    else:
        d.arc((211,456,332,510),5,175,fill=GOLD,width=7)
    if kind==1:
        face_roi=im.crop((115,224,425,620)).rotate(180)
        im.paste(face_roi,(115,224))
def paint(idx):
    im=Image.new("RGB",(W,H),BG);d=ImageDraw.Draw(im)
    d.rectangle((21,21,W-21,H-21),outline=(82,75,63),width=2)
    d.rectangle((34,33,W-34,39),fill=GOLD)
    centered(d,78,"FINAL VESTIGE / MIND",SMALL,GOLD)
    centered(d,130,STAGES[idx][0],BIG,INK)
    if idx<4: face(im,idx)
    elif idx==4:
        for x,c in ((160,GOLD),(380,INK)):
            d.ellipse((x-74,341,x+74,489),outline=c,width=6)
            d.line((x,500,x,630),fill=c,width=3)
        centered(d,661,"RETINA     /     GRAVITY",SMALL,MUTED)
    else:
        d.rectangle((101,319,439,610),outline=GOLD,width=4)
        centered(d,367,"OBSERVED",FONT,GOLD)
        centered(d,436,"≠",BIG,INK)
        centered(d,510,"PROVEN",FONT,GOLD)
    centered(d,727,STAGES[idx][1],FONT,INK)
    centered(d,765,STAGES[idx][2],FONT,INK)
    centered(d,868,"THOMPSON 1980  /  EXPERIMENT, NOT ENDORSEMENT",SMALL,MUTED)
    fn=DEST/f"scene-{idx+1:02d}.png";im.save(fn,optimize=True);return fn
frames=[paint(i) for i in range(6)]
manifest=DEST/"sequence.ffconcat"
with manifest.open("w",encoding="utf-8") as out:
    out.write("ffconcat version 1.0\n")
    for f,dur in zip(frames,DURATIONS):
        out.write(f"file '{f.resolve()}'\nduration {dur}\n")
    out.write(f"file '{frames[-1].resolve()}'\n")
target=DEST/"the-face-that-turned-40s.mp4"
cmd=["ffmpeg","-nostdin","-y","-loglevel","error","-safe","0","-f","concat","-i",str(manifest),"-vf","fps=12,format=yuv420p","-c:v","libx264","-preset","medium","-crf","22","-movflags","+faststart","-t","40",str(target)]
subprocess.run(cmd,check=True)
(DEST/"poster.png").write_bytes(frames[0].read_bytes())
print(target)
