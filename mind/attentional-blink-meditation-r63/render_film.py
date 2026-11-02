#!/usr/bin/env python3
"""Original 40s educational research film, not a validated RSVP experiment.
Local OFFLINE review asset only. Requires Pillow, ffmpeg and ffprobe."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math, subprocess, hashlib, shutil
ROOT=Path(__file__).resolve().parent
W,H,FPS=540,960,12
DUR=[6,7,7,7,7,6]
LINES=[
('THE TWO TARGETS','ONE THEN TWO','A stream can contain both target numbers.'),
('THE BLINK','A SHORT GAP','The later target can be harder to report.'),
('THE EXCEPTION','LAG ONE','Immediate targets can sometimes be spared.'),
('THE RETREAT','THREE MONTHS','Researchers studied intensive meditation training.'),
('THE CLAIM','TWELVE MINUTES','A sales format is not a controlled experiment.'),
('THE METHOD','READ THE SOURCE','Ask what was actually measured.')
]
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
SANS='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
GOLD='#c7a66c';CREAM='#f4efe6';MUTED='#bdb4a6';DARK='#090d0d'

def font(path,size):return ImageFont.truetype(path,size)

def fit(draw,words,maxwidth,maxsize=48,minimum=21,face=SERIF):
    for size in range(maxsize,minimum-1,-1):
        f=font(face,size)
        if draw.textbbox((0,0),words,font=f)[2] <= maxwidth:return f
    return font(face,minimum)

def wave(d,idx):
    # Original schematic rapid-visual-stream art; intentionally not timed like a lab task.
    chars=['A','K','7','R','G','3','M']
    for j,ch in enumerate(chars):
        x=36+j*68
        d.rounded_rectangle((x,300,x+55,408),radius=9,outline=GOLD if ch in ('7','3') else '#3c5149',width=2)
        d.text((x+10,331),ch,font=font(SANS,36),fill=GOLD if ch in ('7','3') else CREAM)
    d.line([(36,450),(500,450)],fill='#45514a',width=2)
    d.rectangle((36,449,36+(464*(idx+1)/6),453),fill=GOLD)
    d.text((38,475),'TARGETS DISPLAYED  /  REPORT NOT ASSURED',font=font(SANS,13),fill=MUTED)

def scene(idx):
    im=Image.new('RGB',(W,H),DARK);d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,12),fill=GOLD)
    d.text((34,38),'FINAL VESTIGE  /  MIND & PERCEPTION',font=font(SANS,13),fill=GOLD)
    d.text((34,92),f'FIELD NOTE  /  {idx+1:02d} OF 06',font=font(SANS,16),fill=MUTED)
    wave(d,idx)
    title,big,desc=LINES[idx]
    d.text((34,578),title,font=font(SANS,16),fill=GOLD)
    f=fit(d,big,W-68,48)
    d.text((34,625),big,font=f,fill=CREAM)
    # wrap descriptive line
    words=desc.split();raw=[];line=''
    for word in words:
        cand=(line+' '+word).strip()
        if d.textbbox((0,0),cand,font=font(SANS,19))[2]>W-75 and line:
            raw.append(line);line=word
        else:line=cand
    raw.append(line)
    for j,row in enumerate(raw):d.text((34,719+j*31),row,font=font(SANS,19),fill=MUTED)
    d.rectangle((34,863,W-34,867),fill='#36413d')
    d.rectangle((34,863,34+(W-68)*(idx+1)/6,867),fill=GOLD)
    d.text((34,895),'EDUCATIONAL CONCEPT  ·  NOT PRODUCT EVIDENCE',font=font(SANS,12),fill=MUTED)
    return im

def main():
    framepaths=[]
    for i in range(6):
        p=ROOT/f'scene-{i+1:02d}.png';scene(i).save(p,optimize=True);framepaths.append(p)
    # An exact frame count per scene avoids VFR concat timing ambiguity.
    inputs=[]
    for i,(p,duration) in enumerate(zip(framepaths,DUR)):
        inputs+=['-loop','1','-framerate',str(FPS),'-t',str(duration),'-i',str(p)]
    filtergraph=''.join(f'[{i}:v]setsar=1,format=yuv420p[v{i}];' for i in range(6))
    filtergraph+=''.join(f'[v{i}]' for i in range(6))+'concat=n=6:v=1:a=0[out]'
    mp4=ROOT/'the-second-number-40s.mp4'
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y',*inputs,'-filter_complex',filtergraph,'-map','[out]','-c:v','libx264','-preset','fast','-crf','28','-r',str(FPS),'-pix_fmt','yuv420p','-movflags','+faststart',str(mp4)]
    subprocess.run(cmd,check=True)
    probe=subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames,avg_frame_rate,width,height,codec_name:format=duration,size','-of','default=noprint_wrappers=1',str(mp4)],text=True)
    (ROOT/'ffprobe.txt').write_text(probe)
    (ROOT/'sha256.txt').write_text('video sha256 '+hashlib.sha256(mp4.read_bytes()).hexdigest()+'\n')
    assert 'nb_frames=480' in probe,probe
    assert 'duration=40.000000' in probe,probe
    print(probe)
if __name__=='__main__':main()
