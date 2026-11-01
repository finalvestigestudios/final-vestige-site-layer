"""Render a wholly original 40-second portrait educational silent film.

Pillow and ffmpeg only. No merchant content, telemetry, audio, borrowed assets, or user data.
Run: python render_attentional_blink.py
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import subprocess
import math

OUT=Path(__file__).resolve().parent
W,H,FPS,SEC=540,960,12,40
BG=(9,10,10)
WHITE=(244,239,230)
BODY=(216,210,199)
GOLD=(198,162,109)
SOFT=(160,154,145)
PANEL=(19,20,19)
LINE=(65,57,47)
DARK=(18,20,20)
FONTS='/usr/share/fonts/truetype/dejavu/'
regular=FONTS+'DejaVuSans.ttf'
bold=FONTS+'DejaVuSans-Bold.ttf'
serif=FONTS+'DejaVuSerif.ttf'

def font(size,kind='regular'):
 return ImageFont.truetype({'regular':regular,'bold':bold,'serif':serif}[kind],size)

def lines(draw,text,fontobj,max_width):
 words=text.split(); row=[]; result=[]
 for word in words:
  trial=' '.join(row+[word])
  if row and draw.textbbox((0,0),trial,font=fontobj)[2]>max_width:
   result.append(' '.join(row));row=[word]
  else:row.append(word)
 if row:result.append(' '.join(row))
 return result

def para(draw,text,y,color=BODY,size=25,max_width=448,x=46,leading=14,kind='regular'):
 f=font(size,kind)
 for line in lines(draw,text,f,max_width):
  draw.text((x,y),line,font=f,fill=color)
  y+=size+leading
 return y

def base(number,title,sub,progress):
 im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
 d.text((44,50),'FINAL VESTIGE  /  MIND',font=font(18,'bold'),fill=GOLD)
 d.line((44,94,496,94),fill=LINE,width=2)
 d.text((44,126),f'0{number} / 06',font=font(18),fill=GOLD)
 y=para(d,title,172,color=WHITE,size=36,max_width=453,leading=12,kind='serif')
 d.line((44,832,496,832),fill=LINE,width=2)
 para(d,sub,855,color=SOFT,size=19,max_width=440,leading=8)
 d.rectangle((44,928,496,934),fill=(42,39,35))
 d.rectangle((44,928,44+int(452*progress),934),fill=GOLD)
 return im,d,max(y+22,328)

def ellipse(d,xy,color,line=None): d.ellipse(xy,fill=color,outline=line)

def scene(number,t):
 # t = local fraction of the segment
 progress=([0,6,13,20,27,34][number-1]+t*[6,7,7,7,7,6][number-1])/40
 if number==1:
  im,d,y=base(1,'Two numbers. One missing.','An experiment in the limits of attention',progress)
  d.rounded_rectangle((51,366,247,630),radius=9,fill=GOLD)
  d.rounded_rectangle((293,366,489,630),radius=9,fill=PANEL,outline=GOLD,width=3)
  d.text((101,397),'3',font=font(165,'serif'),fill=DARK)
  # second number remains physically on screen but is less pronounced
  d.text((343,397),'8',font=font(165,'serif'),fill=(125,111,93))
  d.text((65,679),'BOTH ON SCREEN',font=font(23,'bold'),fill=WHITE)
  d.text((65,724),'NOT BOTH REPORTED',font=font(21),fill=GOLD)
 elif number==2:
  im,d,y=base(2,'The 1992 visual-stream test','Raymond, Shapiro & Arnell · 1992',progress)
  for i,ch in enumerate('A7KX4M'):
   xpos=43+i*76
   color=GOLD if ch in '74' else PANEL
   d.rounded_rectangle((xpos,394,xpos+65,501),radius=5,fill=color,outline=GOLD if ch in '74' else LINE,width=2)
   d.text((xpos+12,421),ch,font=font(43,'bold'),fill=DARK if ch in '74' else SOFT)
  para(d,'The second target was harder to report at certain short delays after the first.',561,WHITE,25,445,47,13)
 elif number==3:
  im,d,y=base(3,'The eyes never needed to blink','The word “blink” is a metaphor',progress)
  ellipse(d,(132,374,410,590),PANEL,LINE)
  ellipse(d,(182,421,360,555),WHITE)
  ellipse(d,(252,431,330,535),GOLD)
  ellipse(d,(280,461,304,509),DARK)
  para(d,'The target could be visible while its report was lost.',636,WHITE,26,435,51,12)
 elif number==4:
  im,d,y=base(4,'Three months of practice','Slagter and colleagues · 2007',progress)
  for idx in range(3):
   x=62+150*idx
   d.rounded_rectangle((x,394,x+117,515),radius=7,fill=PANEL,outline=GOLD,width=2)
   d.text((x+32,425),f'{idx+1}',font=font(52,'serif'),fill=WHITE)
  para(d,'Researchers reported a smaller attentional blink after intensive meditation training.',570,WHITE,25,435,49,11)
  d.text((49,743),'INTENSIVE TRAINING, NOT AN MP3 TRIAL',font=font(16,'bold'),fill=GOLD)
 elif number==5:
  im,d,y=base(5,'A boundary that matters','What the experiment did not test',progress)
  d.rounded_rectangle((52,398,488,482),radius=8,fill=(28,40,31),outline=(102,144,106),width=2)
  d.text((75,421),'ATTENTION EXPERIMENT',font=font(23,'bold'),fill=WHITE)
  d.line((73,523,469,523),fill=GOLD,width=7)
  d.rounded_rectangle((52,560,488,668),radius=8,fill=(42,29,26),outline=(138,76,64),width=2)
  para(d,'No named commercial audio product was evaluated.',590,WHITE,23,376,76,8)
 elif number==6:
  im,d,y=base(6,'Evidence before the offer','Original educational research film · 40 seconds',progress)
  d.rounded_rectangle((91,392,449,642),radius=12,fill=PANEL,outline=LINE,width=2)
  d.line((130,457,410,457),fill=GOLD,width=4)
  d.line((130,497,379,497),fill=SOFT,width=3)
  d.line((130,537,394,537),fill=SOFT,width=3)
  d.line((130,577,355,577),fill=SOFT,width=3)
  para(d,'Test preferences for free. Read the actual studies.',680,WHITE,25,423,55,12)
 return im

if __name__=='__main__':
 cuts=[0,6,13,20,27,34,40]
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-vcodec','libx264','-preset','fast','-crf','26','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'attentional-blink-40s.mp4')]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 for index in range(FPS*SEC):
  seconds=index/FPS
  segment=next(k for k in range(6) if cuts[k]<=seconds<cuts[k+1])
  t=(seconds-cuts[segment])/(cuts[segment+1]-cuts[segment])
  proc.stdin.write(scene(segment+1,t).tobytes())
 proc.stdin.close(); rc=proc.wait()
 if rc: raise RuntimeError(f'ffmpeg exited {rc}')
 scene(1,.5).save(OUT/'attentional-blink-poster.png')
 for k in range(1,7):scene(k,.5).save(OUT/f'qa-scene-{k}.png')
 print('Rendered',OUT/'attentional-blink-40s.mp4')
