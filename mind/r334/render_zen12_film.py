#!/usr/bin/env python3
"""Render the original, silent 42-second Mind R334 explanatory film.

Source-controlled recipe. Requires Pillow and local ffmpeg + ffprobe.
No network, vendor sound libraries, tracking, or stock footage.
Run: python mind/r334/render_zen12_film.py
Optional local output path: python mind/r334/render_zen12_film.py /tmp/zen12-42s.mp4
The MP4 is a release artifact, NOT committed or deployed by this script.
"""
from __future__ import annotations
import pathlib, shutil, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
OUTPUT = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE / "zen12-42s.mp4"
PAGES = [
    ("WHAT WAS TESTED?", "A recording helped some participants.", "But what was actually tested?"),
    ("THE CLINICAL STUDY", "333 people with multiple sclerosis", "were assigned to audio access or usual care."),
    ("THE MEASURE", "Researchers measured fatigue impact.", "Not concentration at your desk."),
    ("THE PRODUCT", "Zen12 is a twelve-minute audio course", "offered in three different tiers."),
    ("THE FREE FIRST STEP", "Try an ordinary twelve-minute routine.", "Compare evidence before a purchase."),
    ("THE FINAL VESTIGE RULE", "Make a decision based on what is known.", "The source is not the sales claim."),
]

def font(size: int, serif: bool = False):
    candidates = (["/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"] if serif else ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"])
    for path in candidates:
        if pathlib.Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def card(i: int) -> Image.Image:
    im = Image.new("RGB", (1280, 720), "#101920")
    d = ImageDraw.Draw(im)
    # Original diagrammatic film, not an archival facsimile.
    d.ellipse((785, -110, 1400, 505), outline="#594a3b", width=3)
    d.ellipse((880, -15, 1305, 410), outline="#473e35", width=2)
    d.line((100, 80, 1180, 80), fill="#927f65", width=2)
    d.text((105, 110), "FINAL VESTIGE  /  MIND & PERCEPTION", font=font(23), fill="#e2bd81")
    d.text((105, 238), PAGES[i][0], font=font(58, True), fill="#f7f0e4")
    d.text((105, 352), PAGES[i][1], font=font(33), fill="#e2e9e5")
    d.text((105, 415), PAGES[i][2], font=font(33), fill="#e2e9e5")
    for n in range(6):
        x = 105 + n * 155
        d.rounded_rectangle((x, 635, x + 125, 641), radius=3, fill="#e2bd81" if n <= i else "#445661")
    d.text((105, 665), f"00:{i * 7:02d}–00:{(i + 1) * 7:02d}  •  UNPUBLISHED REVIEW FILM", font=font(19), fill="#abb9ba")
    return im

def main():
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise SystemExit("ffmpeg and ffprobe are required; no download attempted")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="fv-r334-") as tmp:
        root = pathlib.Path(tmp)
        manifest = []
        for i in range(6):
            path = root / f"slide-{i:02d}.png"
            card(i).save(path)
            manifest.extend([f"file '{path.as_posix()}'", "duration 7"])
        manifest.append(f"file '{(root / 'slide-05.png').as_posix()}'")
        (root / "concat.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")
        subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",str(root / "concat.txt"),"-vf","fps=6,scale=960:540:flags=lanczos,format=yuv420p","-c:v","libx264","-preset","veryfast","-crf","29","-movflags","+faststart","-an",str(OUTPUT)],check=True)
    duration = subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(OUTPUT)], text=True).strip()
    if not 41.8 <= float(duration) <= 42.5:
        raise SystemExit(f"Unexpected film duration: {duration}s")
    print(f"RENDERED {OUTPUT} duration={duration}s bytes={OUTPUT.stat().st_size}")

if __name__ == "__main__":
    main()
