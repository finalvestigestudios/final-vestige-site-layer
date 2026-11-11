"""Original FV Mind R301 source-led short film. Offline Pillow + FFmpeg, 42s.
Source control is not a hosted media asset or publication approval.
Use: python render_zen12_source_ladder.py output_directory
"""
import sys, math, subprocess, pathlib
from PIL import Image, ImageDraw, ImageFont
OUT=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else '.'); OUT.mkdir(parents=True,exist_ok=True)
W,H,FPS,DURATION=960,540,12,42
SCENES=[
('THE SECOND TARGET','What happens when two signals arrive too close together?','EXPERIMENT, NOT SELF-TEST'),
('FIRST TARGET','Report one target in a rapid stream of symbols.','RAYMOND ET AL. · 1992'),
('SECOND TARGET','A second target may be missed at some short delays.','UNDER SPECIFIC TASK CONDITIONS'),
('EXCEPTIONS MATTER','When targets arrive back-to-back, the second may be spared.','LAG-1 SPARING'),
('TRAINING ≠ PRODUCT','An intensive meditation study is not a test of an audio store.','SLAGTER ET AL. · 2007'),
('WHAT ZEN12 SELLS','The seller advertises 12 levels and 48 MP3 recordings.','SELLER CONTENTS · NOT EFFICACY PROOF'),
('READ THE EVIDENCE','Start with the study. Consider free practice. Then evaluate offers.','FINAL VESTIGE STUDIOS · UNPUBLISHED PILOT')]
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font=lambda n,b=False:ImageFont.truetype(BOLD if b else FONT,n)
F_BIG=font(46,True); F_MID=font(23); F_SMALL=font(14,True)
def base(t):
 im=Image.new('RGB',(W,H),'#0b151b'); d=ImageDraw.Draw(im)
 drift=int(8*math.sin(t*.12))
 for k in range(0,540,30): d.line((75,k+drift,885,k+drift),fill='#17282e',width=1)
 d.rectangle((62,54,898,486),outline='#53626a',width=2)
 d.line((86,125,874,125),fill='#bc9656',width=3)
 d.text((88,78),'FINAL VESTIGE     /     MIND & PERCEPTION',font=F_SMALL,fill='#e0c79b')
 return im,d
def render(t):
 idx=min(6,int(t//6)); im,d=base(t)
 title,desc,meta=SCENES[idx]
 d.text((87,184),title,font=F_BIG,fill='#f6f0e3')
 words=desc.split();lines=[];line=''
 for w in words:
  candidate=(line+' '+w).strip()
  if d.textbbox((0,0),candidate,font=F_MID)[2]>730 and line: lines.append(line); line=w
  else: line=candidate
 if line: lines.append(line)
 for k,line in enumerate(lines): d.text((90,275+k*37),line,font=F_MID,fill='#d7d9d6')
 d.text((90,421),meta,font=F_SMALL,fill='#dcbb80')
 d.rounded_rectangle((88,456,871,461),radius=2,fill='#32434b')
 d.rounded_rectangle((88,456,88+int(783*(t/DURATION)),461),radius=2,fill='#d4ab67')
 return im
if __name__=='__main__':
 render(0).save(OUT/'poster.png')
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-vcodec','rawvideo','-s',f'{W}x{H}','-pix_fmt','rgb24','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','32','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'zen12-evidence-before-offer-42s.mp4')]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 for i in range(FPS*DURATION):p.stdin.write(render(i/FPS).tobytes())
 p.stdin.close();raise SystemExit(p.wait())
