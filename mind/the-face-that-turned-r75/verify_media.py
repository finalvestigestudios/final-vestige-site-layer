"""Offline-only tests for the original 40-second educational film.
Usage: python verify_media.py <offline-review-directory>
No network and no user data. Requires ffprobe.
"""
import json, subprocess, sys, re, zipfile
from pathlib import Path
from PIL import Image
ROOT = Path(sys.argv[1]) if len(sys.argv)>1 else Path("film-preview")
VIDEO=ROOT/"the-face-that-turned-40s.mp4"
CAPTIONS=ROOT/"captions.vtt"
REPORT=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries","stream=codec_name,width,height,nb_frames,r_frame_rate:format=duration","-of","json",str(VIDEO)]))
STREAM=REPORT["streams"][0]
assert STREAM["codec_name"]=="h264"
assert STREAM["width"]==540 and STREAM["height"]==960
assert STREAM["nb_frames"]=="480"
assert STREAM["r_frame_rate"]=="12/1"
assert abs(float(REPORT["format"]["duration"])-40)<0.01
assert Image.open(ROOT/"poster.png").size==(540,960)
CUES=re.findall(r"(\d\d:\d\d:\d\d\.\d+) --> (\d\d:\d\d:\d\d\.\d+)",CAPTIONS.read_text(encoding="utf-8"))
def sec(t):
    h,m,s=t.split(":")
    return int(h)*3600+int(m)*60+float(s)
assert len(CUES)==6
assert [round(sec(b)-sec(a)) for a,b in CUES]==[6,7,7,7,7,6]
assert sec(CUES[0][0])==0 and sec(CUES[-1][1])==40
with zipfile.ZipFile(ROOT/"offline-review.zip") as archive:
    assert archive.testzip() is None
    assert "the-face-that-turned-40s.mp4" in archive.namelist()
print("PASS: codec, dimensions, frames, fps, duration, poster, 6 cue intervals, cue endpoints and ZIP")
