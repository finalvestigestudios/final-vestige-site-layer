#!/usr/bin/env python3
"""Offline, real-Chromium print-source custody gate; no external requests."""
from pathlib import Path
import subprocess
import fitz
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[2]
php = root/'apollo-r340/apollo-accession-gallery.php'
markup = subprocess.check_output(['php','-r',"define('ABSPATH',true); require '"+str(php)+"'; echo fv_apollo_r340_experience_shortcode();"],text=True)
css = '\n'.join((root / f).read_text() for f in (
    'apollo-r339/assets/chronology-rail.css',
    'apollo-r345/evidence-plate.css',
    'apollo-r340/assets/accession-gallery.css'))
assert markup.count('data-fv-r340-print-limit') == 4
assert markup.count('data-fv-apollo-print-custody') == 3
assert markup.count('data-fv-apollo-print-source="board"') == 3
assert markup.count('data-fv-r339-cta="editorial"') == 1
assert '<img' not in markup and 'data-geo-pin' not in markup and 'payhip.com' not in markup
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True,args=['--no-sandbox'])
    for width in (320,390,768,1440,1920):
        c=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=False)
        page=c.new_page()
        page.set_content('<html lang="en"><head><style>'+css+'</style></head><body>'+markup+'</body></html>')
        assert page.locator('.fv-apollo-r345__card').count()==3
        assert page.locator('.fv-apollo-r345__print-custody:visible').count()==0
        assert page.locator('.fv-apollo-r345__source a:visible').count()==3
        assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+1')
        pdf=page.pdf(format='A4',print_background=True)
        doc=fitz.open(stream=pdf,filetype='pdf')
        words='\n'.join(x.get_text() for x in doc)
        assert words.count('Original Board source:') == 3
        assert words.count('Record custody:') == 9
        assert words.count('Photograph evidence limitation:') == 4
        assert ' '.join(words.split()).count('Rights review required:') == 4
        assert words.count('Primary source:') == 5
        assert words.count('Later institutional source:') == 1
        links=[a.get('uri','') for x in doc for a in x.get_links() if a.get('kind')==2]
        assert sum(u.startswith('https://www.nasa.gov/') for u in links)>=17
        assert sum(u.startswith('https://finalvestige.com/') for u in links)==1
        doc.close();c.close()
    browser.close()
print('PASS: 5 Chromium widths / 5 native PDFs / 3 original Board plate custodians / 1 free CTA')
