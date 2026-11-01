"""Original Final Vestige Mind R49 silent 40s educational film.
Source-controlled design; uses Pillow/ffmpeg, no third-party imagery or sound.
Run: python render_r49.py. Output in the script's directory.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import subprocess, math
ROOT=Path(__file__).resolve().parent
W,H=540,960
BLACK=(10,12,13); GOLD=(224,188,123); CREAM=(246,237,218); SOFT=(190,192,183)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
F=lambda sz,face=FONT:ImageFont.truetype(face,sz)
def center(d,s,y,font,color=CREAM):
    b=d.textbbox((0,0),s,font=font);d.text(((W-b[2])/2,y),s,font=font,fill=color)
def lines(d,ss,y=635,size=39,step=55,color=CREAM):
    for j,s in enumerate(ss): center(d,s,y+j*step,F(size,BOLD if size<34 else SERIF),color)
def base(n):
    im=Image.new('RGB',(W,H),BLACK);d=ImageDraw.Draw(im)
    for x in range(0,W,12):
        shift=int(4*math.sin(x/26+n));d.line([(x,0),(x+shift,H)],fill=(14,17,18),width=2)
    d.line((42,110,498,110),fill=(91,79,61),width=2)
    center(d,'FINAL VESTIGE  /  MIND',57,F(17,BOLD),GOLD)
    d.line((42,855,498,855),fill=(91,79,61),width=2)
    center(d,f'EVIDENCE FILM    •    {n:02d} / 06',887,F(14),SOFT)
    return im,d

def scene1():
    im,d=base(1)
    d.rounded_rectangle((115,280,420,522),radius=12,outline=(105,94,75),width=3)
    d.line((146,420,391,420),fill=GOLD,width=5)
    d.rounded_rectangle((170,342,240,405),radius=20,outline=CREAM,width=3)
    d.ellipse((302,342,370,408),outline=GOLD,width=4)
    lines(d,['STARTING CAN','BE THE HARDEST','PART'],600,37,52)
    return im

def scene2():
    im,d=base(2)
    cx,cy=270,379
    for r,col in [(174,(66,61,52)),(128,(122,98,67)),(75,GOLD)]:
        d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=col,width=3)
    d.line((cx,cy,cx,260),fill=CREAM,width=6)
    d.line((cx,cy,335,419),fill=CREAM,width=6)
    d.ellipse((cx-10,cy-10,cx+10,cy+10),fill=GOLD)
    lines(d,['12 MINUTES','3 FREE FORMATS'],620,38,59)
    center(d,'SILENCE   /   SOUND   /   GUIDANCE',764,F(16),SOFT)
    return im

def scene3():
    im,d=base(3)
    for i,(s,c) in enumerate(zip(['GUIDED','MUSIC','NATURE','WHITE NOISE'],[GOLD,CREAM,GOLD,CREAM])):
        x=68+(i%2)*214;y=264+(i//2)*165
        d.rounded_rectangle((x,y,x+188,y+137),radius=14,fill=(24,27,27),outline=(88,79,64),width=2)
        d.arc((x+48,y+20,x+135,y+98),0,270,fill=c,width=5)
        d.text((x+18,y+104),s,font=F(16,BOLD),fill=c)
    lines(d,['4 STYLES','SELLER LISTED'],670,37,56)
    return im

def scene4():
    im,d=base(4)
    cards=[('05','CONSISTENT'),('08','CONTRARY'),('01','MIXED')]
    for j,(num,lab) in enumerate(cards):
        x=36+j*169
        d.rounded_rectangle((x,278,x+155,507),radius=12,fill=(23,26,27),outline=(91,82,66),width=2)
        d.text((x+27,332),num,font=F(54,BOLD),fill=GOLD if j!=1 else CREAM)
        d.text((x+15,425),lab,font=F(14,BOLD),fill=SOFT)
    lines(d,['14 EEG STUDIES'],625,41,55)
    center(d,'2023 REVIEW — NOT A ZEN12 TEST',746,F(17),GOLD)
    return im

def scene5():
    im,d=base(5)
    d.rounded_rectangle((105,225,436,575),radius=12,fill=(28,31,30),outline=(118,99,69),width=3)
    for i,txt in enumerate(['SILENCE','SOUND','GUIDANCE']):
        y=282+i*90
        d.rectangle((136,y,168,y+32),outline=GOLD,width=3)
        d.line((141,y+15,151,y+25,165,y+5),fill=CREAM,width=3)
        d.text((195,y),txt,font=F(24,BOLD),fill=CREAM)
    lines(d,['TRY BEFORE','YOU BUY'],638,41,58)
    return im

def scene6():
    im,d=base(6)
    for r in range(74,201,38):d.ellipse((270-r,372-r,270+r,372+r),outline=(92+r//5,76+r//8,57+r//12),width=2)
    d.line((270,372,270,219),fill=GOLD,width=7)
    d.line((270,372,350,429),fill=CREAM,width=7)
    lines(d,['TIME IS','MEASURABLE.'],624,38,51)
    center(d,'PROMISES NEED EVIDENCE.',767,F(21,BOLD),GOLD)
    return im

def main():
    frames=[scene1(),scene2(),scene3(),scene4(),scene5(),scene6()]
    times=[6,7,7,7,7,6]
    stills=ROOT/'stills';stills.mkdir(exist_ok=True)
    for j,im in enumerate(frames):im.save(stills/f'scene-{j+1:02d}.png',optimize=True)
    sheet=Image.new('RGB',(W*3,H*2),BLACK)
    for j,im in enumerate(frames):sheet.paste(im,((j%3)*W,(j//3)*H))
    sheet.save(ROOT/'contact-sheet.png',optimize=True)
    frames[-1].save(ROOT/'poster.png',optimize=True)
    segment_paths=[]
    for j,seconds in enumerate(times):
        segment=ROOT/f'part-{j+1:02d}.mp4'
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-loop','1','-framerate','12','-i',str(stills/f'scene-{j+1:02d}.png'),'-t',str(seconds),'-c:v','libx264','-preset','ultrafast','-crf','32','-pix_fmt','yuv420p','-r','12',str(segment)],check=True)
        segment_paths.append(segment)
    manifest=ROOT/'concat.txt';manifest.write_text(''.join("file '"+str(p)+"'\n" for p in segment_paths))
    output=ROOT/'time-not-proof-40s.mp4'
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(manifest),'-c','copy','-movflags','+faststart',str(output)],check=True)
    print(f'RENDERED {output} bytes={output.stat().st_size} seconds={sum(times)} scenes={len(frames)}')
if __name__=='__main__':main()
