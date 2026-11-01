#!/usr/bin/env python3
"""R47: actual Chromium / PHP shortcode set_content; NOT real WordPress HTTP."""
import sys,hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_r46_pair_smoke import fixture

def run():
    html=fixture();seen=[]
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for width in (320,360,390,768,1024,1440,1920):
            for js in (False,True):
                c=b.new_context(viewport={'width':width,'height':900},java_script_enabled=js,
                    is_mobile=width<=390,has_touch=width<=390,reduced_motion='reduce',accept_downloads=True)
                pg=c.new_page();errors=[];requests=[]
                pg.on('pageerror',lambda e:errors.append(str(e)))
                pg.on('request',lambda r:requests.append(r.url))
                pg.set_content(html)
                assert not errors and not requests
                assert pg.locator('[data-fva-record]:visible').count()==6
                assert pg.locator('[data-fva-citation-text]:visible').count()==6
                assert not pg.evaluate('document.documentElement.scrollWidth>innerWidth+2')
                assert pg.locator('[data-fva-export]').is_visible()==js
                if js:
                    pg.locator('[data-fva-filter="2017"]').click()
                    with pg.expect_download() as d:pg.locator('[data-fva-export]').click()
                    download=d.value
                    assert download.suggested_filename=='apollo-1-nasa-source-register.txt'
                    raw=Path(download.path()).read_bytes()
                    assert raw.count(b'https://www.nasa.gov/image-detail/')==6
                    assert raw.count(b'individual review required.')==6
                    assert b'S67-19766 has no independently verified day' in raw
                    assert pg.locator('[data-fva-record]:visible').count()==2
                    seen.append(hashlib.sha256(raw).hexdigest())
                c.close()
        assert len(set(seen))==1
        c=b.new_context();pg=c.new_page();pg.set_content(html)
        pg.locator('[data-fva-citation-text]').first.evaluate('(x)=>x.textContent="tampered"')
        pg.locator('[data-fva-export]').click()
        assert 'Download unavailable' in pg.locator('[data-fva-export-status]').inner_text()
        assert pg.locator('[data-fva-record]:visible').count()==6
        c.close();b.close()
    print('PASS 14 Chromium combinations + tamper; 7 byte-identical six-record exports')

if __name__=='__main__':run()
