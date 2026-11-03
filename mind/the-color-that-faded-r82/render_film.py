"""Original silent 40s educational film for Final Vestige Mind R82.
Safe media: explanatory color-fade animation is NOT an experimental response.
Render: python render_film.py. Requires Pillow and ffmpeg.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, subprocess

OUT=Path(__file__).resolve().parent
W,H,FPS,SECONDS=540,960,12,40
S=(0,6,12,20,26,33,40)
TITLES=[
    ("THE COLOR", "WAS ALWAYS THERE", "FINAL VESTIGE / FIELD FILM 082"),
    ("THE IMAGE", "DOES NOT MOVE", "A quiet point. A soft patch."),
    ("SOME VIEWERS", "NOTICE FADING", "The film illustrates it; this is not a test."),
    ("LOOK AGAIN", "THE PATCH REMAINS", "The source can be unchanged."),
    ("THE EYE", "IS NOT STILL", "Adaptation. Drift. Microsaccades."),
    ("OBSERVE FIRST", "INFER SECOND", "Follow the evidence. Not the promise."),
]
BG=(11,15,15)
INK=(243,235,218)
GOLD=(207,159,98)
TEAL=(127,205,196)
DIM=(164,161,153)
font_candidates=[
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
]
font_bold_candidates=[
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
]
for file in font_candidates:
    if Path(file).exists(): normal=file;break
for file in font_bold_candidates:
    if Path(file).exists(): bold=file;break
f_label=ImageFont.truetype(bold,19)
f_big=ImageFont.truetype(bold,36)
f_mid=ImageFont.truetype(normal,21)
f_small=ImageFont.truetype(normal,17)

def text_center(draw,y,value,font,fill):
    box=draw.textbbox((0,0),value,font=font)
    x=(W-(box[2]-box[0]))/2
    draw.text((x,y),value,font=font,fill=fill)

def render_frame(frame):
    t=frame/FPS
    scene=max(i for i in range(6) if t>=S[i])
    q=(t-S[scene])/(S[scene+1]-S[scene])
    im=Image.new('RGB',(W,H),BG)
    dr=ImageDraw.Draw(im)
    # Original hand-drawn documentary border and quiet vignette.
    for y in range(H):
        if y%3==0:
            c=int(10+6*math.sin(y/H*math.pi))
            dr.line((0,y,W,y),fill=(c,c+4,c+3))
    dr.rounded_rectangle((28,28,W-28,H-28),radius=12,outline=(65,58,45),width=2)
    dr.rectangle((30,29,30+int((W-60)*t/SECONDS),32),fill=GOLD)
    dr.text((42,51),'FV / MIND & PERCEPTION',font=f_label,fill=GOLD)
    dr.text((42,82),'SILENT FIELD FILM   /   40 SEC',font=f_small,fill=DIM)
    # A nearly static fixation diagram. Nothing is neurologically measured.
    cx,cy=W/2,H*.41
    left=(cx-78,cy)
    right=(cx+113,cy)
    dr.ellipse((left[0]-7,left[1]-7,left[0]+7,left[1]+7),fill=INK)
    dr.ellipse((left[0]-19,left[1]-19,left[0]+19,left[1]+19),outline=(65,70,65),width=1)
    # Explanation-only fade animation in scene 2, restoration in scene 3.
    intensity=1
    if scene==2: intensity=max(.11,1-.88*min(1,q*1.25))
    if scene==3: intensity=.12+.88*min(1,q*2)
    if scene==4: intensity=.85
    phase=.35+0.05*math.sin(t*.8)
    layer=Image.new('RGBA',(W,H),(0,0,0,0))
    ld=ImageDraw.Draw(layer)
    for rad in range(85,13,-3):
        alpha=int(max(0, (85-rad)/75)* (10+155*intensity))
        ld.ellipse((right[0]-rad,right[1]-rad,right[0]+rad,right[1]+rad),fill=(*TEAL,max(0,min(255,alpha))))
    layer=layer.filter(ImageFilter.GaussianBlur(10))
    im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
    dr=ImageDraw.Draw(im)
    if scene==4:
        # Small stylized movement marks, not quantitative eye tracking.
        off=8*math.sin(t*5)
        dr.arc((left[0]-32+off,left[1]-32,left[0]+32+off,left[1]+32),210,325,fill=GOLD,width=3)
        dr.line((left[0]+26+off,left[1]-17,left[0]+34+off,left[1]-11),fill=GOLD,width=3)
    dr.line((44,620,W-44,620),fill=(77,68,52),width=2)
    first,second,small=TITLES[scene]
    text_center(dr,659,first,f_big,INK)
    text_center(dr,721,second,f_big,INK)
    text_center(dr,815,small,f_mid,(212,197,173))
    dr.text((43,H-92),f'SCENE {scene+1:02d} / 06',font=f_label,fill=GOLD)
    dr.text((W-93,H-92),f'{int(t):02d}s',font=f_label,fill=DIM)
    return im

def main():
    video=OUT/'the-color-was-always-there-40s.mp4'
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','25','-pix_fmt','yuv420p','-movflags','+faststart',str(video)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    pics=[]
    try:
        for k in range(FPS*SECONDS):
            im=render_frame(k)
            if k in [0,7*FPS,15*FPS,23*FPS,29*FPS,37*FPS]: pics.append(im.copy())
            proc.stdin.write(im.tobytes())
        proc.stdin.close()
        if proc.wait()!=0: raise RuntimeError('ffmpeg failed')
    except BaseException:
        proc.kill();proc.wait();raise
    poster=render_frame(0)
    poster.save(OUT/'poster.png',optimize=True)
    contact=Image.new('RGB',(3*270,2*480),BG)
    for i,im in enumerate(pics): contact.paste(im.resize((270,480)),((i%3)*270,(i//3)*480))
    contact.save(OUT/'contact-sheet.png',optimize=True)
    print('Rendered',video.name,'frames',FPS*SECONDS,'poster', (OUT/'poster.png').name)

if __name__=='__main__': main()
