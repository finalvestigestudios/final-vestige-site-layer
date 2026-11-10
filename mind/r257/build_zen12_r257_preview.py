#!/usr/bin/env python3
"""Original 42-second silent illustrated card-film; draft-only, never deployed.
Use: python3 build_zen12_r257_preview.py <output-dir>
Requires Pillow + system ffmpeg. Fonts are system dependencies, not redistributed.
No consumer claims, merchant assets, tracking, streaming, or forced playback.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import subprocess, math, sys
ROOT=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/r257film')
ROOT.mkdir(parents=True,exist_ok=True)
W,H=540,960
serif='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
sans='/usr/share/fonts/truetype/lato/Lato-Regular.ttf'
bold='/usr/share/fonts/truetype/lato/Lato-Bold.ttf'
F=lambda p,s:ImageFont.truetype(p,s)
heading=F(serif,45); small=F(sans,24); tiny=F(bold,17)
BG=(10,20,30); GOLD=(232,192,119); IVORY=(247,233,203); SILVER=(205,225,220); TEAL=(74,136,142)
cards=[
('12 MINUTES','A duration.\nNot an outcome.','A number on a clock is not a measured benefit.'),
('THE EXPERIENCE','A quiet session\nmay feel valuable.','What caused that feeling is a different question.'),
('THE COMPARISON','Timer. Voice.\nExpectation.','Several factors can influence the same experience.'),
('THE EVIDENCE','14 EEG studies.','5 compatible · 8 contrary · 1 mixed.'),
('THE LIMIT','That review did\nnot test Zen12.','Nor did it prove 12 minutes equals an hour.'),
('THE FREE TEST','Try a timer.\nRecord what fits.','A routine diary is not medical proof.'),
('THE DECISION','Evidence before\nyou purchase.','Read the independent guide and verify the terms.')]
def centered(draw,text,y,font,fill):
 lines=[]
 for logical_line in text.split('\n'):
  words=logical_line.split(); current=''
  for word in words:
   trial=(current+' '+word).strip()
   if draw.textbbox((0,0),trial,font=font)[2]>W-84 and current:
    lines.append(current); current=word
   else:current=trial
  if current:lines.append(current)
 for line in lines:
  box=draw.textbbox((0,0),line,font=font); width=box[2]-box[0]
  draw.text(((W-width)/2,y),line,font=font,fill=fill)
  y+=(box[3]-box[1])+18
 return y
for i,(k,h,desc) in enumerate(cards):
 img=Image.new('RGB',(W,H),BG); pix=img.load()
 for y in range(H):
  for x in range(W):
   glow=17*max(0,1-math.hypot((x-W*.52)/(W*.9),(y-H*.42)/(H*.65)))
   pix[x,y]=(int(10+glow*.5),int(21+glow*.73),int(31+glow))
 d=ImageDraw.Draw(img)
 d.rectangle((19,19,W-20,H-20),outline=(83,114,115),width=2)
 d.arc((145,145,395,395),start=30,end=306,fill=GOLD,width=8)
 d.arc((162,162,378,378),start=210,end=357,fill=TEAL,width=4)
 d.line([(W//2,185),(W//2,270)],fill=GOLD,width=4)
 d.ellipse((W//2-10,260,W//2+10,280),fill=GOLD)
 centered(d,'FINAL VESTIGE STUDIOS',56,tiny,GOLD)
 centered(d,k,438,tiny,GOLD)
 centered(d,h,496,heading,IVORY)
 centered(d,desc,704,small,SILVER)
 d.line((76,825,464,825),fill=(82,123,125),width=2)
 d.rectangle((76,819,76+int(388*(i+1)/7),831),fill=GOLD)
 centered(d,f'{i+1} / 7   ·   00:{i*6:02d}–00:{(i+1)*6:02d}',852,tiny,GOLD)
 img.save(ROOT/f'frame_{i+1:02d}.png',optimize=True)
captions=[
'Twelve minutes is an amount of time—not a measured benefit.',
'A listener may feel calmer. That experience deserves respect.',
'But a free timer, a guided voice, and expectation can all matter.',
'The 2023 EEG review found mixed results for binaural-beat entrainment.',
'It did not test Zen12 Premium or prove twelve minutes equals sixty.',
'Compare the format with a free session. Record what you noticed.',
'Read the evidence and the terms before deciding to purchase.']
def tt(s): return f'00:00:{s:02d}.000'
with open(ROOT/'zen12_42s_preview.vtt','w',encoding='utf-8') as f:
 f.write('WEBVTT\n\n')
 for i,t in enumerate(captions):f.write(f'{tt(i*6)} --> {tt((i+1)*6)}\n{t}\n\n')
inputs=[]; chains=[]; streams=[]
for i in range(7):
 inputs+=['-loop','1','-framerate','12','-t','6','-i',str(ROOT/f'frame_{i+1:02d}.png')]
 chains.append(f'[{i}:v]fps=12,format=yuv420p,fade=t=in:st=0:d=0.3,fade=t=out:st=5.7:d=0.3[v{i}]')
 streams.append(f'[v{i}]')
filter_complex=';'.join(chains+[''.join(streams)+'concat=n=7:v=1:a=0[outv]'])
cmd=['ffmpeg','-hide_banner','-loglevel','error','-y']+inputs+['-filter_complex',filter_complex,'-map','[outv]','-c:v','libx264','-preset','veryfast','-crf','23','-pix_fmt','yuv420p','-r','12','-movflags','+faststart',str(ROOT/'zen12_42s_preview.mp4')]
subprocess.run(cmd,check=True)
subprocess.run(['ffprobe','-v','error','-show_entries','format=duration,size','-of','default=noprint_wrappers=1',str(ROOT/'zen12_42s_preview.mp4')],check=True)
print('Draft only:',ROOT/'zen12_42s_preview.mp4')
