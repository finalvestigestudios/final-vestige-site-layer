#!/usr/bin/env python3
"""Evidence-based, fail-closed media admission for FV EX2 protected review.

No network calls or CMS writes. Original image sizes in WP metadata are NOT proof
of browser transfer; success requires independently collected bytes and network
provenance, verified against published attachment dimensions and file types.
"""
import argparse, hashlib, json, pathlib, sys, unittest, io, copy
from html.parser import HTMLParser
from urllib.parse import urlparse

class ArchiveParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.images=[]; self.links=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='img' and 'data-fv-archive-img' in a:self.images.append(a)
        if tag=='a' and 'href' in a:self.links.append(a['href'])

def validate(html, ledger):
    p=ArchiveParser();p.feed(html)
    faults=[]; expected=[a for a in ledger['assets'] if a['in_preview']]
    allowed={a['src']:a for a in expected}
    if len(p.images)!=len(expected):faults.append('IMAGE_COUNT_DRIFT')
    seen=[]
    for img in p.images:
        src=img.get('src',''); a=allowed.get(src)
        if a is None:faults.append('UNREVIEWED_IMAGE_SOURCE');continue
        seen.append(src)
        if img.get('alt','').find(a['alt_contains'])<0:faults.append('ALT_TEXT_SOURCE_DRIFT:'+a['key'])
        if str(img.get('width'))!=str(a['width']) or str(img.get('height'))!=str(a['height']):faults.append('DIMENSION_DRIFT:'+a['key'])
        if not img.get('loading')=='lazy':faults.append('IMAGE_LOADING_POLICY_DRIFT:'+a['key'])
        sources=img.get('srcset','').split(',')
        if not sources:faults.append('MISSING_RESPONSIVE_VARIANTS:'+a['key'])
        for var in sources:
            url=var.strip().split()[0] if var.strip() else ''
            host=urlparse(url).hostname
            if host not in ('i0.wp.com','finalvestige.com') or a['file'] not in url:
                faults.append('UNREVIEWED_SRCSET_VARIANT:'+a['key'])
        if a['primary_evidence'] not in p.links:faults.append('MISSING_PRIMARY_SOURCE_LINK:'+a['key'])
    if len(set(seen))!=len(expected):faults.append('DUPLICATED_OR_MISSING_ARCHIVE_IMAGE')
    for a in ledger['assets']:
        if not a['rights_source'].startswith('https://'):faults.append('NO_RIGHTS_SOURCE:'+a['key'])
        if a['key']=='nypl_map' and a['in_preview']:faults.append('NYPL_NOT_CLEARED_FOR_PREVIEW')
    return sorted(set(faults)),{'preview_images':len(p.images),'expected_preview_images':len(expected),
                               'source_links':len(p.links),'wp_media_records':len(ledger['assets'])}

def verify_transfers(ledger, transfer_dir, receipts_file):
    """Validates local byte integrity only; receipts require independent network proof."""
    problems=[];verified=[]
    if not transfer_dir or not receipts_file or not receipts_file.is_file():
        return [],['NETWORK_BYTES_NOT_SUPPLIED']
    try: receipts=json.loads(receipts_file.read_text())
    except Exception:return [],['INVALID_NETWORK_RECEIPTS']
    for a in (a for a in ledger['assets'] if a['in_preview']):
        r=receipts.get(a['key'],{}); p=transfer_dir/a['file']
        if not p.is_file():problems.append('MISSING_BYTES:'+a['key']);continue
        data=p.read_bytes();digest=hashlib.sha256(data).hexdigest()
        if (r.get('source_url')!=a['src'] or r.get('http_status')!=200 or
            r.get('sha256')!=digest or r.get('received_bytes')!=len(data)):
            problems.append('NETWORK_PROVENANCE_UNMATCHED:'+a['key']);continue
        if len(data)!=a['bytes_wp_metadata']:
            problems.append('WP_FILESIZE_UNMATCHED:'+a['key']);continue
        magic=(data[:2]==b'\xff\xd8') if a['mime']=='image/jpeg' else (data[:4]==b'RIFF' and data[8:12]==b'WEBP')
        if not magic:problems.append('IMAGE_SIGNATURE_UNMATCHED:'+a['key']);continue
        try:
            from PIL import Image
            with Image.open(io.BytesIO(data)) as im:
                if im.size != (a['width'],a['height']):problems.append('IMAGE_DECODE_SIZE_UNMATCHED:'+a['key']);continue
                im.verify()
        except Exception:
            problems.append('IMAGE_DECODE_FAILED:'+a['key']);continue
        verified.append({'key':a['key'],'sha256':digest,'bytes':len(data)})
    return verified,problems

