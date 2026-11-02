"""Original Final Vestige 40-second silent evidence short; source only, no borrowed media.
Requires Pillow and local ffmpeg. Do not upload to production without first-party hosting approval.
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
import subprocess

ROOT = Path(__file__).resolve().parent
W, H, FPS, SECONDS = 540, 960, 12, 40
SCENES = [
    ('A SMALL WINDOW', 'Twelve minutes is an inviting idea.', 'It is also only a duration.', 7),
    ('FORMAT, NOT PROOF', 'An audio recording describes a routine.', 'That does not establish its effects.', 7),
    ('THE COMPARISON', 'An hour-for-twelve-minutes claim', 'requires outcomes defined in advance.', 7),
    ('THE EVIDENCE', 'Compare real people, suitable controls,', 'and repeatable results.', 6),
    ('THE FREE EXPERIMENT', 'Try listening formats you already have.', 'Notice what you actually enjoy.', 7),
    ('THE CHOICE', 'Choose with evidence.', 'No purchase is required to begin.', 6),
]
assert sum(scene[3] for scene in SCENES) == SECONDS
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
regular = ImageFont.truetype(FONT, 25)
small = ImageFont.truetype(FONT, 17)
caption_font = ImageFont.truetype(FONT, 20)
bold = ImageFont.truetype(BOLD, 45)
numfont = ImageFont.truetype(FONT, 83)


def center(d, y, line, font, color, maxw=440):
    """Truncate only if an original script line is unexpectedly too wide."""
    while d.textbbox((0, 0), line, font=font)[2] > maxw:
        line = line[:-1]
    x = (W - d.textbbox((0, 0), line, font=font)[2]) / 2
    d.text((x, y), line, font=font, fill=color)


def render(index, local_fraction, frame):
    im = Image.new('RGB', (W, H), (10, 12, 12))
    draw = ImageDraw.Draw(im)
    # Vertical original color field, bounded so even 8-bit RGB remains readable.
    for row in range(H):
        value = int(13 + 12 * row/H)
        draw.line((0, row, W, row), fill=(value, value+1, value))
    draw.rectangle((27, 27, W-27, H-27), outline=(127, 106, 70), width=2)
    draw.text((50, 52), 'FINAL VESTIGE  /  THE MIND ARCHIVE', font=small, fill=(218, 190, 142))
    draw.line((50, 87, 490, 87), fill=(115, 100, 75), width=1)
    # Six-piece progress ruler. All visual movement is reduced and optional by video controls.
    for i in range(6):
        col = (203, 167, 104) if i <= index else (62, 60, 56)
        draw.rounded_rectangle((49+i*75, 114, 105+i*75, 120), radius=2, fill=col)
    cx, cy = 270, 334
    radius = 142
    draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), outline=(92, 80, 64), width=3)
    angle = 2*math.pi*(frame/(FPS*SECONDS))
    theta = -math.pi/2 + angle
    px = cx + (radius-16)*math.cos(theta)
    py = cy + (radius-16)*math.sin(theta)
    draw.line((cx, cy, px, py), fill=(209, 175, 109), width=5)
    draw.ellipse((cx-6, cy-6, cx+6, cy+6), fill=(235, 218, 184))
    center(draw, 307, f'00:{frame // FPS:02d}', numfont, (240, 231, 214), 450)
    draw.line((80, 555, 460, 555), fill=(174, 146, 100), width=2)
    center(draw, 589, SCENES[index][0], caption_font, (205, 173, 116))
    center(draw, 637, SCENES[index][1], regular, (239, 232, 223))
    center(draw, 687, SCENES[index][2], regular, (232, 225, 215))
    draw.text((50, 844), '40 SEC  •  EVIDENCE BEFORE OFFERS', font=small, fill=(192, 179, 153))
    draw.text((50, 887), 'EDUCATIONAL CONCEPT • NOT A PRODUCT TEST', font=small, fill=(192, 179, 153))
    return im


def main():
    out = ROOT / 'twelve-minutes-not-a-result-40s.mp4'
    cmd = [
        'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
        '-f', 'rawvideo', '-vcodec', 'rawvideo', '-pix_fmt', 'rgb24',
        '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-an',
        '-vcodec', 'libx264', '-preset', 'fast', '-crf', '24',
        '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(out)
    ]
    contact = Image.new('RGB', (W*3, H*2), (10, 12, 12))
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    frame_no = 0
    try:
        for index, scene in enumerate(SCENES):
            count = scene[3]*FPS
            for j in range(count):
                im = render(index, j/count, frame_no)
                if j == count//2:
                    contact.paste(im, ((index % 3)*W, (index//3)*H))
                    if index == 0:
                        im.save(ROOT / 'poster.png', optimize=True)
                proc.stdin.write(im.tobytes())
                frame_no += 1
    finally:
        proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError('ffmpeg render failed')
    contact.save(ROOT / 'contact-sheet.png', optimize=True)
    assert frame_no == SECONDS*FPS == 480
    print(f'Rendered {out} | frames={frame_no} | seconds={SECONDS}')


if __name__ == '__main__':
    main()
