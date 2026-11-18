#!/usr/bin/env python3
"""Original 42-second silent typography film. Requires Pillow, ffmpeg, ffprobe.
No network, stock clips, external media, product testimonials, or tracking.
Exported MP4 is a local proof, NOT a hosted/authorized site asset.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import shutil, subprocess

OUT = Path(__file__).resolve().parent
W, H = 960, 540
BG = '#101721'; PANEL = '#1d2a36'; GOLD = '#e0c18a'; WHITE = '#f0ecdf'; MUTE = '#b9c7cc'
SCENES = [
 ('01 / OBSERVE', 'Two events,', 'one brief interval.', 'The first target does not guarantee the second.'),
 ('02 / EXPERIMENT', 'A rapid stream.', 'Two target items.', 'Researchers recorded what participants reported.'),
 ('03 / INTERFERENCE', 'Distractions between', 'the targets matter.', 'Some sequences make the second harder to report.'),
 ('04 / COUNTEREXAMPLE', 'Immediate targets', 'can be spared.', 'The result changes when the sequence changes.'),
 ('05 / LIMIT', 'Meditation research', 'is not product proof.', 'The Zen12 audio itself was not tested here.'),
 ('06 / YOUR DECISION', 'Check the source.', 'Then compare the offer.', 'No claims of automatic brainwave or medical effects.'),
]
def font(size, bold=False):
    candidates = [
      '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
      '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf',
    ]
    for candidate in candidates:
        if Path(candidate).is_file(): return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()

frames = OUT / 'frames'; frames.mkdir(parents=True, exist_ok=True)
for i, (label, head1, head2, sub) in enumerate(SCENES):
    im=Image.new('RGB', (W,H), BG); d=ImageDraw.Draw(im)
    d.rounded_rectangle((54,58,906,482), radius=18, fill=PANEL, outline='#50616d', width=2)
    d.rectangle((55,58,906,65), fill=GOLD)
    d.text((81,100), 'FINAL VESTIGE  /  MIND & PERCEPTION', font=font(20,True), fill=GOLD)
    d.text((81,157),label,font=font(22,True),fill=MUTE)
    d.text((81,228),head1,font=font(46,True),fill=WHITE)
    d.text((81,288),head2,font=font(46,True),fill=GOLD)
    d.text((82,384),sub,font=font(22),fill=WHITE)
    for j in range(6):
        x=84+j*44; d.rounded_rectangle((x,438,x+30,446),radius=4,fill=GOLD if j<=i else '#546578')
    d.text((820,427),f'{7*(i+1):02d}s / 42s',font=font(17),fill=MUTE)
    im.save(frames/f'{i:02d}.png',optimize=True)

concat=OUT/'frames.txt'
concat.write_text(''.join(f"file '{(frames/f'{i:02d}.png').as_posix()}'\nduration 7\n" for i in range(6)) + f"file '{(frames/'05.png').as_posix()}'\n",encoding='utf-8')
mp4=OUT/'ZEN12_42S_SILENT_PREVIEW.mp4'
if not shutil.which('ffmpeg'): raise SystemExit('ffmpeg not installed')
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(concat),'-t','42','-r','24','-vf',f'scale={W}:{H},format=yuv420p','-c:v','libx264','-preset','veryfast','-crf','24','-movflags','+faststart','-an',str(mp4)], check=True)
print(f'Built {mp4} ({mp4.stat().st_size} bytes); silent, 42 seconds, six original illustrated text scenes.')
