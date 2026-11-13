#!/usr/bin/env python3
"""R340: read-only exact output reproducibility on a source-pinned private build.

Independently regenerates all 100 draft bytes in memory using the authenticated
builder/source tree; refuses a pair that was edited identically in both exports.
Synthetic parity is not native validation, source support, QD, or release.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
from preparedness.tools import r339_export_draft_safety_gate as previous

SCHEMA = 'fv-preparedness-r340-source-to-render-reproducibility-v1'
BUILDER_BLOB = '349173d1e1d735eade218d95c7a0a2649c8cccd9'
CSS_BLOB = 'e354395cdb7985eb2fe16b99ca9fd66c9885557e'
EDITORIAL_HUB_BLOB = 'e1e749169a58e35a32c1d48ee8c46c209630965b'
VALID_SLUG = re.compile(r'\A[a-z0-9]+(?:-[a-z0-9]+)*\Z')


def receipt(errors: list[str], inspected: int = 0, manifest: list[dict] | None = None) -> dict:
    return {
        'schema': SCHEMA,
        'state': 'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
        'errors': sorted(set(errors)),
        'matched_private_export_files': inspected,
        'expected_private_export_files': 100,
        'sha256_manifest': manifest or [],
        'source_to_render_reproducibility_tested': not bool(errors),
        'authentic_source_checkout_verified': False,
        'source_claim_support_verified': False,
        'qualified_qd_pass': False,
        'emergency_or_medical_advice_approved': False,
        'wordpress_live_or_published': False,
        'paid_preparedness_sku_verified': False,
        'realized_net_revenue_verified': False,
        'may_merge': False,
        'may_publish': False,
        'may_activate_commerce': False,
    }


def exact_compare(expected: dict[str, bytes], actual: dict[str, bytes]) -> dict:
    """Pure byte-level comparison; exact 100-file output contract, always draft."""
    if type(expected) is not dict or type(actual) is not dict:
        return receipt(['UNTRUSTED_OR_MISSING_EXPORT_MAPPING'])
    if len(expected) != 100 or set(expected) != set(actual):
        missing = set(expected) - set(actual)
        extra = set(actual) - set(expected)
        return receipt(['EXACT_100_FILE_SET_REQUIRED'] +
                       ['MISSING_EXPORT:' + x for x in sorted(missing)] +
                       ['EXTRA_EXPORT:' + x for x in sorted(extra)])
    errors = []; manifest = []; matched = 0
    for path in sorted(expected):
        if (type(path) is not str or not re.fullmatch(r'(wp|preview)/[a-z0-9-]+\.html', path)
                or type(expected[path]) is not bytes or type(actual[path]) is not bytes):
            errors.append('INVALID_EXPORT_ID_OR_BYTES:' + str(path)); continue
        e, a = expected[path], actual[path]
        if e != a:
            errors.append('SOURCE_TO_RENDER_BYTES_DRIFT:' + path)
            continue
        matched += 1
        manifest.append({'path': path, 'sha256': hashlib.sha256(a).hexdigest(), 'bytes':len(a)})
    return receipt(errors, matched, manifest)


def compose_expected(lib) -> tuple[dict[str, bytes], dict]:
    """Run the existing trusted builder's pure functions; never call main/write_lf."""
    from preparedness.tools import build
    pages = {}; article_rows = []; hubs = []

    def add(slug: str, inner: str, title: str, description: str):
        if not VALID_SLUG.fullmatch(slug) or slug in pages:
            raise ValueError('Duplicate or invalid source page: ' + str(slug))
        pages[slug] = (inner, title, description)

    for slug in lib.articles:
        row = build.build_article(lib, slug)
        meta = row['meta']
        if row['slug'] != slug or meta['slug'] != slug or meta['status']['publish'] != 'draft':
            raise ValueError('Article source identity or draft state drift: ' + slug)
        add(slug, row['inner'], f'{meta["h1"]} | The Preparedness Archive', meta['description'])
        article_rows.append({k:row[k] for k in ('slug','words','minutes','sources','canonical')})
    for section in lib.taxonomy['sections']:
        hub = build.build_hub(lib, section['slug'], include_drafts=True)
        if hub is None:
            raise ValueError('Missing required populated section: ' + section['slug'])
        add(hub['slug'], hub['inner'], hub['title'], hub['description'])
        hubs.append({'section':section['slug'],'guides':hub['count']})
    landing = build.build_landing(lib, include_drafts=True)
    add('landing', landing['inner'], 'The Preparedness Archive | Final Vestige',
        'Evidence-based household preparedness and a historical record of how earlier generations managed without modern infrastructure.')
    if len(article_rows) != 41 or len(hubs) != 8 or len(pages) != 50 or landing['article_cards'] != 41:
        raise ValueError('Not the authentic 41 entry, eight hub, 50 page source inventory')
    outputs = {}
    for slug,(inner,title,desc) in pages.items():
        outputs['wp/'+slug+'.html'] = build.wp_wrap(lib, inner).encode('utf-8')
        outputs['preview/'+slug+'.html'] = build.preview_wrap(lib, inner, title, desc).encode('utf-8')
    return outputs, {'articles':article_rows,'hubs':hubs,
                     'landing':{k:landing[k] for k in ('populated_sections','article_cards')}}


