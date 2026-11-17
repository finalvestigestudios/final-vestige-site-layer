from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import tempfile

from bs4 import BeautifulSoup

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
UPSTREAM = HERE.parents[2] / 'checkout_r426' / 'experience2' / 'apollo-r426'
PHP = ROOT / 'staging-source-chain.php'
ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
EXPECTED = {
    'staging-source-comparison.php': '36ecba01c84d13bf2546d0bd650e9f95ac50d7d9',
    'assets/source-comparison.css': 'e76decc769e811a59f71c1cf459478d747676eb3',
}

def php_eval(code: str) -> str:
    r = subprocess.run(['php', '-r', code], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout

def test_php_lint():
    r = subprocess.run(['php', '-l', str(PHP)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr

def test_original_upstream_byte_identity():
    for relative, expected in EXPECTED.items():
        b = (UPSTREAM / relative).read_bytes()
        assert hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest() == expected

def test_fallback_default_and_no_wp():
    script = f'define("ABSPATH",1);require "{PHP}";echo fv_r427_shortcode();'
    out = php_eval(script)
    assert ARTICLE in out and '<img' not in out and out.count(ARTICLE) == 1

def test_fallback_mismatched_stage_and_page():
    stub = f'define("ABSPATH",1);define("FV_R427_ENABLED",true);define("FV_R427_STAGING_PAGE_ID",427);function wp_get_environment_type(){{return "production";}}function is_singular(){{return true;}}function get_queried_object_id(){{return 427;}}require "{PHP}";echo fv_r427_shortcode();'
    assert 'viewer unavailable' in php_eval(stub)
    stub = stub.replace('return "production"','return "staging"').replace('return 427;}require','return 428;}require')
    assert 'viewer unavailable' in php_eval(stub)

def test_upstream_integrity_rejects_mutations_and_symlink():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d) / 'reviewed'
        (root/'assets').mkdir(parents=True)
        for name in EXPECTED:
            target=root/name;target.write_bytes((UPSTREAM/name).read_bytes())
        prefix = f'define("ABSPATH",1);require "{PHP}";'
        assert php_eval(prefix + f'echo fv_r427_valid_upstream("{root}")?"PASS":"FAIL";') == 'PASS'
        (root/'assets/source-comparison.css').write_text('/* altered CSS */')
        assert php_eval(prefix + f'echo fv_r427_valid_upstream("{root}")?"PASS":"FAIL";') == 'FAIL'
        (root/'assets/source-comparison.css').write_bytes((UPSTREAM/'assets/source-comparison.css').read_bytes())
        (root/'staging-source-comparison.php').write_text('<?php // tampered')
        assert php_eval(prefix + f'echo fv_r427_valid_upstream("{root}")?"PASS":"FAIL";') == 'FAIL'
        (root/'staging-source-comparison.php').unlink()
        (root/'staging-source-comparison.php').symlink_to(UPSTREAM/'staging-source-comparison.php')
        assert php_eval(prefix + f'echo fv_r427_valid_upstream("{root}")?"PASS":"FAIL";') == 'FAIL'

def test_exact_php_render_real_component():
    html = subprocess.check_output(['php', str(HERE/'render_fixture.php')], text=True)
    soup=BeautifulSoup(html,'html.parser')
    roots=soup.select('[data-fv-r427]')
    assert len(roots)==2
    ids=[tag['id'] for tag in soup.select('[id]')]
    assert len(ids)==len(set(ids))
    for root in roots:
        assert len(root.select('.fv-r426__plate'))==6
        assert len(root.select('.fv-r426__rail li'))==3
        assert len(root.select('details'))==6
        assert len(root.select(f'a[href="{ARTICLE}"]'))==1
        assert len(root.select('img,iframe,script,form,canvas'))==0
        text=root.get_text(' ',strip=True)
        for term in ('1966-10-18','2017-01-24','1967-01-28','1968-03-14','original ignition initiator'):
            assert term in text
        assert 'NASA does not endorse Final Vestige' in text
        assert len(root.select('time[datetime]'))==9
        assert all(tag.get('href','').startswith(('https://','#')) for tag in root.select('a'))
    assert 'source-chain research viewer unavailable' not in html

def test_no_commercial_or_tracking_software():
    code='\n'.join(x.read_text() for x in [PHP,ROOT/'assets/source-chain.css'])
    assert not re.search(r'(payhip|ga4|gtag|pixel|fetch\(|XMLHttpRequest|iframe|<img|woocommerce|sponsor)',code,re.I)
    assert 'FV_R427_ENABLED' in code and 'FV_R427_STAGING_PAGE_ID' in code
    assert 'hash_equals' in code and 'is_link' in code

def test_no_invented_geo_or_merchant_source():
    code=PHP.read_text()
    assert not re.search(r'(longitude|latitude|geojson|\bmapbox\b|affiliate_id|checkout)',code,re.I)
    assert 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/' in code
