#!/usr/bin/env python3
"""R192: independent real Chromium PDF custody acceptance of R191 PHP-rendered Atlas.

Offline set_content only (no real navigation, live WP, or axe); actual page.pdf and
PDF parser verify selectable source URLs, annotation targets, print readability,
text geometry, and the one free CTA. Deterministic raster receipts and controls.
"""
import asyncio
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import fitz
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
DEST = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
EXPECTED = (
 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/',
 'https://www.nasa.gov/image-detail/amf-s66-58038/',
 'https://www.nasa.gov/image-detail/amf-s67-15717/',
 'https://www.nasa.gov/humans-in-space/55-years-ago-final-preparations-for-the-planned-launch-of-apollo-1/',
 'https://www.nasa.gov/image-detail/amf-s67-21294/',
 'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/',
 'https://www.nasa.gov/mission/apollo-1/',
 'https://www.nasa.gov/nasa-brand-center/advertising-guidelines/',
)


def sha(data):
 return hashlib.sha256(data).hexdigest()


def parent_markup():
 data = json.loads(subprocess.check_output([
  'php', str(ROOT/'qa/wp_render_shim.php'), str(ROOT/'dist/fv-ex2-apollo-r191.php')], text=True))
 assert not data['fallback'] and data['chronology'] == 4 and data['details'] == 8
 assert data['css'] == 'enqueued'
 css = (ROOT/'dist/assets/atlas-scoped.css').read_text()
 return data['html'], css


def full_document(markup, css):
 return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
  '<meta name="viewport" content="width=device-width,initial-scale=1">'
  '<title>Apollo source-custody PDF acceptance fixture</title><style>' + css
  + '</style></head><body>' + markup + '</body></html>')


def inspect_pdf(content, source_urls=EXPECTED):
 """Raises on missing link annotation or invisible/missing printed source text."""
 doc = fitz.open(stream=content, filetype='pdf')
 if not (2 <= len(doc) <= 12):
  raise AssertionError('Unexpected printed page count')
 pages = [p.get_text() for p in doc]
 text = '\n'.join(pages)
 flat = re.sub(r'\s+', '', text)
 links = [l.get('uri') for p in doc for l in p.get_links() if l.get('uri')]
 targets = set(links)
 for dest in source_urls:
  assert dest in targets, 'Missing clickable official PDF source: '+dest
  assert re.sub(r'\s+', '', dest) in flat, 'Missing visible literal source: '+dest
 assert DEST in targets, 'Missing clickable free original investigation CTA'
 assert 'Archival source and rights index' in text, 'Missing print-source appendix'
 assert 'No astronaut endorsement' in text, 'Missing non-endorsement caution'
 assert 'No conclusively identified ignition source' in ' '.join(text.split()), 'Lost uncertainty statement'
 assert 'Read original investigation' in text, 'Missing original investigation action'
 assert 'A fire. A record.' in text, 'Missing historical introduction'
 assert sum('Archival source and rights index' in x for x in pages) == 1
 assert all(len(x.strip()) >= 150 for x in pages), 'Blank or near-blank printed sheet'
 clipped=[]
 for i, p in enumerate(doc):
  for block in p.get_text('dict')['blocks']:
   for line in block.get('lines',[]):
    for span in line['spans']:
     rect=fitz.Rect(span['bbox'])
     if not p.rect.contains(rect):
      clipped.append([i+1,span['text'][:48],list(rect)])
 assert not clipped, 'Text outside PDF page: '+repr(clipped[:3])
 return {'pages':len(doc),'visible_official_source_urls':len(source_urls),
         'clickable_official_targets':len(set(source_urls)&targets),
         'clickable_original_cta':DEST in targets,
         'pdf_link_annotation_count':len(links),'offpage_text_spans':len(clipped),
         'page_text_lengths':[len(x) for x in pages]}


async def run(out):
 out.mkdir(parents=True, exist_ok=True)
 markup,css=parent_markup()
 doc=full_document(markup,css)
 checks=[]
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  try:
   for width in (390,1440):
    context=await browser.new_context(viewport={'width':width,'height':900},
                                      java_script_enabled=False, device_scale_factor=1)
    page=await context.new_page()
    await page.set_content(doc)
    actual=await page.pdf(format='A4',print_background=True,prefer_css_page_size=True)
    assert await page.locator('.fv-apollo-print-custody').count() == 1
    p=out/f'apollo-{width}.pdf';p.write_bytes(actual)
    proof=inspect_pdf(actual)
    file=fitz.open(stream=actual,filetype='pdf')
    rasters={}
    for index in (0,3,len(file)-1):
     label=f'page-{index+1}'
     picture=file[index].get_pixmap(matrix=fitz.Matrix(1.25,1.25),alpha=False)
     payload=picture.tobytes('png')
     (out/f'apollo-{width}-{label}.png').write_bytes(payload)
     rasters[label]=sha(payload)
    checks.append({'width':width,'pdf_sha256':sha(actual),
                   'raster_sha256':rasters,'checks':proof})
    await context.close()
  finally:
   await browser.close()
 receipt={'scope':'Chromium page.pdf of real PHP-shortcode output in offline set_content fixture; not installed WordPress, real navigation, or axe',
  'parent_php_git_blob':'e34ec79947034fa5fb1b63f4ddd7b0cd897a32f1',
  'parent_generator_git_blob':'7688d9db57227bada525e4fc0a1f6ffafb1049f5',
  'no_js':True,'real_print_pdf':True,'source_markup_sha256':sha(markup.encode()),
  'css_sha256':sha(css.encode()),'cases':checks,'genuine_axe':'NOT_RUN',
  'installed_wordpress':'NOT_RUN','real_browser_navigation':'BLOCKED_BY_ADMINISTRATOR',
  'lab_lcp':'NOT_AVAILABLE_WITH_SET_CONTENT','real_net_revenue':'NOT_VERIFIED'}
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
 return receipt


def negative_controls():
 markup,css=parent_markup()
 url=EXPECTED[1]
 start=markup.index('<!-- R191 print-only source custody')
 prefix,appendix=markup[:start],markup[start:]
 tampered=appendix.replace('href="'+url+'"','href="#false-source"',1)
 assert tampered != appendix
 return prefix+tampered,css


async def main():
 out=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'r192-evidence'
 result=await run(out)
 # Adversarial negative control tests the independent PDF destination validator.
 broken,css=negative_controls()
 async with async_playwright() as pw:
  b=await pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  page=await b.new_page(java_script_enabled=False)
  await page.set_content(full_document(broken,css))
  pdf=await page.pdf(format='A4',print_background=True)
  try:
   inspect_pdf(pdf)
  except AssertionError as exc:
   (out/'negative-control.txt').write_text('PASS: corrupted source annotation rejected: '+str(exc)+'\n')
  else:
   raise AssertionError('Negative control unexpectedly passed')
  await b.close()
 print(json.dumps({'cases':len(result['cases']),'pages':[x['checks']['pages'] for x in result['cases']],
                   'clickable_sources':[x['checks']['clickable_official_targets'] for x in result['cases']],
                   'negative_control':'PASS'},sort_keys=True))


if __name__=='__main__':
 asyncio.run(main())
