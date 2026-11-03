from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image,ImageOps,ImageDraw,ImageFont
root=Path(__file__).resolve().parent
html=(root/'concept-board.html').read_text()
with sync_playwright() as p:
 b=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for direction in ['dossier','museum','observatory']:
  for width,height in [(1440,900),(390,844)]:
   page=b.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
   page.set_content(html)
   page.locator(f'[data-choice="{direction}"]').click()
   assert page.locator('body').get_attribute('data-direction')==direction
   page.screenshot(path=str(root/f'{direction}-{width}.png'),full_page=False)
   page.close()
 b.close()
imgs=[]
for name in ['dossier','museum','observatory']:
 img=Image.open(root/f'{name}-1440.png').convert('RGB')
 img.thumbnail((640,420))
 imgs.append(img)
w=660;h=500
canvas=Image.new('RGB',(w*3,h),(12,12,11));draw=ImageDraw.Draw(canvas)
for i,(img,name) in enumerate(zip(imgs,['A · THE BLACK DOSSIER','B · MUSEUM AFTER HOURS','C · THE OBSERVATORY'])):
 x=i*w+10
 draw.text((x,15),name,fill=(220,199,153))
 canvas.paste(img,(x,45))
canvas.save(root/'three-directions-desktop.png')
print('Rendered three desktop directions and mobile crops + contact sheet')
