#!/usr/bin/env python3
"""Offline, original 42-second silent motion storyboard for FV Mind R377.

Requirements: Python 3, Pillow, ffmpeg with libx264. No network/media/API calls.
Usage: python mind/r377/render_film.py --output /tmp/fv-mind-r377.mp4
Video is a prototype only: no human narration/audio. Use separately reviewed
VTT and full transcript. No production deployment or merchant activation.
"""
from __future__ import annotations
import argparse, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W,H,FPS,SECS=640,360,12,42
BG=(10,21,30);FG=(236,239,234);GOLD=(227,194,134);MUTED=(178,198,202)
SCENES=[
 ("THE SEARCH SET","Your task shapes what you notice.","2013 / experimental attention"),
 ("24 RADIOLOGISTS","Twenty did not report an inserted gorilla.","Nodule-search simulation"),
 ("GAZE IS NOT AWARENESS","Some looked at its location.","Eye position is not recognition"),
 ("A STUDY, NOT A DIAGNOSIS","Artificial image. Defined task.","No claim about clinical mistakes"),
 ("A PROMISE NEEDS PROOF","What was tested on this exact product?","General science is not a product trial"),
 ("BEFORE YOU BUY","Try the free twelve-minute audit.","One existing Focus Fieldbook"),
]
def font(size):
 for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf","/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"):
  if Path(p).exists(): return ImageFont.truetype(p,size)
 return ImageFont.load_default()
TITLE,BODY,TINY=font(28),font(19),font(14)
def render(frame):
 sec=frame/FPS;idx=min(5,int(sec/7));progress=(frame+1)/(SECS*FPS)
 im=Image.new("RGB",(W,H),BG);d=ImageDraw.Draw(im)
 # Slow, original abstract scan-grid / documentary style, no clinical imagery.
 for x in range(40,620,46):d.line((x,38,x,300),fill=(29,48,56),width=1)
 for y in range(38,300,39):d.line((40,y,600,y),fill=(29,48,56),width=1)
 d.rounded_rectangle((32,28,608,318),radius=12,outline=(83,108,116),width=2)
 d.text((58,63),SCENES[idx][0],font=TITLE,fill=GOLD)
 d.text((58,139),SCENES[idx][1],font=BODY,fill=FG)
 d.text((58,198),SCENES[idx][2],font=TINY,fill=MUTED)
 # Each card stays readable for 7 seconds; progress is subtle, never flickers.
 d.ellipse((514,222,580,288),outline=GOLD,width=3)
 angle=3.14159265359*2*(frame%(FPS*7))/(FPS*7)
 import math
 d.line((547,255,547+24*math.cos(angle),255+24*math.sin(angle)),fill=GOLD,width=3)
 d.rectangle((32,332,608,340),fill=(55,74,82))
 d.rectangle((32,332,32+int(576*progress),340),fill=GOLD)
 return im.tobytes()
def main():
 p=argparse.ArgumentParser();p.add_argument("--output",required=True);args=p.parse_args()
 dst=Path(args.output);dst.parent.mkdir(parents=True,exist_ok=True)
 cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-f","rawvideo","-vcodec","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-an","-c:v","libx264","-preset","slow","-crf","31","-pix_fmt","yuv420p","-movflags","+faststart","-t",str(SECS),str(dst)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 try:
  for i in range(SECS*FPS):proc.stdin.write(render(i))
 finally:proc.stdin.close()
 if proc.wait()!=0:raise SystemExit("ffmpeg failed")
 print(f"RENDERED {dst} ({dst.stat().st_size} bytes; {SECS}s; {FPS}fps; silent prototype only)")
if __name__=="__main__":main()
