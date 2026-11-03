#!/usr/bin/env python3
"""Original 40-second silent, caption-first research promo; deterministic PIL+FFmpeg renderer.
No external media, no merchant assets, no remote assets. Runs: python render_film.py
"""
import math, subprocess, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parent
W,H,FPS=540,960,12
SCENES=[
 (6,'TWELVE MINUTES.','ONE HOUR?','The question is not how fast time passes.','It is what the evidence can support.'),
 (7,'THE OFFER','A short audio ritual','Zen12 advertises twelve-minute sessions','in levels with different listening styles.'),
 (7,'FEATURE','IS NOT PROOF','A recording can be twelve minutes long.','That does not prove an hour of equivalence.'),
 (7,'THE RESEARCH','IS MIXED','A 2023 review examined 14 EEG studies.','It did not test Zen12 itself.'),
 (7,'BEFORE BUYING','TRY FOR FREE','Give twelve quiet minutes to yourself.','Notice comfort and preference, not miracles.'),
 (6,'AN EXPERIENCE','NEEDS CONTEXT','An audio ritual may be useful to someone.','Follow evidence before a purchase.'),
]
assert sum(x[0] for x in SCENES)==40
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
SANS='/usr/share/fonts/truetype/lato/Lato-Medium.ttf'
BOLD='/usr/share/fonts/truetype/lato/Lato-Bold.ttf'
font_label=ImageFont.truetype(BOLD,16)
font_head=ImageFont.truetype(SERIF,48)
font_sub=ImageFont.truetype(SERIF,34)
font_body=ImageFont.truetype(SANS,23)
font_small=ImageFont.truetype(SANS,16)
GOLD=(213,170,111); IVORY=(250,239,219); PALE=(212,205,190)
def center(d, txt, y, font, fill):
  box=d.textbbox((0,0),txt,font=font)
  d.text(((W-(box[2]-box[0]))/2,y),txt,font=font,fill=fill)
def draw(t, ix, local):
  im=Image.new('RGB',(W,H)); p=im.load()
  # Original dark editorial gradient + subtle warmed center.
  for y in range(H):
    phase=0.5+0.5*math.cos((y/H-.41)*math.pi)
    col=(int(8+5*phase),int(13+8*phase),int(15+7*phase))
    for x in range(W):p[x,y]=col
  d=ImageDraw.Draw(im)
  # restrained frame + navigational detail
  d.rectangle((21,21,W-22,H-22),outline=(80,65,47),width=2)
  d.line((46,110,W-46,110),fill=GOLD,width=2)
  d.text((46,54),'FINAL VESTIGE / MIND',font=font_label,fill=GOLD)
  d.text((W-112,54),f'{ix+1:02d} / 06',font=font_label,fill=PALE)
  sec,headline,sub,body1,body2=SCENES[ix]
  # An evidence dial, not an efficacy indicator. 12 tick marks.
  cx,cy=270,400
  d.ellipse((cx-148,cy-148,cx+148,cy+148),outline=(116,88,55),width=2)
  d.ellipse((cx-118,cy-118,cx+118,cy+118),outline=(47,66,65),width=1)
  for i in range(12):
    a=i*math.pi/6-math.pi/2
    r1,r2=133,143
    d.line((cx+math.cos(a)*r1,cy+math.sin(a)*r1,cx+math.cos(a)*r2,cy+math.sin(a)*r2),fill=(177,145,92),width=2)
  angle=-math.pi/2+(local/sec)*math.tau
  d.line((cx,cy,cx+math.cos(angle)*102,cy+math.sin(angle)*102),fill=GOLD,width=6)
  d.ellipse((cx-6,cy-6,cx+6,cy+6),fill=IVORY)
  head_font=font_head
  while d.textbbox((0,0),headline,font=head_font)[2] > W-92:
    head_font=ImageFont.truetype(SERIF,head_font.size-2)
  center(d,headline,183,head_font,IVORY)
  center(d,sub,565,font_sub,GOLD)
  center(d,body1,642,font_body,PALE)
  center(d,body2,678,font_body,PALE)
  # transparent story progress illustration, not a countdown offer
  d.rectangle((46,764,W-46,769),fill=(58,56,53))
  d.rectangle((46,764,46+int((W-92)*(t/40)),769),fill=GOLD)
  d.text((46,790),'ORIGINAL EDUCATIONAL SHORT',font=font_small,fill=GOLD)
  d.text((46,850),'Not a product trial or efficacy demonstration.',font=font_small,fill=PALE)
  d.text((46,884),'Sources and transcript in the reading guide.',font=font_small,fill=PALE)
  return im
frames=[]
t=0
for j,s in enumerate(SCENES):
 frames.append(draw(t,j,s[0]*0.5).resize((270,480)))
 t+=s[0]
contact=Image.new('RGB',(270*3,480*2))
for j,fr in enumerate(frames):contact.paste(fr,((j%3)*270,(j//3)*480))
contact.save(ROOT/'contact-sheet.png')
draw(0,0,1).save(ROOT/'poster.png')
if not shutil.which('ffmpeg'):raise SystemExit('ffmpeg missing')
cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','-','-an','-c:v','libx264','-pix_fmt','yuv420p','-preset','ultrafast','-crf','29','-movflags','+faststart',str(ROOT/'evidence-before-the-audio-40s.mp4')]
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
start=0
try:
 for ix,(dur,*_) in enumerate(SCENES):
  for n in range(int(dur*FPS)):
   im=draw(start+n/FPS,ix,n/FPS)
   proc.stdin.write(im.tobytes())
  start+=dur
finally:
 proc.stdin.close()
 if proc.wait()!=0:raise SystemExit('ffmpeg failed')
print('Rendered',ROOT/'evidence-before-the-audio-40s.mp4')
