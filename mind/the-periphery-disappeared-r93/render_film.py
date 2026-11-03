"""Original, schematic 40-second FV Troxler explainer; not a live experiment.
Needs Pillow and ffmpeg. Renders 540x960, 12fps, H.264. No remote assets.
"""
from PIL import Image, ImageDraw, ImageFont
import math, subprocess, pathlib, shutil

HERE = pathlib.Path(__file__).resolve().parent
FPS, W, H, N = 12, 540, 960, 480
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
SERIF = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
SM = ImageFont.truetype(FONT, 19)
MID = ImageFont.truetype(FONT, 25)
HD = ImageFont.truetype(SERIF, 43)
BIG = ImageFont.truetype(SERIF, 51)
GOLD, WHITE, MUTED, TURQ = '#d7ad72','#f5eee2','#c7bfb2','#80a9b1'
SCENES = [
    (0, 6, 'THE CIRCLE', 'IS STILL THERE.', 'Keep your eyes on the cross.'),
    (6, 13, 'A FIXED GAZE', 'IS NOT A CAMERA.', 'The stimulus is still on-screen.'),
    (13, 20, 'THE PERIPHERAL', 'IMAGE MAY FADE.', 'This is a visual metaphor, not a test.'),
    (20, 27, 'AN OBSERVATION', 'FROM 1804.', 'Modern studies measure it differently.'),
    (27, 34, 'TWO TRUE', 'DESCRIPTIONS.', 'The stimulus stayed. Experience changed.'),
    (34, 40, 'WHAT DID', 'YOU NOTICE?', 'Try our free static observation guide.'),
]

def centered(draw, xy, title, font, fill):
    x,y=xy
    bb=draw.textbbox((0,0),title,font=font)
    draw.text((x-(bb[2]-bb[0])/2, y),title,font=font,fill=fill)

def frame(num):
    t=num/FPS
    step=next(i for i,(start,end,*_) in enumerate(SCENES) if start <= t < end)
    _,_,h1,h2,cap=SCENES[step]
    im=Image.new('RGB',(W,H),(12,14,14)); d=ImageDraw.Draw(im)
    for y in range(H):
        shift=int(7*math.sin(y/H*math.pi))
        d.line((0,y,W,y),fill=(12+shift,14+shift,14+shift))
    d.rectangle((32,34,W-32,H-34),outline='#3e3b35',width=2)
    d.rectangle((58,51,174,54),fill=GOLD)
    d.text((58,70),'FINAL VESTIGE  /  MIND',font=SM,fill=GOLD)
    centered(d,(W/2,155),h1,BIG,WHITE)
    centered(d,(W/2,211),h2,HD,WHITE)
    d.line((58,289,W-58,289),fill='#625444',width=2)
    # Original static target, with a teaching fade on scene three only.
    alpha=1.0 if step!=2 else max(.05,1-(t-13)/7)
    edge=(int(112*alpha+20),int(153*alpha+20),int(159*alpha+20))
    if step in (0,1,2,5):
        d.ellipse((332,419,477,564),outline=edge,width=15)
        d.line((203,489,249,489),fill=GOLD,width=4)
        d.line((226,466,226,512),fill=GOLD,width=4)
        if step==1:
            d.ellipse((142,400,302,560),outline='#6d675d',width=2)
    elif step==3:
        d.text((60,417),'1804',font=ImageFont.truetype(SERIF,84),fill=GOLD)
        d.text((60,533),'Troxler described fading',font=MID,fill=WHITE)
        d.text((60,568),'during steady fixation.',font=MID,fill=WHITE)
    elif step==4:
        d.rounded_rectangle((49,395,491,474),radius=8,outline=TURQ,width=3)
        d.text((70,414),'DISPLAY:  dot still present',font=MID,fill=WHITE)
        d.rounded_rectangle((49,494,491,578),radius=8,outline=GOLD,width=3)
        d.text((70,516),'REPORT:  I could not see it',font=SM,fill=WHITE)
    d.line((58,674,W-58,674),fill='#625444',width=2)
    # Wrap the descriptive caption without inventing measured results.
    from textwrap import wrap
    lines=wrap(cap,width=38)
    for i,line in enumerate(lines):centered(d,(W/2,706+28*i),line,SM,MUTED)
    d.text((58,844),'ILLUSTRATIVE / NOT A SCIENTIFIC TRIAL',font=SM,fill=GOLD)
    d.text((58,887),f'{step+1:02d} / 06',font=MID,fill=WHITE)
    d.rounded_rectangle((140,895,480,902),radius=3,fill='#373531')
    d.rounded_rectangle((140,895,140+int(340*(num+1)/N),902),radius=3,fill=GOLD)
    return im

def main():
    out=HERE/'the-circle-that-did-not-leave-40s.mp4'
    cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}',
         '-framerate',str(FPS),'-i','-','-an','-c:v','libx264','-pix_fmt','yuv420p',
         '-preset','veryfast','-crf','23','-movflags','+faststart',str(out)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for i in range(N):
        proc.stdin.write(frame(i).tobytes())
    proc.stdin.close()
    if proc.wait():raise RuntimeError('ffmpeg encode failed')
    frame(0).save(HERE/'poster.png',optimize=True)
    return out
if __name__=='__main__':print(main())
