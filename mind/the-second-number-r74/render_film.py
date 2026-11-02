"""Final Vestige Mind R74: original silent 40-second vertical educational animation.
No experimental footage, product endorsement, licensed media or embedded tracking.
Run: python render_film.py; requires Pillow and ffmpeg, ffprobe for checks.
"""
from pathlib import Path
import subprocess, math, zipfile, shutil, json
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parent
W,H,FPS,FRAMES=540,960,12,480
COL = {'bg':'#090e10','gold':'#c9a16b','white':'#f7eee1','pale':'#cfc7b6','edge':'#64513a','panel':'#142023','red':'#d39076'}
STORY = [
('TWO NUMBERS.','ONE RAPID STREAM.','Which will you remember?', ['7','2','X']),
('THE FIRST','HOLDS YOUR ATTENTION.','The next arrives just afterward.', ['7','→','2']),
('THE SECOND','CAN GO UNREPORTED.','At some delays, even when it was on screen.', ['7','?','2']),
('CHANGE THE TIMING.','CHANGE THE REPORT.','This is a measured task effect—not magic.', ['1','—','2']),
('THREE MONTHS','IS NOT 12 MINUTES.','Intensive practice research is not a product trial.', ['90','≠','12']),
('OBSERVATION','IS NOT EXPLANATION.','Follow the evidence. Final Vestige Studios.', ['?','→','!'])
]
DURS = [80,80,80,80,80,80]
font_paths=['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']
def font(sz,bold=False):
    path=font_paths[1 if bold else 0]
    return ImageFont.truetype(path,sz)
def fit(draw,msg,maxw,maxsz,minsz=24,bold=False):
    for s in range(maxsz,minsz-1,-1):
        f=font(s,bold)
        if draw.textbbox((0,0),msg,font=f)[2] <= maxw: return f
    return font(minsz,bold)
def center(draw,msg,y,sz=45,color=None,bold=True):
    f=fit(draw,msg,W-58,sz,24,bold)
    box=draw.textbbox((0,0),msg,font=f)
    draw.text(((W-(box[2]-box[0]))/2,y),msg,font=f,fill=color or COL['white'])
