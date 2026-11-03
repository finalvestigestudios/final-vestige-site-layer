#!/usr/bin/env python3
"""Apollo R98: source-identical, JS-free round-trips for six NASA records across seven views.

Isolated staging transform; NEVER a WordPress payload or publication permission.
"""
import argparse
import hashlib
import html
import json
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

VIEWS = {
    'R85_NASA_SOURCE_REVIEW.html': 'r85-source-',
    'R87_PHOTOGRAPH_DATE_RAIL.html': 'r87-record-',
    'R88_READING_ROOM.html': 'r88-',
    'R89_REVIEW_HUB.html': 'r89-source-',
    'R93_SOURCE_PASSPORTS.html': 'passport-',
    'R94_CURATED_ATLAS.html': 'atlas-',
    'R97_SOURCE_GALLERY.html': 'gallery-',
}
CSS = '''/* R98 additive navigation, scoped; no inherited page or theme overrides. */
.r98-route{display:flex;flex-wrap:wrap;align-items:center;gap:.45rem .8rem;margin:.8rem 0 0;padding:.65rem 0 0;border-top:1px solid currentColor;font:600 .86rem/1.5 system-ui,sans-serif}
.r98-route a{display:inline-flex;align-items:center;min-height:44px;min-width:44px;padding:.3rem .6rem;border:1px solid currentColor;border-radius:2px;color:inherit;text-decoration:underline;text-underline-offset:.2em;overflow-wrap:anywhere}
.r98-route a:focus-visible{outline:3px solid #f5cb81;outline-offset:3px}
.r98-route .r98-explainer{width:100%;font-weight:400;font-size:.8rem}
@media(max-width:430px){.r98-route{display:grid;grid-template-columns:1fr}.r98-route a{max-width:100%}}
@media(forced-colors:active){.r98-route a{color:LinkText;border-color:CanvasText}.r98-route a:focus-visible{outline:3px solid Highlight}}
@media(prefers-reduced-motion:reduce){.r98-route *{scroll-behavior:auto!important;transition:none!important}}
@media print{.r98-route{display:none!important}}
'''

def sha(b):
    return hashlib.sha256(b).hexdigest()

def custody(src):
    if not src.is_dir() or src.is_symlink():
        raise ValueError('R98_SOURCE_DIRECTORY')
    receipt_path=src/'R97_GALLERY_RECEIPT.json'
    if not receipt_path.is_file() or receipt_path.is_symlink():
        raise ValueError('R98_MISSING_RECEIPT')
    receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
    if not (receipt.get('schema')=='fv.apollo.r97.gallery.v1' and
            receipt.get('release')=='STAGING_HOLD' and
            receipt.get('publication_approved') is False and
            all(receipt.get(k)==0 for k in ('photo_rights_cleared','images_embedded','geo_pins','inferred_edges')) and
            receipt.get('records')==6 and len(receipt.get('files',{}))==28):
        raise ValueError('R98_UNAPPROVED_RELEASE')
    expected=set(receipt['files'])|{'R97_GALLERY_RECEIPT.json'}
    if {p.name for p in src.iterdir()} != expected:
        raise ValueError('R98_UNREVIEWED_FILES')
    for name in sorted(expected):
        p=src/name
        if not re.fullmatch(r'[A-Za-z0-9_.-]+', name) or not p.is_file() or p.is_symlink():
            raise ValueError('R98_UNSAFE_FILE:'+name)
        if name in receipt['files'] and sha(p.read_bytes())!=receipt['files'][name]:
            raise ValueError('R98_HASH_MISMATCH:'+name)
    source=json.loads((src/'R93_SOURCE_PASSPORTS.json').read_text(encoding='utf-8'))
    rows=source['records']
    if [r['id'] for r in rows] != [f'{n:02}' for n in range(1,7)]:
        raise ValueError('R98_SOURCE_SET')
    if any(r['rights']!='INDIVIDUAL REVIEW REQUIRED' for r in rows):
        raise ValueError('R98_RIGHTS')
    if rows[0]['provisional'] is not True or rows[0]['date']!='January 1967 — day unconfirmed':
        raise ValueError('R98_CREW_PROVISIONAL')
    if any(r['date']!='January 24, 2017' for r in (rows[3],rows[5])):
        raise ValueError('R98_RETROSPECTIVE_DATE')
    return receipt,rows

