#!/usr/bin/env python3
"""Offline NASA catalog witness for the Apollo 1 evidence-casefile.

The six exact NASA source pages were manually checked on 2026-10-30.
This is a *catalog metadata* gate, not a network freshness test, a legal
rights determination, a validation of Board interpretation, or a certification
of image download/redistribution. It deliberately keeps all photos link-only.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
CASEFILE = HERE.parent.parent.parent / 'apollo-casefile'
GENERATED = HERE.parent.parent / 'generated'
NASA_MEDIA_RULES = 'https://www.nasa.gov/nasa-brand-center/images-and-media/'

# NASA image-detail pages reviewed 2026-10-30 (live references; no media copied).
# The precise date/credit/descriptions must survive subsequent transformations.
WITNESSES = (
    ('01', 'https://www.nasa.gov/image-detail/apollo-1-crew-honored/',
     'Apollo 1 crew training portrait', 'Jan 1967', 'NASA', 'contemporary',
     ('crew', 'Launch Complex 34'), 'link_only_persons_visible', 4),
    ('02', 'https://www.nasa.gov/image-detail/amf-s67-15717/',
     'NASA S67-15717', '3 Jan 1967', 'NASA / JSC', 'contemporary',
     ('Command/Service Module 012', 'mating'), 'link_only_image_transport_unreviewed', 5),
    ('03', 'https://www.nasa.gov/image-detail/amf-s66-58038/',
     'NASA S66-58038', '18 Oct 1966', 'NASA / JSC', 'pre_fire_training',
     ('altitude chamber', 'training'), 'link_only_persons_visible', 4),
    ('04', 'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/',
     'NASA KSC-20170124-PH_KLS01_0164', '24 Jan 2017', 'NASA / Kim Shiflett',
     'retrospective_2017', ('tribute', '2017'), 'link_only_image_transport_unreviewed', 4),
    ('05', 'https://www.nasa.gov/image-detail/amf-s67-21294/',
     'NASA S67-21294', '28 Jan 1967', 'NASA / JSC', 'post_fire_damage',
     ('after the Apollo 1 fire', 'heat damage'), 'link_only_image_transport_unreviewed', 5),
    ('06', 'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/',
     'NASA KSC-20170124-PH_KLS01_0090', '24 Jan 2017', 'NASA / Kim Shiflett',
     'retrospective_2017', ('redesigned', 'tribute'), 'link_only_image_transport_unreviewed', 4),
)

class EditorialHold(ValueError):
    pass

def require(condition, why):
    if not condition:
        raise EditorialHold(why)

def audit(data: dict, export: dict, fragment: str = '') -> dict:
    """Verify NASA image context, chronology and six exported source records.

    Keep this independent of the 12 pinned PR215 source blobs. Call it before
    packaging; the source cannot silently claim photo-rights approval or
    substitute a later museum display for a contemporary evidence photograph.
    """
    rows = data.get('records', [])
    exported = export.get('records', [])
    require(len(rows) == len(WITNESSES) == len(exported), 'NASA six-record count changed')
    require([x.get('id') for x in rows] == [x[0] for x in WITNESSES], 'NASA source order/ID drift')
    require([x.get('claim_id') for x in exported] == [x[0] for x in WITNESSES], 'Export claim ID drift')
    require(data.get('rights_policy') == NASA_MEDIA_RULES, 'NASA rights-policy reference changed')
    require(export.get('not_a_rights_clearance') is True and
            export.get('no_reproduced_images') is True,
            'Export no-rights-clearance/no-reproduction flags changed')
    require(data.get('verified_at') == '2026-10-30', 'Historical NASA source witness date changed')
    for witness, row, rendered in zip(WITNESSES, rows, exported):
        (rid, url, catalog, date, credit, era, description_terms, rights, link_uses) = witness
        fields = {'image_url':url, 'source_id':catalog,
                  'source_date':date,'image_credit':credit,'rights':rights}
        for field, exact in fields.items():
            require(row.get(field) == exact, f'NASA record {rid}: {field} differs from checked NASA catalog witness')
        u=urlsplit(row['image_url'])
        require((u.scheme,u.hostname,u.username,u.password,u.query,u.fragment) ==
                ('https','www.nasa.gov',None,None,'',''),
                f'NASA record {rid}: image link lost source origin or added parameters')
        for term in description_terms:
            require(term.lower() in row.get('image_description','').lower(),
                    f'NASA record {rid}: catalog image-description context omitted: {term}')
        require(row.get('limit') and row.get('finding') and row.get('image_description'),
                f'NASA record {rid}: limitation/source distinction removed')
        require('photo' in (row['finding']+' '+row['limit']).lower() or
                'image' in (row['finding']+' '+row['limit']).lower(),
                f'NASA record {rid}: distinction between photographs and Board evidence omitted')
        if era == 'retrospective_2017':
            context = (row['finding']+' '+row['image_description']+' '+row['limit']).lower()
            require('2017' in context and ('museum' in context or 'tribute' in context or 'exhibit' in context),
                    f'NASA record {rid}: a 2017 exhibit must never appear as 1967 accident footage')
        if era == 'pre_fire_training':
            require('1966' in row['limit'] and '1967' in row['limit'],
                    f'NASA record {rid}: 1966 training source needs explicit 1967 fire distinction')
        correspondence = {
            'image_record_url':url, 'image_catalog_id':catalog,
            'image_date':date, 'image_credit':credit,
            'image_description':row['image_description'],
            'image_evidence_limit':row['limit'], 'media_status':rights,
            'rights_policy_url':NASA_MEDIA_RULES,
        }
        for field, exact in correspondence.items():
            require(rendered.get(field) == exact, f'NASA record {rid}: exported {field} diverges')
        require(rendered.get('geometry') == 'not_assigned', f'NASA record {rid}: invented coordinates')
        if fragment:
            # The PR215 page intentionally repeats each catalog link in stage,
            # Research Desk, comparison, gallery and source views. Losing even
            # one surface is a provenance regression despite other copies.
            require(fragment.count(url) >= link_uses,
                    f'NASA record {rid}: one or more NASA citation surfaces missing')
            require(f'id="source-{rid}"' in fragment,
                    f'NASA record {rid}: accessible source drawer missing')
    if fragment:
        require('<img' not in fragment.lower() and '<picture' not in fragment.lower(),
                'NASA-linked images remain URL-only; embedded media prohibited')
    digest = hashlib.sha256(json.dumps(WITNESSES, separators=(',',':'), ensure_ascii=False).encode()).hexdigest()
    return {'status':'PASS_CATALOG_METADATA_ONLY',
            'nasa_image_pages_checked':6,
            'witness_date':'2026-10-30',
            'witness_sha256':digest,
            'images_reproduced':0,
            'geographic_pins_added':0,
            'source_rights': 'HOLD_PER_ITEM_REVIEW',
            'limitations':'No live fetch in this offline gate; no image reproduction rights or historical analysis certified'}

def audit_files(casefile: Path = CASEFILE, generated: Path = GENERATED) -> dict:
    data=json.loads((casefile/'records.json').read_text(encoding='utf-8'))
    exported=json.loads((generated/'evidence-export.json').read_text(encoding='utf-8'))
    fragment=(generated/'fragment.html').read_text(encoding='utf-8')
    return audit(data,exported,fragment)

if __name__ == '__main__':
    print(json.dumps(audit_files(), indent=2, sort_keys=True))
