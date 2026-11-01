"""Original Final Vestige R52 change-blindness conceptual film. No third-party assets."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import subprocess

OUT = Path(__file__).resolve().parent
W, H, FPS, DURATION = 540, 960, 12, 40
BREAKS = [7, 14, 21, 28, 34, 40]
BG = (10, 15, 16)
CREAM = (244, 239, 230)
GOLD = (199, 166, 108)
MUTED = (185, 178, 168)
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
SERIF = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
regular = lambda s: ImageFont.truetype(FONT, s)
serif = lambda s: ImageFont.truetype(SERIF, s)

HEADS = [
    ('THE CONVERSATION', 'Two people begin to talk.'),
    ('THE INTERRUPTION', 'A door briefly hides one face.'),
    ('A DIFFERENT PERSON', 'The exchange continues.'),
    ('ONE 1998 EXPERIMENT', 'About half noticed the change.'),
    ('WHAT WAS MISSING?', 'A comparison across the gap.'),
    ('FOLLOW THE EVIDENCE', 'Not a product-efficacy trial.'),
]
FOOTERS = [
    'An illustrative scene; not research footage.',
    'The door concealed the substitution.',
    'Some observers did not report the change.',
    'The result was conditional, not universal.',
    'Attention shapes what we can compare.',
    'Scientific interest is not a sales claim.',
]

def centered(draw, y, text, font, fill=CREAM):
    bb = draw.textbbox((0, 0), text, font=font)
    draw.text(((W - (bb[2] - bb[0])) / 2, y), text, font=font, fill=fill)

def silhouette(draw, x, kind='a', fade=1):
    head = (138, 174, 162) if kind == 'a' else (190, 151, 142)
    torso = (68, 100, 93) if kind == 'a' else (129, 92, 84)
    if fade < 1:
        head = tuple(int(v*fade) for v in head)
        torso = tuple(int(v*fade) for v in torso)
    draw.ellipse((x-58, 355, x+58, 471), fill=head)
    draw.rounded_rectangle((x-82, 464, x+82, 663), radius=70, fill=torso)
    if kind == 'b':
        draw.polygon([(x-49,384),(x-20,359),(x+28,361),(x+57,384)], fill=(99,76,71))

def scene(seconds):
    return next(i for i, end in enumerate(BREAKS) if seconds < end)

def frame(index):
    t = index / FPS
    i = scene(t)
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle((28, 28, W-28, H-28), outline=(93, 80, 63), width=2)
    d.line((54, 160, W-54, 160), fill=(84, 75, 64), width=2)
    d.text((55, 73), 'FINAL VESTIGE  /  MIND 52', font=regular(17), fill=GOLD)
    centered(d, 193, HEADS[i][0], regular(24), GOLD)
    centered(d, 244, HEADS[i][1], serif(21))
    d.ellipse((69, 326, 462, 722), outline=(56, 54, 50), width=3)
    if i < 3:
        silhouette(d, 150, 'a')
        silhouette(d, 386, 'a' if i < 2 else 'b')
        if i == 1:
            local = t - 7
            x = int(-35 + 64*local)
            d.rectangle((x, 320, x+160, 715), fill=(171,144,105), outline=GOLD, width=3)
            d.rectangle((x+15,338,x+145,697),fill=(73,65,53))
            d.ellipse((x+126,522,x+134,530),fill=GOLD)
        if i == 0:
            d.rounded_rectangle((251,310,471,369),radius=10,outline=GOLD,width=2)
            d.text((268,330),'Directions?',font=regular(21),fill=CREAM)
    elif i == 3:
        d.ellipse((149,396,390,637), outline=GOLD, width=12)
        d.pieslice((149,396,390,637), 90, 270, fill=GOLD)
        centered(d, 659, 'About half detected it', regular(19), CREAM)
    elif i == 4:
        for x, col in [(78,(133,173,163)), (307,(184,149,144))]:
            d.rounded_rectangle((x,388,x+152,621),radius=8,fill=(20,25,26),outline=GOLD,width=2)
            d.ellipse((x+55,432,x+100,477),fill=col)
            d.rounded_rectangle((x+34,486,x+118,569),radius=35,fill=col)
        d.line((250,518,294,518),fill=GOLD,width=5)
        d.polygon([(293,518),(281,506),(281,530)],fill=GOLD)
        centered(d,665,'Two views. A missing link.',regular(18),CREAM)
    else:
        d.rounded_rectangle((93,387,447,632),radius=8,fill=(22,25,24),outline=GOLD,width=3)
        d.text((115,420),'OBSERVATION',font=regular(21),fill=GOLD)
        d.line((115,462,414,462),fill=(90,80,66),width=2)
        d.text((115,498),'Interpretation',font=regular(21),fill=CREAM)
        d.text((115,540),'is not proof.',font=serif(28),fill=CREAM)
    d.line((58,762,482,762),fill=(81,73,62),width=2)
    centered(d,790,FOOTERS[i],regular(17),MUTED)
    centered(d,844,'Educational concept  /  not a real test',regular(16),MUTED)
    d.rectangle((52,898,int(52+436*((index+1)/(DURATION*FPS))),903),fill=GOLD)
    return img

def main():
    path = OUT / 'change-blindness-40s.mp4'
    cmd = ['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}', '-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','26','-pix_fmt','yuv420p','-movflags','+faststart',str(path)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for n in range(DURATION*FPS):
        p.stdin.write(frame(n).tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise RuntimeError('ffmpeg encoder failed')
    frame(16*FPS).save(OUT / 'film-poster.png')
    print(path)

if __name__ == '__main__':
    main()
