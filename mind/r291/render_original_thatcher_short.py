"""Render the ORIGINAL seven-scene, silent ~42s Mind/Perception explainer.

Requires Pillow and ffmpeg; outputs MP4, poster, VTT, transcript and 7 scene PNGs.
No third-party photographs, voice clips, music, paid packages, or merchant images.
Only local research visualization; NOT automatically published to WordPress.
Run: python mind/r291/render_original_thatcher_short.py
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import subprocess

OUT = Path(__file__).resolve().parent / "generated"
OUT.mkdir(parents=True, exist_ok=True)
W, H = 960, 540
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
TITLE = ImageFont.truetype(SERIF, 37)
SUB = ImageFont.truetype(SANS, 22)
SMALL = ImageFont.truetype(SANS, 16)
GOLD = (223, 190, 139)
WHITE = (242, 238, 227)
LIGHT = (199, 207, 203)
scenes = [
    ("THE FACE THAT CHANGED", "Without changing a single pixel,", "what happens when a portrait is turned?"),
    ("1980 · PETER THOMPSON", "A portrait with inverted eyes and mouth", "looked strange when the face was upright."),
    ("ROTATE THE WHOLE IMAGE", "Upside down, many observers find", "the altered features less disturbing."),
    ("NOT A UNIVERSAL RULE", "The strength depends on the face,", "the edits, and what observers are asked."),
    ("EVIDENCE HAS LIMITS", "Face perception is not proof that", "a commercial audio changes your mind."),
    ("TRY YOUR OWN RECORD", "Sketch, rotate, and write down", "what changed in your judgment."),
    ("FOLLOW THE SOURCE TRAIL", "Read the study. Ask what it tested.", "Final Vestige Studios · Mind & Perception"),
]

def centered(d, txt, y, font, color):
    bb = d.textbbox((0, 0), txt, font=font)
    d.text(((W-(bb[2]-bb[0]))/2, y), txt, fill=color, font=font)

def face(d, cx, cy, scale=1, flip=False):
    R = int(80*scale)
    cx, cy = int(cx), int(cy)
    d.ellipse((cx-R, cy-R*1.27, cx+R, cy+R*1.27), outline=GOLD, width=3)
    off = int(24*scale)
    eyeY = cy + int(27*scale) if flip else cy-int(27*scale)
    mouthY = cy - int(46*scale) if flip else cy+int(46*scale)
    for ex in [cx-off, cx+off]:
        d.arc((ex-15,eyeY-8,ex+15,eyeY+8),0 if flip else 180,180 if flip else 360,fill=GOLD,width=3)
    d.arc((cx-33,mouthY-10,cx+33,mouthY+14),180 if flip else 0,360 if flip else 180,fill=GOLD,width=3)
    d.line((cx,cy-12,cx-6,cy+18,cx+8,cy+18),fill=GOLD,width=3)

frames = []
for i, (headline, line1, line2) in enumerate(scenes):
    im = Image.new("RGB", (W, H))
    pix = im.load()
    for y in range(H):
        for x in range(W):
            glow = int(19*(x/W)*(1-y/H))
            pix[x, y] = (13+glow, 21+glow, 23+glow)
    d = ImageDraw.Draw(im)
    d.rectangle((30, 26, W-30, H-30), outline=(93,102,98), width=2)
    d.text((58,46),"FINAL VESTIGE  /  OBSERVER LABORATORY",font=SMALL,fill=GOLD)
    d.text((W-102,46),f"{i+1:02d} / 07",font=SMALL,fill=LIGHT)
    centered(d,headline,135,TITLE,WHITE)
    centered(d,line1,214,SUB,LIGHT)
    centered(d,line2,249,SUB,LIGHT)
    if i in (0,1,2,3):
        face(d,W//2,382,.65,flip=(i==2))
    elif i in (4,5):
        d.line((360,395,600,395),fill=GOLD,width=3)
        d.ellipse((464,351,496,383),outline=GOLD,width=3)
    else:
        d.rectangle((348,349,613,400),outline=GOLD,width=2)
        centered(d,"THE SOURCE IS THE STORY",360,SMALL,GOLD)
    d.text((58,H-58),"ORIGINAL STUDIO GRAPHICS · NOT EXPERIMENTAL STIMULI",font=SMALL,fill=LIGHT)
    path=OUT/f"scene_{i+1:02d}.png"
    im.save(path,optimize=True)
    frames.append(path)

(OUT/"poster.png").write_bytes(frames[0].read_bytes())
vtt=["WEBVTT",""]
trans=["# The Face That Changed — original 42-second silent explainer","","Research graphic, NOT the original Thatcher experimental stimulus; no product effectiveness claim.",""]
for i,(headline,l1,l2) in enumerate(scenes):
    start=i*6
    end=(i+1)*6
    vtt.extend([str(i+1),f"00:00:{start:02d}.000 --> 00:00:{end:02d}.000",headline,l1+" "+l2,""])
    trans.append(f"**{start:02d}–{end:02d}s | {headline}.** {l1} {l2}")
(OUT/"captions.vtt").write_text("\n".join(vtt),encoding="utf-8")
(OUT/"transcript.md").write_text("\n\n".join(trans)+"\n",encoding="utf-8")
concat=[]
for p in frames:
    concat.extend([f"file '{p}'","duration 6"])
concat.append(f"file '{frames[-1]}'")
(OUT/"concat.txt").write_text("\n".join(concat)+"\n")
subprocess.run(["ffmpeg","-y","-loglevel","error","-safe","0","-f","concat","-i",str(OUT/"concat.txt"),"-r","12","-c:v","libx264","-pix_fmt","yuv420p","-movflags","+faststart","-t","42",str(OUT/"thatcher-original-42s.mp4")],check=True)
print(f"Rendered silent optional video at {OUT/'thatcher-original-42s.mp4'}. Never autoplay.")
