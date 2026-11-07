#!/usr/bin/env python3
"""R191: printed Apollo evidence retains complete, source-linked provenance without JS.

Inputs pinned to exact R190 release candidate bytes; generated shortcode is staging only.
"""
from pathlib import Path
import hashlib, html, json, re, subprocess, sys
ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent/'apollo-r190'
OUT=ROOT/'dist'
PINS={
 'php':'e99652fdfeb0a05b41b1dcb1a1dd430c19e59bc2a430827d3408242d34c72880',
 'html':'f368766a4b8058208c524f5809f975ba859a108090923de6d6d8e2b59653c315',
 'css':'dddb5a73a58d266f5d5dc67f88b7114c15fb8736134b2c345126717f91c1d7b6',
 'js':'eeab075280948b771eecd4cb13cc04ed946ffc34fc059bd6ac0d16ba555e446b',
}
PATHS={'php':'fv-ex2-apollo-r190.php','html':'templates/atlas-fragment.html',
       'css':'assets/atlas-scoped.css','js':'assets/campaign-handoff.js'}
URLS=(
 ('Technical findings 01–04 / Apollo 204 Review Board','https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'),
 ('NASA S66-58038 / pre-test preparation','https://www.nasa.gov/image-detail/amf-s66-58038/'),
 ('NASA S67-15717 / spacecraft processing','https://www.nasa.gov/image-detail/amf-s67-15717/'),
 ('NASA / January 1967 preparations','https://www.nasa.gov/humans-in-space/55-years-ago-final-preparations-for-the-planned-launch-of-apollo-1/'),
 ('NASA S67-21294 / aftermath (not ignition)','https://www.nasa.gov/image-detail/amf-s67-21294/'),
 ('NASA / 2017 commemorative exhibit','https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/'),
 ('NASA mission overview','https://www.nasa.gov/mission/apollo-1/'),
 ('NASA advertising / endorsement and likeness rules','https://www.nasa.gov/nasa-brand-center/advertising-guidelines/'),
)

def digest(data): return hashlib.sha256(data).hexdigest()
def read_parent():
    if not (PARENT/'dist'/PATHS['php']).exists():
        subprocess.run([sys.executable,str(PARENT/'build_r190.py')],check=True)
    data={k:(PARENT/'dist'/path).read_bytes() for k,path in PATHS.items()}
    for key,value in data.items():
        if digest(value)!=PINS[key]:raise ValueError('R190 parent source SHA-256 mismatch: '+key)
    return data

def build():
    data=read_parent()
    old_html=data['html'].decode('utf8')
    # All entries except the explicit policy page MUST already occur in verified R190 source.
    for title,url in URLS:
        if 'advertising-guidelines' not in url and old_html.count('href="'+url+'"')<1:
            raise ValueError('Source destination drift for '+title)
    if old_html.count('<footer class="end">')!=1:raise ValueError('Footer anchor drift')
    rows=''.join('<li><strong>'+html.escape(name)+'</strong><br><a href="'+html.escape(url,quote=True)+'" rel="noreferrer noopener">'+html.escape(url)+'</a></li>' for name,url in URLS)
    appendix=('<!-- R191 print-only source custody; visible without JS in printed output. -->'
      '<section class="fv-apollo-print-custody" aria-labelledby="fv-apollo-print-custody-title">'
      '<h2 id="fv-apollo-print-custody-title">Archival source and rights index</h2>'
      '<p>Primary technical evidence and separate photo catalog records. Photos do not independently establish ignition. '
      'No astronaut endorsement or commercial promotional rights are certified.</p><ol>'+rows+'</ol></section>')
    new_html=old_html.replace('<footer class="end">',appendix+'<footer class="end">')
    new_css=data['css'].decode('utf8')+'''\n/* R191: printing closed native <details> hides their sources in Chromium.
   This static, no-JS appendix ensures a paper/PDF copy retains source custody. */
.fv-apollo-atlas .fv-apollo-print-custody{display:none}
@media print {
 .fv-apollo-atlas .fv-apollo-print-custody{display:block;border-top:2px solid #444;padding:1.1rem 0;color:#000}
 .fv-apollo-atlas .fv-apollo-print-custody h2{font-size:1.6rem;color:#000}
 .fv-apollo-atlas .fv-apollo-print-custody li{break-inside:avoid;margin:0 0 .8rem;overflow-wrap:anywhere}
 .fv-apollo-atlas .fv-apollo-print-custody a{overflow-wrap:anywhere;color:#000;text-decoration:underline}
 .fv-apollo-atlas .fv-apollo-print-custody p{color:#000}
 /* Print must not inherit the dark-surface palette or pale accent text. */
 .fv-apollo-atlas, .fv-apollo-atlas h1, .fv-apollo-atlas h2, .fv-apollo-atlas h3,
 .fv-apollo-atlas .tag, .fv-apollo-atlas .eyebrow, .fv-apollo-atlas .intro,
 .fv-apollo-atlas .hero p, .fv-apollo-atlas .notice, .fv-apollo-atlas .small,
 .fv-apollo-atlas .source-card p, .fv-apollo-atlas .plate p,
 .fv-apollo-atlas .rail time, .fv-apollo-atlas .rail small,
 .fv-apollo-atlas summary, .fv-apollo-atlas .plate .limit,
 .fv-apollo-atlas .print-custody li {color:#000!important}
 .fv-apollo-atlas .plate .limit{background:#eee!important}
 .fv-apollo-atlas .notice{border-color:#444!important}
}
'''
    new_php=data['php'].decode('utf8').replace('r190','r191').replace('R190','R191')
    for key,new_value in (('html',new_html),('css',new_css)):
        n=new_php.count(PINS[key])
        if n!=1:raise ValueError('Expected one PHP SHA pin for '+key+', got '+str(n))
        new_php=new_php.replace(PINS[key],digest(new_value.encode('utf8')))
    assert 'e99652fd' not in new_php
    paths={'php':'fv-ex2-apollo-r191.php','html':PATHS['html'],'css':PATHS['css'],'js':PATHS['js']}
    objs={'php':new_php.encode('utf8'),'html':new_html.encode('utf8'),'css':new_css.encode('utf8'),'js':data['js']}
    for key,path in paths.items():
        dest=OUT/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(objs[key])
    receipt={'parent_pr':1411,'parent_commit':'654b36da7a3af538504be518d4fae3a7ff161ec6',
        'parent_pins':PINS,'output_sha256':{k:digest(v) for k,v in objs.items()},'printed_source_count':len(URLS),
        'release':'DRAFT / STAGING HOLD','genuine_axe':False,'installed_wordpress':False,'net_revenue_verified':False}
    (OUT/'manifest.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    return receipt

if __name__=='__main__':print(json.dumps(build(),sort_keys=True,indent=2))
