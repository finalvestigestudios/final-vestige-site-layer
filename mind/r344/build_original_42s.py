#!/usr/bin/env python3
"""Original Final Vestige Mind R344 review film: 6 silent caption-compatible 7-second scenes.
No network resources or brand-owned media. Local review output only; not for deployment.
Usage: python mind_r344_original_42s.py
Requires Pillow and ffmpeg. Never activate affiliate links or autoplay.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math, subprocess, json

OUT=Path(__file__).parent
W,H=1280,720
BG=(10,12,12); GOLD=(190,152,99); IVORY=(243,235,220); SUB=(181,173,156)
FONT='/usr/share/fonts/truetype/lato/Lato-Medium.ttf'
BOLD='/usr/share/fonts/truetype/lato/Lato-Bold.ttf'
HEADS=[
 ('THE EXPLANATION TRAP','A scientific story can sound complete','before it is proven.'),
 ('TWO TRUE FACTS','Sound has frequencies.','Brains show rhythms.'),
 ('THE MISSING LINK','But those facts do not establish','what a particular recording does.'),
 ('THE EVIDENCE','Fourteen studies.','Inconsistent EEG results.'),
 ('THE FAIR QUESTION','Where is a controlled test','of this actual product and outcome?'),
 ('MAKE THE EVIDENCE THE EXPERIENCE','Try the free exercise.','Choose without pressure.')
]

def font(size,bold=False): return ImageFont.truetype(BOLD if bold else FONT,size)
def center(draw,xy,text,f,fill,max_width=1050):
    size=draw.textbbox((0,0),text,font=f); width=size[2]-size[0]
    draw.text((xy[0]-width/2,xy[1]),text,font=f,fill=fill)

def scene(i):
    img=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(img)
    # Original procedural topographic wave, no imported imagery.
    for j in range(17):
        y0=120+j*17
        points=[]
        for x in range(0,W+8,8):
            y=y0+12*math.sin(x/76+j*.49)+5*math.cos(x/27+j*.83)
            points.append((x,int(y)))
        opacity=int(20+14*j/17)
        d.line(points,fill=(opacity+11,opacity+12,opacity+8),width=1)
    d.line((95,88,1185,88),fill=GOLD,width=2)
    d.rectangle((95,89,190,94),fill=GOLD)
    d.text((96,46),'FINAL VESTIGE / MIND & PERCEPTION',font=font(21,True),fill=IVORY)
    title,a,b=HEADS[i]
    center(d,(W/2,248),title,font(24,True),GOLD)
    center(d,(W/2,339),a,font(53,True),IVORY)
    center(d,(W/2,415),b,font(45),IVORY)
    if i==2:
        d.line((350,540,565,540),fill=GOLD,width=4)
        d.line((715,540,930,540),fill=GOLD,width=4)
        d.ellipse((608,511,672,575),outline=GOLD,width=3)
        center(d,(640,510),'?',font(47,True),GOLD)
    else:
        d.line((95,590,1185,590),fill=(53,50,45),width=2)
    d.text((95,628),'EVIDENCE BEFORE CLAIMS',font=font(19,True),fill=SUB)
    d.text((1130,628),f'{i+1:02d} / 06',font=font(19),fill=GOLD)
    p=OUT/f'mind_r344_frame_{i+1:02d}.png'; img.save(p,optimize=True)
    return p

def main():
    frames=[scene(i) for i in range(6)]
    concat=OUT/'mind_r344_concat.txt'
    concat.write_text(''.join(f"file '{p.as_posix()}'\nduration 7\n" for p in frames)+f"file '{frames[-1].as_posix()}'\n")
    output=OUT/'mind_r344_original_42s.mp4'
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-safe','0','-f','concat','-i',str(concat),'-vf','tpad=stop_mode=clone:stop_duration=1','-frames:v','504','-r','12','-c:v','libx264','-preset','veryfast','-pix_fmt','yuv420p','-movflags','+faststart','-an',str(output)]
    subprocess.run(cmd,check=True)
    probe=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration,size','-of','json',str(output)],check=True,capture_output=True,text=True)
    data=json.loads(probe.stdout)['format']
    assert abs(float(data['duration'])-42)<.02,data
    print(json.dumps({'file':str(output),'duration_seconds':float(data['duration']),'size_bytes':int(data['size']),'resolution':f'{W}x{H}','audio':False,'source_frames':6,'mode':'unpublished local review'}))
if __name__=='__main__':main()
