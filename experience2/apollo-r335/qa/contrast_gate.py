#!/usr/bin/env python3
"""R335 independent computed-text contrast acceptance for REAL R281 PHP/CSS.
This is not axe-core, a screen reader, installed WP, or production CWV.
"""
import hashlib, json, re, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
PHP=ROOT/'apollo-r281/apollo-source-experience.php'
CSS=ROOT/'apollo-r281/assets/apollo-source-experience.css'
HARNESS=ROOT/'apollo-r320/qa/wp_late_shortcodes.php'
OUT=ROOT/'apollo-r335/QA'
PINS={PHP:'f59a083de8d0774ed7210bfe4e18726feea73f76',
      CSS:'577a5d33518baec6e1beff1517779264d342bc50',
      HARNESS:'f8987327fd6b49afcf8996c695100e3e7471c831'}
WIDTHS=(320,360,390,768,1024,1440,1920)
COLLECT=r'''root => {
  function rgb(s){let x=s.match(/rgba?\(([^)]+)\)/);if(!x)return null;
    let vals=x[1].split(/[,\s/]+/).filter(Boolean).map(Number);return vals.length>=3?vals:null;}
  function canvas(el){while(el){let c=rgb(getComputedStyle(el).backgroundColor);
      if(c && (c.length<4 || c[3]>=.999))return c.slice(0,3); el=el.parentElement;}return [255,255,255];}
  function lum(c){return c.map(v=>{v=v/255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4);})
      .reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);}
  let nodes=[],walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
  for(let n;(n=walker.nextNode());){if(!n.textContent.trim())continue;
    let e=n.parentElement,s=getComputedStyle(e),rect=e.getBoundingClientRect();
    if(s.display==='none'||s.visibility==='hidden'||rect.width<1||rect.height<1)continue;
    let ink=rgb(s.color),ground=canvas(e),size=parseFloat(s.fontSize),weight=parseInt(s.fontWeight)||400;
    if(!ink || !ground)continue;
    let a=lum(ink),b=lum(ground),contrast=(Math.max(a,b)+.05)/(Math.min(a,b)+.05);
    let threshold=size>=24 || (size>=18.66 && weight>=700)?3:4.5;
    nodes.push({tag:e.tagName,contrast:+contrast.toFixed(3),threshold,size,weight,
      text:n.textContent.trim().slice(0,62),ink:s.color,ground:ground.join(',')});
  }
  return {nodes, horizontalOverflow:document.documentElement.scrollWidth-innerWidth,
   officialLinks:[...root.querySelectorAll('a[data-fv-link-purpose]')].length,
   ctas:[...root.querySelectorAll('a[data-fv-cta]')].length,
   media:[...root.querySelectorAll('[data-fv-media-record]')].map(x=>x.dataset.fvImageRights)};
}'''
def blob(path):
    b=path.read_bytes()
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def page_html():
    html=subprocess.check_output(['php',str(HARNESS),'late-dynamic','1'],text=True).split('<!--R320_QUEUE:',1)[0]
    return re.sub(r'<link rel="stylesheet" href="/assets/apollo-source-experience.css[^\"]*">','',html)
def audited(page):
    page.locator('details').evaluate_all('(items)=>items.forEach(e=>e.open=true)')
    return page.locator('section.fv-r281').evaluate(COLLECT)
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for f,sha in PINS.items(): assert blob(f)==sha, (str(f),blob(f),sha)
    subprocess.run(['php','-l',str(PHP)],check=True,capture_output=True)
    html=page_html();css=CSS.read_text();results=[];negative=[]
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        try:
            for js in (True,False):
                for width in WIDTHS:
                    for font in ((16,64) if width==320 else (16,)):
                        page=b.new_page(viewport={'width':width,'height':900},java_script_enabled=js,
                            reduced_motion='reduce',has_touch=width<=390,forced_colors='active' if width==390 else 'none')
                        page.set_content(html.replace('</head>',f'<style>html{{font-size:{font}px}}\n{css}</style></head>'))
                        got=audited(page)
                        assert got['horizontalOverflow']<=1,(width,font,got['horizontalOverflow'])
                        assert got['officialLinks']==17 and got['ctas']==1 and got['media']==['not-cleared-for-reuse']*4
                        assert len(got['nodes'])>160,len(got['nodes'])
                        failing=[n for n in got['nodes'] if n['contrast']+.01<n['threshold']]
                        assert not failing, (width,font,failing[:8])
                        if (width,font,js) in ((320,64,True),(390,16,False),(1440,16,True)):
                            name=f'r335-contrast-{width}-font{font}-'+('js' if js else 'nojs')+'.png'
                            page.screenshot(path=str(OUT/name),full_page=True)
                        results.append({'width':width,'rootFontPx':font,'js':js,'textNodes':len(got['nodes']),
                            'minimumContrast':min(n['contrast'] for n in got['nodes']),'failed':0})
                        page.close()
            # Adversarial real-browser test proves the detector fails a dangerously dark
            # primary source link and an almost invisible source-boundary label.
            for name,override in [('darkened-gold', '.fv-r281{--gold:#222222!important}'),
                                  ('darkened-muted','.fv-r281{--muted:#333333!important}')]:
                page=b.new_page();page.set_content(html.replace('</head>',f'<style>{css}\n{override}</style></head>'))
                check=audited(page);failing=[n for n in check['nodes'] if n['contrast']+.01<n['threshold']]
                assert failing,(name,'contrast gate failed open')
                negative.append({'mutation':name,'detected':True,'failingNodes':len(failing)})
                page.close()
        finally:b.close()
    rec={'sprint':'R335','status':'STAGING ONLY, NOT LIVE','render':'real R281 PHP in WordPress stub',
         'browser':'Chromium (offline HTML fixture)','contexts':len(results),'tests':results,
         'negativeControls':negative,'sourceBlobs':{str(k.relative_to(ROOT)):v for k,v in PINS.items()},
         'axeCore':'NOT EXECUTED','screenReader':'NOT EXECUTED','otherBrowsers':'NOT EXECUTED',
         'installedWordPress':False,'nativeHttpCsp':'NOT EXECUTED','productionLCP':None,'productionCLS':None,
         'realizedNetRevenuePer1000QualifiedSessions':None,'release':'HARD HOLD'}
    (OUT/'r335-result.json').write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n')
    print('PASS R335',len(results),'actual Chromium configurations;',sum(x['textNodes'] for x in results),'computed text-node contrast checks;',len(negative),'unsafe mutations detected')
if __name__=='__main__':main()
