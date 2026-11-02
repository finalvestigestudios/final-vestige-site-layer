#!/usr/bin/env python3
"""Render an original 40s silent historical-science short. No third-party clips/music.
Requires Pillow, ffmpeg and ffprobe. Output is offline review ONLY; not an approved web asset.
Run: python render_40s.py /mnt/data/fv_mind_r58
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import math
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 540, 960, 12
DURATIONS = [6, 7, 7, 7, 7, 6]
SCENES = [
    ("THE PENDULUM MOVED.", "The hand appeared still.", "VISIBLE MOTION IS NOT A CAUSE."),
    ("1852 / CARPENTER", "An idea might influence movement without a felt decision.", "A HISTORICAL HYPOTHESIS."),
    ("1854 / CHEVREUL", "Ask what the experiment establishes.", "THE QUESTION BEFORE THE EXPLANATION."),
    ("1976 / MEASURED", "Attention and cues changed pendulum movement in a study.", "EASTON & SHOR / n = 60."),
    ("A REAL SWING.", "A mistaken interpretation is still possible.", "THE APPARENT IS NOT THE PROVEN."),
    ("KEEP ASKING.", "What observation might change your mind?", "FINAL VESTIGE / EVIDENCE FIRST.")
]
if sum(DURATIONS) != 40:
    raise RuntimeError("Film scene times must sum to exactly forty seconds.")
FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
def font(idx, size):
    try:
        return ImageFont.truetype(FONTS[idx], size)
    except OSError:
        return ImageFont.load_default()
def wrap(draw, s, f, width):
    words = s.split()
    lines, line = [], ""
    for word in words:
        attempt = (line + " " + word).strip()
        if draw.textbbox((0, 0), attempt, font=f)[2] > width and line:
            lines.append(line)
            line = word
        else:
            line = attempt
    if line:
        lines.append(line)
    return lines
def paint(draw, text, xy, f, color, width, spacing=10):
    x,y = xy
    for line in wrap(draw, text, f, width):
        draw.text((x,y), line, font=f, fill=color, stroke_width=0)
        y += f.size + spacing
    return y
def draw_frame(frame_num):
    t = frame_num / FPS
    elapsed, scene = 0, 0
    for i, duration in enumerate(DURATIONS):
        if t < elapsed + duration:
            scene = i
            break
        elapsed += duration
    img = Image.new("RGB", (W,H), "#0a0c0b")
    d = ImageDraw.Draw(img)
    d.rectangle((24,24,W-24,H-24), outline="#746447", width=2)
    d.text((52,55), "FINAL VESTIGE  /  MIND ARCHIVE", font=font(2,16), fill="#d8bc82")
    d.line((52,105,488,105), fill="#655942", width=2)
    title,sub,footer = SCENES[scene]
    paint(d,title,(52,151),font(0,42),"#f8f1e2",438,14)
    paint(d,sub,(52,276),font(1,29),"#dfd5be",430,13)
    # Thin filament and pendulum illustrate a physical system, not a real lab recording.
    angle = 0.23 * math.sin(t * (2 * math.pi / 2.7))
    pivot = (270,494)
    length = 242
    end = (int(pivot[0]+length*math.sin(angle)),int(pivot[1]+length*math.cos(angle)))
    for r in (210,155):
        d.arc((270-r,540-r//3,270+r,540+r), 18, 165, fill="#3c4038", width=2)
    d.line((pivot[0],pivot[1],end[0],end[1]),fill="#edce91",width=3)
    d.ellipse((end[0]-24,end[1]-35,end[0]+24,end[1]+35),fill="#d6b277",outline="#fff0c3",width=2)
    d.ellipse((pivot[0]-6,pivot[1]-6,pivot[0]+6,pivot[1]+6),fill="#f4dcad")
    d.text((52,829),footer,font=font(2,18),fill="#f4e1bc")
    d.line((52,875,488,875),fill="#655942",width=2)
    d.text((52,892),"ILLUSTRATION · NOT A SCIENTIFIC TEST OR PRODUCT AD",font=font(1,13),fill="#b8b4a8")
    return img
def main():
    out = Path(sys.argv[1] if len(sys.argv)>1 else "/mnt/data/fv_mind_r58").resolve()
    out.mkdir(parents=True, exist_ok=True)
    poster = out / "film-poster.png"
    draw_frame(0).save(poster, optimize=True)
    mp4 = out / "pendulum-evidence-40s.mp4"
    with TemporaryDirectory(prefix="fv_r58_frames_") as temp:
        frame_dir=Path(temp)
        for number in range(sum(DURATIONS)*FPS):
            draw_frame(number).save(frame_dir / ("frame_%04d.png" % number), compress_level=1)
        subprocess.run([
            "ffmpeg","-y","-hide_banner","-loglevel","error",
            "-framerate",str(FPS),"-i",str(frame_dir/"frame_%04d.png"),
            "-vf","format=yuv420p","-c:v","libx264","-preset","medium","-crf","30",
            "-movflags","+faststart","-t","40",str(mp4)
        ],check=True)
    print(mp4, mp4.stat().st_size, "bytes")
    subprocess.run([
      "ffprobe","-v","error","-select_streams","v:0",
      "-show_entries","stream=codec_name,width,height,r_frame_rate,nb_frames",
      "-show_entries","format=duration,size","-of","default=noprint_wrappers=1",str(mp4)
    ],check=True)
if __name__ == "__main__":
    main()