class Controls(unittest.TestCase):
    def setUp(self):
        self.ledger={'assets':[{'key':'apollo_1','in_preview':True,'src':'https://finalvestige.com/wp-content/uploads/test.jpg','alt_contains':'Apollo 1','width':10,'height':20,'file':'test.jpg','mime':'image/jpeg','bytes_wp_metadata':2,'primary_evidence':'https://nasa.gov/test','rights_source':'https://nasa.gov/rights'}]}
        self.img='<a href="https://nasa.gov/test">source</a><img src="https://finalvestige.com/wp-content/uploads/test.jpg" data-fv-archive-img alt="Apollo 1" width="10" height="20" loading="lazy" srcset="https://i0.wp.com/test.jpg 300w">'
    def test_valid_structure(self):self.assertFalse(validate(self.img,self.ledger)[0])
    def test_added_unreviewed_image(self):self.assertIn('IMAGE_COUNT_DRIFT',validate(self.img+self.img,self.ledger)[0])
    def test_swapped_source(self):self.assertIn('UNREVIEWED_IMAGE_SOURCE',validate(self.img.replace('src="https://finalvestige.com/wp-content/uploads/test.jpg"','src="https://evil.example/test.jpg"'),self.ledger)[0])
    def test_no_source_link(self):self.assertIn('MISSING_PRIMARY_SOURCE_LINK:apollo_1',validate(self.img.replace('https://nasa.gov/test','https://example.com/other'),self.ledger)[0])
    def test_alt_drift(self):self.assertIn('ALT_TEXT_SOURCE_DRIFT:apollo_1',validate(self.img.replace('alt="Apollo 1"','alt="Decoration"'),self.ledger)[0])
    def test_dimensions(self):self.assertIn('DIMENSION_DRIFT:apollo_1',validate(self.img.replace('height="20"','height="21"'),self.ledger)[0])
    def test_srcset_host(self):self.assertIn('UNREVIEWED_SRCSET_VARIANT:apollo_1',validate(self.img.replace('https://i0.wp.com/test.jpg','https://bad.example/test.jpg'),self.ledger)[0])
    def test_byte_absence_fail_closed(self):self.assertEqual(verify_transfers(self.ledger,None,None)[1],['NETWORK_BYTES_NOT_SUPPLIED'])
    def test_false_receipt_rejected(self):
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            d=pathlib.Path(t);(d/'test.jpg').write_bytes(b'xx');(d/'receipts.json').write_text(json.dumps({'apollo_1':{'http_status':200,'source_url':'https://finalvestige.com/wp-content/uploads/test.jpg','sha256':'bogus','received_bytes':2}}))
            self.assertTrue(verify_transfers(self.ledger,d,d/'receipts.json')[1])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--ledger',type=pathlib.Path,required=True);ap.add_argument('--html',type=pathlib.Path,required=True);ap.add_argument('--transfer-dir',type=pathlib.Path);ap.add_argument('--receipts',type=pathlib.Path);ap.add_argument('--report',type=pathlib.Path);ap.add_argument('--self-test',action='store_true');args=ap.parse_args()
    if args.self_test:
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(Controls)
        result=unittest.TextTestRunner(verbosity=1).run(suite)
        if not result.wasSuccessful():return 1
    ledger=json.loads(args.ledger.read_text());faults,summary=validate(args.html.read_text(),ledger)
    verified,missing=verify_transfers(ledger,args.transfer_dir,args.receipts)
    report={'source_integrity': 'PASS' if not faults else 'FAIL','source_problems':faults,'structure':summary,
            'binary_transfer': 'VERIFIED_LOCAL_RECEIPTS_NOT_PRODUCTION_CERTIFICATION' if not missing else 'BLOCKED',
            'binary_problems':missing,'locally_checked_media':verified,'word_press_core_execution':'NOT_TESTED',
            'rights_scope':'Editorial only; US-specific NYPL status; NASA no endorsement; no worldwide or commercial clearance assertion',
            'release_decision':'HOLD'}
    text=json.dumps(report,indent=2);print(text)
    if args.report:args.report.write_text(text+'\n')
    return 1 if faults else 2 if missing else 0
if __name__=='__main__':sys.exit(main())
