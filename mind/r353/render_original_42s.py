from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import subprocess
D=Path('/mnt/data/mind_r353'); D.mkdir(exist_ok=True)
W,H=1280,720
font='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
mono='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
scenes=[
('WHAT IF AN INSTRUCTION', 'CHANGES WHAT YOU NOTICE?', 'THE SCIENCE OF SUGGESTION'),
('SAY THE INK COLOR.', 'TRY NOT TO READ THE WORD.', 'THE STROOP TASK'),
('A SPOKEN SUGGESTION', 'CHANGED SOME RESPONSES.', '2006 · HIGHLY SUGGESTIBLE PARTICIPANTS'),
('INDUCTION AND SUGGESTION', 'WERE TESTED SEPARATELY.', '2025 · EMOTIONAL STROOP · N = 34'),
('NEITHER STUDY', 'TESTED A RETAIL AUDIO PRODUCT.', 'THE LIMIT OF THE EVIDENCE'),
('FOLLOW THE EXPERIMENT.', 'NOT THE PROMISE.', 'FINAL VESTIGE STUDIOS · MIND ARCHIVE'),
]
for i,(a,b,c) in enumerate(scenes):
 im=Image.new('RGB',(W,H),'#0b1216');draw=ImageDraw.Draw(im)
 gold='#dbb47c'; pale='#ede6d9'
 draw.rectangle((70,65,1210,655), outline='#8f7759', width=3)
 draw.line((155,195,1125,195), fill=gold, width=2)
 draw.line((155,550,1125,550), fill=gold, width=2)
 for idx,(text,y,font_size) in enumerate(((a,273,49),(b,362,43),(c,480,19))):
  f=ImageFont.truetype(font if idx<2 else mono,font_size)
  box=draw.textbbox((0,0),text,font=f)
  x=(W-(box[2]-box[0]))//2
  draw.text((x,y),text,font=f,fill=pale if idx<2 else gold)
 draw.text((160,102),f'FINAL VESTIGE  /  MIND RESEARCH      {i+1:02d} / 06',font=ImageFont.truetype(mono,18),fill=gold)
 draw.text((1000,590),'42 SECONDS',font=ImageFont.truetype(mono,18),fill=gold)
 im.save(D/f'frame_{i:02d}.png')
cmd=['ffmpeg','-hide_banner','-loglevel','error','-y']
for i in range(6): cmd+=['-loop','1','-framerate','12','-t','7','-i',str(D/f'frame_{i:02d}.png')]
streams=''.join(f'[{i}:v]' for i in range(6))
cmd+=['-filter_complex',f'{streams}concat=n=6:v=1:a=0[v]','-map','[v]','-r','12','-c:v','libx264','-preset','veryfast','-crf','25','-pix_fmt','yuv420p','-movflags','+faststart',str(D/'mind_r353_original_42s_proof.mp4')]
subprocess.run(cmd,check=True,timeout=120)
print('built',D/'mind_r353_original_42s_proof.mp4')
