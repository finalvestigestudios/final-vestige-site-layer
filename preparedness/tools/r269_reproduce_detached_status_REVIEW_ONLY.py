#!/usr/bin/env python3
"""Manual OFFLINE Chromium source/print review; no publishing or QD certification.
Usage: python -I preparedness/tools/r269_reproduce_detached_status_REVIEW_ONLY.py --output /tmp/r269-unique-empty-folder
Requires local Playwright, Chromium, pdfinfo and pdftotext. Output outside repository.
"""
from __future__ import annotations
import argparse
import asyncio
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
GATE=ROOT/'tools/r269_cutout_review_status_hold.py'
WIDTHS=(320,360,390,768,1440)
LABEL='UNAPPROVED - DO NOT USE'

def safe_dir(out):
    out=out.resolve()
    if out==ROOT or ROOT in out.parents:raise ValueError('evidence output inside source forbidden')
    out.mkdir(parents=True,exist_ok=True)
    if any(out.iterdir()):raise ValueError('refuse to overwrite prior evidence')
    return out

def require(value,msg):
    if not value:raise ValueError('R269 review reproduction FAILED: '+msg)

async def run(output,chromium):
    spec=importlib.util.spec_from_file_location('r269_review',GATE)
    gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
    old=(ROOT/gate.OLD_PATH).read_bytes();new=(ROOT/gate.NEW_PATH).read_bytes()
    gate.inspect(old,new)
    report={'state':'DRAFT_HARD_HOLD','original_git_blob':gate.OLD_BLOB,
            'candidate_git_blob':gate.NEW_BLOB,'screens':{},'prints':{},
            'independent_qd_pass':False,'privacy_approved':False,
            'physical_cutout_approved':False,'public_published':False,
            'full_native_pipeline_executed':False,'release_authorized':False}
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path=chromium,headless=True,args=['--no-sandbox'])
        try:
            report['chromium_version']=browser.version
            for width in WIDTHS:
                ctx=await browser.new_context(viewport={'width':width,'height':900},java_script_enabled=False)
                await ctx.route('**/*',lambda route:route.abort())
                page=await ctx.new_page();await page.set_content(new.decode('utf-8'))
                d=await page.evaluate('''() => ({
                    document_width:document.documentElement.scrollWidth,
                    viewport_width:innerWidth,
                    card_width:document.querySelector('.pa-foldcard').getBoundingClientRect().width,
                    labels:[...document.querySelectorAll('.pa-face > .pa-prototype-status')].map(x=>({text:x.textContent.trim(),hidden:getComputedStyle(x).display==='none',font:getComputedStyle(x).fontSize}))
                })''')
                require(d['document_width']<=width+1,'mobile overflow '+str(width))
                require(len(d['labels'])==2 and all(x['text']==LABEL and not x['hidden'] for x in d['labels']),'screen badges missing')
                report['screens'][width]=d
                await page.screenshot(path=str(output/f'candidate_{width}.png'),full_page=True)
                await ctx.close()
            for js in (False,True):
                ctx=await browser.new_context(viewport={'width':390,'height':900},java_script_enabled=js)
                await ctx.route('**/*',lambda route:route.abort())
                page=await ctx.new_page();await page.set_content(new.decode('utf-8'))
                await page.emulate_media(media='print')
                d=await page.evaluate('''() => {
                    const rect = el => { const x=el.getBoundingClientRect();return {x:x.x,y:x.y,w:x.width,h:x.height,bottom:x.bottom,right:x.right}};
                    const card=document.querySelector('.pa-foldcard');const faces=[...document.querySelectorAll('.pa-face')];
                    return {card:rect(card),faces:faces.map(rect),
                        labels:faces.map(f=>rect(f.querySelector(':scope > .pa-prototype-status'))),
                        label_fonts:faces.map(f=>getComputedStyle(f.querySelector(':scope > .pa-prototype-status')).fontSize),
                        texts:faces.map(f=>f.innerText),
                        children_inside_faces:faces.map(f=>[...f.children].every(c=>{const a=c.getBoundingClientRect(),b=f.getBoundingClientRect();return a.x>=b.x-1&&a.right<=b.right+1&&a.y>=b.y-1&&a.bottom<=b.bottom+1}))}
                }''')
                require(abs(d['card']['w']-672)<1,'card width not 7in')
                require(203<=d['card']['h']<=225,'card height drift')
                require(len(d['faces'])==2 and len(d['labels'])==2,'faces or labels missing')
                require(all(d['children_inside_faces']),'printed content clipped outside face')
                for face,lab in zip(d['faces'],d['labels']):
                    require(lab['x']>=face['x']-1 and lab['right']<=face['right']+1 and
                            lab['y']>=face['y']-1 and lab['bottom']<=face['bottom']+1,
                            'print badge outside cutout')
                require(all('10.666' in f or f=='10.6667px' for f in d['label_fonts']),
                        'print badge not 8pt')
                raw=await page.pdf(format='Letter',print_background=True)
                fn=output/f'candidate_js_{int(js)}.pdf';fn.write_bytes(raw)
                info=subprocess.check_output(['pdfinfo',str(fn)],text=True)
                counts=[int(row.split(':',1)[1]) for row in info.splitlines() if row.startswith('Pages:')]
                require(counts==[1],'PDF page count != 1')
                text=subprocess.check_output(['pdftotext','-raw',str(fn),'-'],text=True)
                require(text.count(LABEL)==2,'detached review label not in PDF twice')
                for s in ('Privacy: This card may be lost','Privacy: A finder can read',
                          'Out-of-area contact:','Telephone:','Backup contact:','Backup telephone:','Plan reviewed:'):
                    require(s in text,'printed privacy/field lost '+s)
                report['prints'][str(js)]={**d,'page_count':counts[0],
                          'badge_text_count_in_pdf':text.count(LABEL),
                          'pdf_sha256':hashlib.sha256(raw).hexdigest()}
                await ctx.close()
        finally:await browser.close()
    for field in ('card','faces','labels','label_fonts','texts','children_inside_faces','page_count','badge_text_count_in_pdf'):
        require(report['prints']['False'][field]==report['prints']['True'][field],
                'JS print parity changed: '+field)
    report['bounded_browser_status_within_cutout_observed']=True
    report['physical_print_cut_fold_not_tested']=True
    (output/'r269_review_observation.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

def main():
    a=argparse.ArgumentParser();a.add_argument('--output',required=True,type=Path)
    a.add_argument('--chromium',default=shutil.which('chromium') or '/usr/bin/chromium')
    args=a.parse_args()
    out=safe_dir(args.output)
    report=asyncio.run(run(out,args.chromium))
    print(json.dumps({'state':report['state'],'chromium':report['chromium_version'],
       'widths':{k:v['document_width'] for k,v in report['screens'].items()},
       'print_heights':{k:v['card']['h'] for k,v in report['prints'].items()},
       'status_on_each_face':report['bounded_browser_status_within_cutout_observed']}))
if __name__=='__main__':main()
