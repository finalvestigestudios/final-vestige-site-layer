#!/usr/bin/env python3
"""Original silent 42-second editorial film proof; no external footage or audio.
Requires Pillow and ffmpeg. Run: python mind/r343/build_original_42s.py
For local review only. MP4 is intentionally not committed/embedded/published.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess, math

ROOT = Path(__file__).resolve().parent
FONT = '/usr/share/fonts/truetype/lato/Lato-Regular.ttf'
FONT_BOLD = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'
assert Path(FONT).exists() and Path(FONT_BOLD).exists(), 'Adjust font paths for your system'
W, H = 1280, 720
scenes = [
 ('01 / THE CONFLICT', 'A familiar word can interfere\nwith naming its ink color.', 'An everyday attention experiment'),
 ('02 / THE SUGGESTION', 'One instruction changed\na laboratory response.', 'Only in selected participants and conditions'),
 ('03 / THE LIMIT', 'It did not test a\ncommercial meditation MP3.', 'Research is not an endorsement'),
 ('04 / THE COMPARISON', 'A separate finding followed\nthree months of training.', 'Not twelve minutes of branded listening'),
 ('05 / THE PURCHASE', 'A listening routine may appeal.\nThe effect still needs proof.', 'Ask what was measured'),
 ('06 / YOUR TEST', 'Start with a free\ntwelve-minute baseline.', 'Then decide what an audio adds'),
]
frames = []
for index, (eyebrow, statement, note) in enumerate(scenes):
    im = Image.new('RGB', (W, H))
    pix = im.load()
    for y in range(H):
        for x in range(W):
            glow = max(0, 1 - math.hypot(x-950, y-160)/920)
            pix[x,y] = (int(15+26*glow), int(24+24*glow), int(31+20*glow))
    d = ImageDraw.Draw(im, 'RGBA')
    for r in range(230,105,-7):
        alpha = int(10+(230-r)/124*18)
        d.ellipse((895-r,340-r,895+r,340+r), outline=(216,168,102,alpha), width=2)
    d.arc((690,135,1100,545), 20+index*26, 300+index*26, fill=(231,189,122,220), width=4)
    d.line((95,110,1185,110), fill=(181,139,80,130), width=2)
    d.text((96,67), 'FINAL VESTIGE STUDIOS  /  MIND & PERCEPTION',
           font=ImageFont.truetype(FONT_BOLD,18), fill=(215,177,116))
    d.text((100,190), eyebrow, font=ImageFont.truetype(FONT_BOLD,24), fill=(211,165,100))
    d.multiline_text((98,250), statement, font=ImageFont.truetype(FONT_BOLD,51),
                     fill=(244,230,208), spacing=17)
    d.text((102,518), note, font=ImageFont.truetype(FONT,25), fill=(204,197,180))
    d.rectangle((99,616,1180,621), fill=(62,64,62))
    d.rectangle((99,616,99+int(1081*(index+1)/6),621), fill=(217,172,103))
    d.text((99,638), 'A SOURCE-FIRST FIELD GUIDE',
           font=ImageFont.truetype(FONT_BOLD,18), fill=(185,178,166))
    d.text((1118,638), f'{index+1:02d} / 06',
           font=ImageFont.truetype(FONT_BOLD,18), fill=(219,174,111))
    path = ROOT / f'mind_r343_scene_{index+1:02d}.png'
    im.save(path)
    frames.append(path)
manifest = ROOT / 'mind_r343_manifest.txt'
manifest.write_text(''.join(f"file '{p}'\nduration 7\n" for p in frames)
                    + f"file '{frames[-1]}'\n")
out = ROOT / 'mind_r343_original_42s_silent.mp4'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat',
                '-safe','0','-i',str(manifest),'-vsync','vfr','-vf',
                'fps=12,format=yuv420p','-t','42','-c:v','libx264','-crf',
                '23','-movflags','+faststart','-an',str(out)], check=True)
subprocess.run(['ffprobe','-v','error','-show_entries','format=duration,size',
                '-of','default=nw=1',str(out)], check=True)
print('Built:', out)