def report_compare(expected_report: dict, actual_report: dict) -> list[str]:
    if type(expected_report) is not dict or type(actual_report) is not dict:
        return ['MISSING_OR_INVALID_BUILD_REPORT']
    errors=[]
    for key in ('articles','hubs','landing'):
        if actual_report.get(key) != expected_report.get(key):
            errors.append('BUILDER_SOURCE_REPORT_DRIFT:'+key)
    release = actual_report.get('release_evidence')
    if (type(release) is not dict or release.get('article_drafts') != 41
            or release.get('article_published') != 0
            or release.get('independent_qa_verified') is not False
            or release.get('wordpress_publication_performed') is not False
            or release.get('state') != 'HOLD'):
        errors.append('BUILD_REPORT_FALSE_PUBLISH_OR_QD_STATE')
    return errors


def audit_native(root: Path) -> dict:
    """Fail closed unless previous native gates and trusted builder Git blobs pass."""
    root = root.resolve()
    try:
        if previous.audit_native(root)['state'] != 'DRAFT_HARD_HOLD':
            return receipt(['R339_AUTHENTIC_NATIVE_RENDERED_SAFETY_PRECONDITION_REQUIRED'])
        from preparedness.tools import r336_frozen_archive_integrity as custody
        for relative, pin in ((Path('preparedness/tools/build.py'),BUILDER_BLOB),
                              (Path('preparedness/assets/preparedness.css'),CSS_BLOB),
                              (Path('preparedness/content/hubs/start-here.body.html'),EDITORIAL_HUB_BLOB)):
            path = root/relative
            if path.is_symlink() or not path.is_file() or custody.git_blob(path.read_bytes()) != pin:
                return receipt(['RENDERER_OR_CSS_GIT_BLOB_CHANGED:'+str(relative)])
        from preparedness.tools import build
        if Path(build.__file__).resolve() != (root/'preparedness/tools/build.py').resolve():
            return receipt(['IMPORTED_BUILDER_NOT_AUTHENTIC_CHECKOUT'])
        lib = build.Library(root/'preparedness')
        expected, expected_report = compose_expected(lib)
        actual={}
        for folder in ('wp','preview'):
            directory=root/'preparedness/build'/folder
            if directory.is_symlink() or not directory.is_dir():
                return receipt(['UNTRUSTED_EXPORT_DIRECTORY:'+folder])
            for p in directory.iterdir():
                if p.is_symlink() or not p.is_file():
                    return receipt(['UNTRUSTED_EXPORT_ENTRY:'+p.name])
                actual[folder+'/'+p.name] = p.read_bytes()
        checked = exact_compare(expected,actual)
        report = json.loads((root/'preparedness/build/build-report.json').read_text('utf-8'))
        errors = checked['errors']+report_compare(expected_report,report)
        out=receipt(errors,checked['matched_private_export_files'],checked['sha256_manifest'])
        # This flag means only that preconditions and all exact render checks held;
        # unlike release/QD fields, source authorization is not inferred.
        out['authentic_source_checkout_verified'] = not bool(errors)
        return out
    except (OSError,ValueError,KeyError,TypeError,ImportError,UnicodeError,AttributeError):
        return receipt(['AUTHENTIC_NATIVE_SOURCE_BUILDER_AND_EXPORT_CHECKOUT_REQUIRED'])


def main()->int:
    ap=argparse.ArgumentParser(description='Private source-to-render parity, DRAFT/HARD HOLD only')
    ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2])
    r=audit_native(ap.parse_args().repo_root)
    print(json.dumps(r,sort_keys=True,indent=2))
    return 2 if r['state']=='DRAFT_HARD_HOLD' else 1

if __name__=='__main__': raise SystemExit(main())