def rewrite_view(name,text,rows):
    if text.count('</head>')!=1 or 'r98_crosslinks.css' in text:
        raise ValueError('R98_HEAD_INVARIANT:'+name)
    text=text.replace('</head>','<link rel="stylesheet" href="r98_crosslinks.css"></head>',1)
    count=0
    for row in rows:
        n=row['id']; ident=VIEWS[name]+n
        regex=r'(<article\b[^>]*\bid="'+re.escape(ident)+r'"[^>]*>)(.*?)(</article>)'
        def replace(m):
            nonlocal count
            body=m.group(2)
            # Bind the NAV to the actual NASA URL, title and catalog already in this article,
            # not just a numeric id that could silently swap source identities.
            if any(key not in body for key in (row['url'],row['title'],row['catalog'])):
                raise ValueError('R98_SOURCE_CARD_MISMATCH:'+name+':'+n)
            if name=='R97_SOURCE_GALLERY.html':
                destinations=[('Rights', 'R85_NASA_SOURCE_REVIEW.html#r85-source-'+n),
                              ('Reading Room','R88_READING_ROOM.html#r88-'+n),
                              ('Evidence Hub','R89_REVIEW_HUB.html#r89-source-'+n)]
                explainer='Same NASA source · different evidence views, not a causal link.'
            else:
                destinations=[('Open gallery record '+n,'R97_SOURCE_GALLERY.html#gallery-'+n)]
                explainer='Same NASA record · rights-unreviewed image remains withheld.'
            links=' '.join('<a href="'+html.escape(href,quote=True)+'">'+html.escape(label)+'</a>' for label,href in destinations)
            nav='<nav class="r98-route" aria-label="Alternate views of NASA source '+n+'">'+links+'<span class="r98-explainer">'+explainer+'</span></nav>'
            count+=1
            return m.group(1)+body+nav+m.group(3)
        text,num=re.subn(regex,replace,text,count=1,flags=re.S)
        if num!=1:
            raise ValueError('R98_MISSING_CARD:'+name+':'+n)
    if count!=6:
        raise ValueError('R98_CARD_COUNT:'+name)
    return text

def build(src,out,archive=None):
    receipt,rows=custody(src)
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise ValueError('R98_NONEMPTY_OUTPUT')
    if archive and archive.exists():
        raise ValueError('R98_ARCHIVE_EXISTS')
    # All validation and rendering before writing prevents partial output on input errors.
    data={p.name:p.read_bytes() for p in src.iterdir()}
    for page in VIEWS:
        data[page]=rewrite_view(page,data[page].decode('utf-8'),rows).encode('utf-8')
    data['r98_crosslinks.css']=CSS.encode('utf-8')
    receipt_out={
      'schema':'fv.apollo.r98.roundtrip.v1','release':'STAGING_HOLD',
      'publication_approved':False,'photo_rights_cleared':0,'images_embedded':0,
      'geo_pins':0,'inferred_edges':0,'records':6,'views':7,
      'reciprocal_gallery_links':54,'inherited_receipt_sha256':sha((src/'R97_GALLERY_RECEIPT.json').read_bytes()),
      'files':{name:sha(data[name]) for name in sorted(data)},
      'note':'Inherited R97 receipt covers unmodified R97 input only; R98 receipt covers transformed output.'}
    data['R98_ROUNDTRIP_RECEIPT.json']=(json.dumps(receipt_out,sort_keys=True,indent=2)+'\n').encode('utf-8')
    out.mkdir(parents=True,exist_ok=True)
    for name in sorted(data):
        (out/name).write_bytes(data[name])
    if archive:
        archive.parent.mkdir(parents=True,exist_ok=True)
        with ZipFile(archive,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
            for name in sorted(data):
                info=ZipInfo(name,date_time=(1980,1,1,0,0,0))
                info.compress_type=ZIP_DEFLATED
                info.create_system=3
                info.external_attr=0o100644<<16
                z.writestr(info,data[name])
    return receipt_out

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--src',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--archive',type=Path)
    opts=parser.parse_args()
    print(json.dumps(build(opts.src,opts.out,opts.archive),sort_keys=True))
