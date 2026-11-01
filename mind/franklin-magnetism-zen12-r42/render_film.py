"""Original silent 40-second storyboard renderer; requires Pillow and ffmpeg; renders only offline.
No source video, stock assets, user data, network or product demonstrations. Six 80-frame scenes at 12fps.
"""
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw, ImageFont
W,H,FPS,SCENES=540,960,12,6
STORIES=[
("THE BLINDFOLD","Passy, 1784. A young participant waits."),
("ONE APRICOT TREE","A physician prepares a single tree."),
("FOUR OTHER TREES","The boy is guided to different trees."),
("AN INTENSE REACTION","He faints at a tree never magnetized."),
("EXPERIENCE IS REAL","The proposed cause remains unproved."),
("EVIDENCE BEFORE CLAIM","What does an audio product actually test?")
]
def font(size):
    for path in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf","/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"]:
        if Path(path).exists():return ImageFont.truetype(path,size)
    return ImageFont.load_default()
def make_frame(idx):
    im=Image.new("RGB",(W,H),(18,26,32));d=ImageDraw.Draw(im)
    d.rounded_rectangle((28,28,W-28,H-28),radius=14,outline=(145,115,78),width=3)
    headline,sub=STORIES[idx]
    d.text((42,80),"FINAL VESTIGE  /  EVIDENCE FILE",font=font(17),fill=(222,189,136))
    d.multiline_text((42,162),headline,font=font(35),fill=(246,229,201),spacing=10)
    d.text((42,780),sub,font=font(18),fill=(245,238,224))
    d.text((42,865),f"SCENE {idx+1}/6  ·  HISTORICAL ILLUSTRATION",font=font(16),fill=(224,199,158))
    for n in range(4):
        x=100+n*112
        d.line((x,570,x,430),fill=(212,212,194),width=10)
        d.ellipse((x-38,350,x+38,440),fill=(59,85,65),outline=(195,211,180),width=3)
    if idx in (1,2,3):
        d.ellipse((215,613,325,723),outline=(231,184,123),width=6)
        d.line((200,663,340,663),fill=(231,184,123),width=8)
    if idx==3:d.text((75,300),"NOT THE PREPARED TREE",font=font(20),fill=(255,223,162))
    if idx==5:d.text((85,320),"FEELING ≠ CAUSE",font=font(33),fill=(255,223,162))
    return im
def main():
    out=Path(__file__).parent/"offline-blind-test-40s.mp4"
    cmd=["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-pix_fmt","yuv420p","-preset","veryfast","-crf","28","-movflags","+faststart",str(out)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for idx in range(SCENES):
            raw=make_frame(idx).tobytes()
            for _ in range(80):p.stdin.write(raw)
    finally:p.stdin.close()
    result=p.wait()
    if result: raise RuntimeError(f"ffmpeg failed: {result}")
    print(out)
if __name__=="__main__":main()
