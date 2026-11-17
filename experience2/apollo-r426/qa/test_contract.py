"""Offline source contract. Source URLs and rights must survive exactly."""
import re
import subprocess
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
PHP = ROOT / 'staging-source-comparison.php'
CSS = ROOT / 'assets/source-comparison.css'
STORY = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'

class Nodes(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]; self.ids=[]; self.times=[]; self.details=0; self.img=0
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.append(attrs['id'])
        if tag=='a':self.links.append(attrs.get('href'))
        if tag=='time':self.times.append(attrs.get('datetime'))
        if tag=='details':self.details+=1
        if tag in ('img','iframe','video','script','form'):self.img+=1

def rendered(n=1):
    return subprocess.run(['php',str(ROOT/'qa/render_fixture.php'),str(n)], check=True,capture_output=True,text=True).stdout

def parser(n=1):
    p=Nodes();p.feed(rendered(n));return p

def test_php_syntax():
    assert 'No syntax errors' in subprocess.run(['php','-l',str(PHP)],capture_output=True,text=True,check=True).stdout

def test_exact_sources_and_one_cta_per_instance():
    p=parser(1)
    assert p.links.count(STORY)==1
    assert len([x for x in p.links if x and x.startswith('https://www.nasa.gov/image-detail/')]) == 6
    assert len(set(p.links))==12 # 3 anchors + 6 NASA catalogue + report + media + story

def test_no_media_republished_or_unapproved_commerce():
    p=parser(1)
    assert p.img==0
    assert all(not any(s in (x or '').lower() for s in ('payhip','stripe','checkout','utm_')) for x in p.links)
    for s in ('NASA does not endorse','No map pins','NASA photographs are not reproduced','not conclusively'):
        assert s in rendered(1)

def test_duplicate_instance_ids():
    p=parser(2)
    assert len(p.ids)==len(set(p.ids))
    assert len([x for x in p.links if x==STORY])==2
    assert p.details==12

def test_chronological_dates_separated_from_photos():
    p=parser(1)
    assert p.times[:3]==['1967-01-27','1967','1968-03-14']
    assert p.times[3:]==['1967','1967-01-03','1966-10-18','2017-01-24','1967-01-28','2017-01-24']

def test_staging_gate_is_opt_in():
    text=PHP.read_text()
    for key in ('FV_R426_ENABLED','FV_R426_STAGING_PAGE_ID',"wp_get_environment_type() === 'staging'",'get_queried_object_id'):
        assert key in text
    cmd=['php','-r',"define('ABSPATH',true);require '"+str(PHP)+"';echo fv_r426_shortcode();"]
    assert STORY in subprocess.run(cmd,capture_output=True,text=True,check=True).stdout

def test_css_accessibility_and_no_network():
    css=CSS.read_text();src=PHP.read_text()
    assert ':focus-visible' in css and 'prefers-reduced-motion' in css and 'forced-colors' in css and '@media print' in css
    assert '<details>' in src and '<summary>' in src and '<time datetime=' in src
    assert 'wp_enqueue_script(' not in src and 'fetch(' not in src

def test_no_geographic_pins_or_excluded_homes():
    text=PHP.read_text()+CSS.read_text()
    assert 'leaflet' not in text.lower() and 'mapbox' not in text.lower() and 'google.maps' not in text.lower()
    assert 'final-vestige-site-layer' not in text.lower()
