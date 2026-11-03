#!/usr/bin/env python3
"""Reproducible original 40-second silent educational film for FV Mind R100.
Requires Pillow and FFmpeg; does not download or reuse merchant footage.
This render is for OFFLINE review only. No hosting or affiliate activation.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess, shutil, math, hashlib

ROOT = Path(__file__).resolve().parent
W, H, FPS = 540, 960, 12
STAGES = [
    (6, 'TWELVE MINUTES', ['A session length.', 'Not a clinical result.'], '01 / THE FORMAT'),
    (7, 'THE BIG PROMISE', ['The seller compares it', 'to an hour of meditation.'], '02 / THE CLAIM'),
    (7, 'WHAT WAS TESTED?', ['Independent EEG studies', 'show mixed findings.'], '03 / THE RESEARCH'),
    (7, 'NOT THIS PRODUCT', ['Those studies did not', 'test Zen12 itself.'], '04 / THE BOUNDARY'),
    (7, 'TRY FIRST', ['Twelve minutes of quiet', 'costs nothing to compare.'], '05 / THE PRACTICE'),
    (6, 'READ THE EVIDENCE', ['Choose a routine.', 'Keep the claims separate.'], '06 / THE DECISION'),
]
assert sum(s[0] for s in STAGES) == 40

def font(size, serif=False):
    p = ('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf' if serif
         else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    return ImageFont.truetype(p, size)

def text_center(d, y, words, size, color, serif=False):
    f=font(size,serif)
    bbox=d.textbbox((0,0), words, font=f)
    d.text(((W-(bbox[2]-bbox[0]))/2,y),words,font=f,fill=color)

def scene(i):
    duration,heading,body,tag=STAGES[i]
    im=Image.new('RGB',(W,H),'#0D1414')
    d=ImageDraw.Draw(im)
    for y in range(H):
        if y%3==0: d.line((0,y,W,y), fill=(14+int(y/100),19+int(y/120),19+int(y/120)), width=1)
    d.rectangle((25,25,W-25,H-25),outline='#544732',width=2)
    text_center(d,72,'FINAL VESTIGE / MIND ARCHIVE',18,'#CCB18A')
    d.ellipse((112,172,428,488),outline='#C7A66C',width=4)
    d.ellipse((156,216,384,444),outline='#625741',width=2)
    d.line((201,255,339,391),fill='#C7A66C',width=4)
    d.line((339,255,201,391),fill='#C7A66C',width=4)
    text_center(d,303,'12',72,'#F4EFE6',serif=True)
    text_center(d,406,'MINUTES',17,'#CCB18A')
    text_center(d,527,tag,17,'#C7A66C')
    if len(heading)>17:
        words=heading.split(' ')
        midpoint=max(1, len(words)//2)
        heads=[' '.join(words[:midpoint]),' '.join(words[midpoint:])]
    else: heads=[heading]
    y=580
    for line in heads:
        fs=33
        while fs>21 and d.textbbox((0,0),line,font=font(fs,True))[2]>W-55:fs-=1
        text_center(d,y,line,fs,'#F4EFE6',True);y+=46
    y=max(695,y+38)
    for line in body:text_center(d,y,line,24,'#E4D9C6');y+=43
    d.line((50,839,W-50,839),fill='#7B694D',width=2)
    text_center(d,863,'EVIDENCE BEFORE THE AUDIO',17,'#D1AD73')
    text_center(d,900,'No product endorsement. No guarantee.',13,'#BEB7AB')
    return im

def main():
    frames=[]
    for i,_ in enumerate(STAGES):
        filename=ROOT/f'scene-{i+1:02d}.png';scene(i).save(filename,optimize=True);frames.append(filename)
    # FFmpeg concat duration uses the demuxer timebase; 12fps enforces exactly 480 frames.
    concat=ROOT/'scenes.ffconcat'
    lines=['ffconcat version 1.0']
    for i,(seconds,*_) in enumerate(STAGES):
        lines += [f"file '{frames[i].name}'",f'duration {seconds}']
    lines.append(f"file '{frames[-1].name}'")
    concat.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    output=ROOT/'evidence-before-audio-r100-40s.mp4'
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-safe','0','-i',str(concat),
                    '-vf',f'fps={FPS},format=yuv420p','-frames:v',str(FPS*40),
                    '-an','-c:v','libx264','-preset','medium','-crf','25','-movflags','+faststart',str(output)],check=True)
    # Make a 3x2 storyboard contact sheet for visual QA.
    sheet=Image.new('RGB',(810,960),'#0A0B0B')
    for i,f in enumerate(frames):
        thumb=Image.open(f);thumb.thumbnail((270,480));sheet.paste(thumb,((i%3)*270,(i//3)*480))
    sheet.save(ROOT/'contact-sheet.png',optimize=True)
    scene(0).save(ROOT/'poster.png',optimize=True)
    probe=subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=width,height,r_frame_rate,nb_frames,codec_name',
                                   '-of','default=noprint_wrappers=1',str(output)],text=True)
    (ROOT/'ffprobe.txt').write_text(probe,encoding='utf-8')
    print('film',output,'sha256',hashlib.sha256(output.read_bytes()).hexdigest())
    print(probe)

if __name__=='__main__':main()
