"""R476: Build original 42-second silent captioned research-only preview.
No licensed music, third-party photographs, actual McGurk stimulus or vendor claims.
Requires Pillow and ffmpeg/ffprobe. Output stays local, NOT a published/hosted video.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import math, subprocess

ROOT = Path(__file__).resolve().parent
W,H=1280,720
TEXTS=[
 ('TWO SIGNALS', 'You hear a syllable. You watch the lips.\nThey seem to agree.'),
 ('A MISMATCH', 'But what if the audio and the face\ncame from two different recordings?'),
 ('A THIRD SOUND', 'In the McGurk experiment, some listeners\nreport a third sound.'),
 ('A SINCERE REPORT', 'Your report can be sincere. It can still\ndiffer from the original track.'),
 ('FINDING ≠ PROMISE', 'That is a perception finding —\nnot proof of a meditation product.'),
 ('READ THE EVIDENCE', 'Check the evidence. Compare formats.\nDecide whether you need to buy anything.'),
]

def font(size, serif=False):
    path='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf' if serif else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    return ImageFont.truetype(path,size)

y=np.linspace(0,1,H,dtype=np.float32)[:,None,None]
x=np.linspace(0,1,W,dtype=np.float32)[None,:,None]
base=np.zeros((H,W,3),dtype=np.float32)
base[:,:,0]=11+8*x[:,:,0]+5*y[:,:,0]
base[:,:,1]=19+18*x[:,:,0]+4*y[:,:,0]
base[:,:,2]=30+26*x[:,:,0]+5*y[:,:,0]
for idx,(heading,caption) in enumerate(TEXTS):
    im=Image.fromarray(base.clip(0,255).astype('uint8'),'RGB').convert('RGBA')
    layer=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(layer)
    # Soft geometric studio halo and gold concentric waves: all original artwork.
    for j in range(8):
        r=90+j*31
        d.ellipse((W//2-r,170-r*.25,W//2+r,170+r*.25),outline=(211,177,109,max(10,65-j*8)),width=2)
    # One line is acoustic; other line stands for a lip-motion record, never simulated speech.
    for channel,offset in enumerate((0,25)):
        pts=[]
        for px in range(85,1195,5):
            p=(px-85)/(1195-85)
            wave=math.sin(2*math.pi*(4*p+idx*.13+channel*.22)) * (17 + 7*math.sin(math.pi*p))
            pts.append((px,219+wave+offset))
        d.line(pts,fill=(229,193,116,205 if channel==0 else 135),width=3)
    d.line([(85,268),(1195,268)],fill=(190,195,197,65),width=1)
    d.text((86,48),'FINAL VESTIGE STUDIOS  /  MIND & PERCEPTION',font=font(21),fill=(214,193,148,255))
    d.text((W//2,332),heading,font=font(55,True),anchor='mm',fill=(244,228,191,255),stroke_width=0)
    d.multiline_text((W//2,425),caption,font=font(35),anchor='ma',align='center',spacing=17,fill=(235,239,238,255))
    d.text((86,652),'SOURCE BEFORE STORY  ·  AN OPTIONAL RESEARCH FILM',font=font(18),fill=(174,190,199,255))
    d.text((1195,652),f'{idx+1:02d}/06',font=font(19),anchor='ra',fill=(221,189,121,255))
    out=Image.alpha_composite(im,layer).convert('RGB');out.save(ROOT/f'card_{idx+1:02d}.png',optimize=True)

args=['ffmpeg','-hide_banner','-loglevel','error','-y']
for idx in range(6): args+=['-loop','1','-framerate','24','-t','7.5','-i',str(ROOT/f'card_{idx+1:02d}.png')]
filt=[]
for idx in range(6): filt.append(f'[{idx}:v]format=yuv420p,settb=AVTB,setsar=1[v{idx}]')
prev='v0'
for idx in range(1,6):
    nxt=f'x{idx}';off=round(idx*6.9,2)
    filt.append(f'[{prev}][v{idx}]xfade=transition=fade:duration=0.6:offset={off}[{nxt}]');prev=nxt
out=ROOT/'ZEN12_MCGURK_OPTIONAL_42S_SILENT_PREVIEW.mp4'
args+=['-filter_complex',';'.join(filt),'-map',f'[{prev}]','-an','-r','24','-c:v','libx264','-preset','medium','-crf','30','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
print('rendering',out)
subprocess.run(args,check=True)
subprocess.run(['ffprobe','-v','error','-show_entries','format=duration,size','-of','default=noprint_wrappers=1',str(out)],check=True)