def render_frame(frame):
    scene=min(5,frame//80)
    within=frame%80
    a,b,desc,symbols=STORY[scene]
    im=Image.new('RGB',(W,H),COL['bg']);d=ImageDraw.Draw(im)
    d.line((24,78,W-24,78),fill=COL['gold'],width=2)
    d.text((30,34),'FINAL VESTIGE  /  MIND',font=font(18,True),fill=COL['gold'])
    d.text((W-91,37),f'{scene+1:02d} / 06',font=font(15),fill=COL['pale'])
    center(d,a,137,48,color=COL['white'])
    center(d,b,206,45,color=COL['gold'])
    # Original symbolic design; no visual content from the original studies.
    d.rounded_rectangle((39,322,501,725),radius=20,fill=COL['panel'],outline=COL['edge'],width=2)
    for x in (130,270,410):d.ellipse((x-70,426,x+70,566),outline=COL['edge'],width=2)
    for i,(x,symbol) in enumerate(zip((130,270,410),symbols)):
        c=COL['white'] if i==0 else COL['gold'] if i==2 else COL['pale']
        if scene==2 and i==2:
            # A translucent-looking obstruction illustrates uncertain report, not literal invisibility.
            c=COL['edge'] if within<48 else COL['gold']
        d.text((x,495),symbol,font=font(78,True),fill=c,anchor='mm')
    d.line((50,638,490,638),fill=COL['edge'],width=2)
    d.text((70,660),'AN ILLUSTRATION, NOT A TEST',font=font(16),fill=COL['pale'])
    # Use word wrap for legibility on mobile, keep within video safe area.
    words=desc.split();rows=[];current=''
    for word in words:
        tentative=(current+' '+word).strip()
        if d.textbbox((0,0),tentative,font=font(24))[2]>W-66 and current:
            rows.append(current);current=word
        else: current=tentative
    if current: rows.append(current)
    for i,line in enumerate(rows):center(d,line,771+i*34,24,color=COL['pale'],bold=False)
    d.line((24,898,W-24,898),fill=COL['gold'],width=2)
    d.text((28,910),'THE SECOND NUMBER  ·  40 SECOND EXPLAINER',font=font(15),fill=COL['gold'])
    return im

def make():
    video=ROOT/'the-second-number-40s.mp4'
    cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','-','-an','-c:v','libx264','-pix_fmt','yuv420p','-preset','fast','-crf','31','-movflags','+faststart',str(video)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for f in range(FRAMES):p.stdin.write(render_frame(f).tobytes())
        p.stdin.close()
        err=p.stderr.read().decode('utf-8','replace')
        if p.wait()!=0:raise RuntimeError(err)
    finally:
        if p.poll() is None:p.kill()
    render_frame(0).save(ROOT/'poster.png')
    thumbs=[render_frame(n*80+36).resize((216,384)) for n in range(6)]
    sheet=Image.new('RGB',(216*3,384*2))
    for n,thumb in enumerate(thumbs):sheet.paste(thumb,((n%3)*216,(n//3)*384))
    sheet.save(ROOT/'contact-sheet.png')
    vtt='''WEBVTT\n\n00:00:00.000 --> 00:00:06.600\nTwo numbers. One rapid stream. Which will you remember?\n\n00:00:06.600 --> 00:00:13.300\nThe first target catches your attention. The next arrives just afterward.\n\n00:00:13.300 --> 00:00:20.000\nAt certain delays, people may miss the second target—even while looking at the screen.\n\n00:00:20.000 --> 00:00:26.600\nChange the timing or instructions, and the missing target may reappear in reports.\n\n00:00:26.600 --> 00:00:33.300\nMonths of intensive meditation training changed a laboratory measure in one small study. That is not proof of any audio product.\n\n00:00:33.300 --> 00:00:40.000\nPerception is evidence. Explanation takes another step. Explore the sources at Final Vestige.\n'''
    (ROOT/'captions.vtt').write_text(vtt,encoding='utf-8')
    (ROOT/'review-player.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Final Vestige R74 video review only</title><style>body{font:1.1rem/1.6 system-ui;color:#f6f0e7;background:#090e10;max-width:800px;margin:auto;padding:20px}video{width:min(100%,480px);height:auto}a{color:#edc995}video:focus{outline:3px solid #edc995}</style><h1>The Second Number (offline review)</h1><p>Original silent explanatory artwork, not a laboratory demonstration or Zen12 endorsement. Video is not on WordPress.</p><video controls preload="none" playsinline poster="poster.png"><source src="the-second-number-40s.mp4" type="video/mp4"><track default kind="captions" srclang="en" label="English captions" src="captions.vtt">Your browser cannot play this video. See the captions file.</video><p>Complete text is provided by captions.vtt. Use native keyboard controls. No autoplay, remote embed, cookies or tracking.</p></html>''',encoding='utf-8')
    out=ROOT/'offline-review.zip'
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for item in ['the-second-number-40s.mp4','poster.png','contact-sheet.png','captions.vtt','review-player.html','render_film.py']:
            z.write(ROOT/item,arcname=item)
    assert zipfile.ZipFile(out).testzip() is None
    probe=subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=codec_name,width,height,avg_frame_rate,nb_read_frames','-show_entries','format=duration,size','-of','json',str(video)],text=True)
    pinfo=json.loads(probe)
    assert abs(float(pinfo['format']['duration'])-40)<.05,pinfo
    assert pinfo['streams'][0]['codec_name']=='h264'
    assert pinfo['streams'][0]['width']==540 and pinfo['streams'][0]['height']==960
    assert int(pinfo['streams'][0]['nb_read_frames'])==480
    print(json.dumps({'video':str(video),'probe':pinfo,'zip':str(out),'zip_integrity':'PASS'},indent=2))
if __name__=='__main__':make()
