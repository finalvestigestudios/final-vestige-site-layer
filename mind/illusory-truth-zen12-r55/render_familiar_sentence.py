#!/usr/bin/env python3
"""Reproducible original 40s illusory-truth motion graphic; no vendor imagery/sounds."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math, subprocess, shutil, hashlib, os

OUT = Path(__file__).resolve().parent
W, H, FPS, SECONDS = 540, 960, 12, 40
INK = (244, 239, 230)
SUB = (211, 203, 190)
GOLD = (198, 170, 113)
GROUND = (10, 13, 13)
PANEL = (22, 26, 24)
SCENES = [
    (0, 6, 'A SENTENCE', ['A claim appears once.', 'You read it and move on.'], '01 · THE ENCOUNTER'),
    (6, 13, 'IT RETURNS', ['Two weeks later, it looks familiar.', 'But the evidence has not changed.'], '02 · REPETITION'),
    (13, 20, 'FEELS TRUER', ['Repeated claims may gain', 'in perceived truth ratings.'], '03 · THE EXPERIMENT'),
    (20, 27, 'NOT PROOF', ['Familiar is not the same', 'as independently verified.'], '04 · THE DISTINCTION'),
    (27, 34, 'CHECK FIRST', ['Ask what supports the claim.', 'Follow the original source.'], '05 · THE PRACTICE'),
    (34, 40, 'READ THE EVIDENCE', ['No product outcome demonstrated.', 'The offer remains disabled.'], '06 · THE LIMIT'),
]

def face_font(size, serif=False):
    paths = ([
        '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',
        '/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf'
    ] if serif else [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf'
    ])
    for p in paths:
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

SERIF = face_font(47, True)
TEXT = face_font(25)
SMALL = face_font(17)
TINY = face_font(13)

def center(draw, xy, text, font, fill, spacing=9):
    draw.multiline_text(xy, text, font=font, fill=fill, spacing=spacing, anchor='mm', align='center', stroke_width=0)

def frame(idx):
    sec = idx / FPS
    scene_index = next(i for i, (start, end, *_rest) in enumerate(SCENES) if start <= sec < end)
    start, end, heading, lines, tag = SCENES[scene_index]
    phase = (sec-start)/(end-start)
    img = Image.new('RGB', (W,H), GROUND)
    d=ImageDraw.Draw(img)
    # Quiet architectural grid; no strobe, external media or hidden experiment footage.
    for y in range(0,H,48): d.line((0,y,W,y), fill=(18,22,21), width=1)
    for x in range(0,W,48): d.line((x,0,x,H), fill=(18,22,21), width=1)
    d.rectangle((30,29,W-30,H-29), outline=(70,66,55), width=2)
    d.rectangle((30,29,W-30,104), fill=(20,24,22))
    center(d,(W//2,67),'FINAL VESTIGE  /  MIND & PERCEPTION',SMALL,GOLD)
    # Slow circular motif and time marker; no flash or abrupt strobe, without rapid flashing.
    drift = int(7*math.sin(2*math.pi*phase))
    d.ellipse((W//2-136-drift,180,W//2+136+drift,452),outline=(72,69,59),width=3)
    d.ellipse((W//2-99,217,W//2+99,415),outline=GOLD,width=3)
    if scene_index in (0,5):
        d.arc((W//2-67,249,W//2+67,383),-90,-90+int(360*phase),fill=INK,width=9)
        center(d,(W//2,316),'12',face_font(54,True),INK)
    elif scene_index==1:
        # Repeated parallel marks represent exposure, not real experiment footage.
        for k in range(3):
            x=170+k*100
            d.rectangle((x-24,284,x+24,332),outline=GOLD if k==2 else INK,width=3)
        d.line((151,350,389,350),fill=(72,69,59),width=3)
    elif scene_index==2:
        d.line((206,268,335,370),fill=INK,width=7)
        d.line((335,268,206,370),fill=INK,width=7)
    elif scene_index==3:
        for j,(y,c) in enumerate([(284,GOLD),(317,INK),(350,GOLD)]):
            d.line((193,y,349,y),fill=c,width=5)
    else:
        d.polygon([(270,245),(326,345),(215,345)],outline=GOLD,width=4)
        center(d,(270,316),'?',face_font(55,True),INK)
    d.rectangle((51,495,W-51,508),fill=(47,45,41))
    d.rectangle((51,495,51+int((W-102)*phase),508),fill=GOLD)
    center(d,(W//2,562),tag,SMALL,GOLD)
    head_size = 47
    while d.textbbox((0,0),heading,font=face_font(head_size, True))[2] > W-108 and head_size > 24:
        head_size -= 1
    center(d,(W//2,634),heading,face_font(head_size,True),INK)
    center(d,(W//2,733),'\n'.join(lines),TEXT,SUB,spacing=18)
    # meaningful disclosure and media limitations persist throughout
    center(d,(W//2,880),'ORIGINAL EDUCATIONAL EXPLAINER · NOT PRODUCT TEST',TINY,GOLD)
    d.rectangle((51,923,W-51,926),fill=(57,56,50))
    d.rectangle((51,923,51+int((W-102)*(idx+1)/(SECONDS*FPS)),926),fill=GOLD)
    return img

def main():
    poster=frame(0)
    poster.save(OUT/'film-poster.png',optimize=True)
    if shutil.which('ffmpeg') is None: raise SystemExit('ffmpeg required')
    dest=OUT/'familiar-sentence-40s.mp4'
    proc=subprocess.Popen([
      'ffmpeg','-y','-hide_banner','-loglevel','error','-f','rawvideo','-pixel_format','rgb24',
      '-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','-','-an','-c:v','libx264',
      '-pix_fmt','yuv420p','-preset','fast','-crf','26','-movflags','+faststart',str(dest)
    ],stdin=subprocess.PIPE)
    for i in range(FPS*SECONDS):
        proc.stdin.write(frame(i).tobytes())
    proc.stdin.close()
    if proc.wait()!=0: raise SystemExit('ffmpeg failed')
    print('Rendered',dest,'bytes',dest.stat().st_size,'sha256',hashlib.sha256(dest.read_bytes()).hexdigest())

if __name__=='__main__': main()
