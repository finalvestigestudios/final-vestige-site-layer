#!/usr/bin/env python3
"""Original silent research short. No merchant audio or original study footage.
Local OFFLINE review asset only. Requires Pillow, ffmpeg and ffprobe."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math, subprocess, hashlib, shutil
ROOT=Path(__file__).resolve().parent
W,H,FPS=540,960,12
DUR=[6,7,7,7,7,6]
LINES=[
('ONE VOICE','IN A CROWDED ROOM','You try to follow one voice.'),
('THE INTERRUPTION','YOUR NAME','Another voice sometimes breaks through.'),
('THE SURPRISE','MOST DID NOT','Most listeners missed it in a lab task.'),
('THE QUESTION','WHAT CHANGED?','Attention is selective, not supernatural.'),
('THE OFFER FORMAT','TWELVE MINUTES','Zen12 advertises short audio in four styles.'),
('THE EVIDENCE','TIME IS NOT PROOF','Outcome claims require independent evidence.')
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
    for channel in range(2):
        pts=[]
        for x in range(20,W-20,3):
            t=(x-20)/W
            amp=(34 if channel==0 else 25)+(20*math.cos(t*7+idx))
            y=340+channel*120+math.sin(t*40+(idx*0.6)+(channel*1.5))*amp
            pts.append((x,y))
        d.line(pts,fill=GOLD if idx in (1,4,5) and channel==0 else '#45514a',width=3)
    for i in range(12):
        r=55+i*23
        d.arc((W/2-r,405-r,W/2+r,405+r),200+idx*10,340+idx*5,fill='#202e2b',width=1)

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
    mp4=ROOT/'the-name-in-the-other-ear-40s.mp4'
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y',*inputs,'-filter_complex',filtergraph,'-map','[out]','-c:v','libx264','-preset','fast','-crf','28','-r',str(FPS),'-pix_fmt','yuv420p','-movflags','+faststart',str(mp4)]
    subprocess.run(cmd,check=True)
    probe=subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames,avg_frame_rate,width,height,codec_name:format=duration,size','-of','default=noprint_wrappers=1',str(mp4)],text=True)
    (ROOT/'ffprobe.txt').write_text(probe)
    (ROOT/'sha256.txt').write_text('video sha256 '+hashlib.sha256(mp4.read_bytes()).hexdigest()+'\n')
    assert 'nb_frames=480' in probe,probe
    assert 'duration=40.000000' in probe,probe
    print(probe)
if __name__=='__main__':main()
