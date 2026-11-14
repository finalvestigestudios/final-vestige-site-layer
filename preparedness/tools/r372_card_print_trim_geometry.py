#!/usr/bin/env python3
"""R372 Tool #104 private print trim-geometry witness. REVIEW ONLY, never clearance.

Original article/source stays untouched. Synthetic browser proof rejects warnings outside
trim faces, lost font legibility, card/face size drift, overflows, network attempts,
missing real PDF warning text and unsafe dynamic values. A browser-generated PDF is
not a physical print or independent child-safety review. Output is always hard hold.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

SCHEMA = 'fv-preparedness-r372-print-trim-geometry-v1'
PATH = 'content/tools/family-reunification-card.body.html'
META = 'content/tools/family-reunification-card.meta.json'
PIN_BODY = 'be8698ac5d020476ff649d85813810e2000c6f98'
PIN_META = '47da1e7e20e39f0ea85e26d54a8d58301f6e0a15'
NOTICE = 'A printed card can be lost. Anyone who finds it can read it.'
# Exact original source print CSS: fixed content-box height + padding exceeds
# parent trim rectangle. The fix is a REVIEW-ONLY in-memory CSS addition.
FACE_CSS = '.pa-foldcard .pa-face { border: 0; border-right: 1px dashed #000; padding: .07in .1in; font-size: 7.5pt; line-height: 1.14; overflow: hidden; height: 2.125in; }'
FACE_CSS_FIXED = FACE_CSS[:-2] + ' box-sizing: border-box; }'

EXPECTED_CARD_WIDTH_CSS_PX = 7 * 96
EXPECTED_CARD_HEIGHT_CSS_PX = 2.125 * 96
# The 6.5pt notice is itself tiny; passing this technical floor is NOT accessibility approval.
MIN_NOTICE_PT = 6.5
TRIM_GUTTER_PX = 0.8
RELEASE = {key: False for key in (
    'may_merge','may_publish','qd_pass','child_privacy_approved',
    'independent_safety_approved','paper_trim_verified','mobile_accessibility_verified',
    'native_build_verified','wp_export_verified','merchant_sale_verified',
    'paid_sku_verified','revenue_attributed')}


def blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def _load(root: Path, name: str):
    p = root / 'tools' / (name + '.py')
    if not p.is_file() or p.is_symlink():
        raise ValueError('MISSING_OR_SYMLINKED_REQUIRED_VALIDATOR:' + name)
    spec = importlib.util.spec_from_file_location('r372_dep_' + name, p)
    if spec is None or spec.loader is None:
        raise ValueError('UNLOADABLE_REQUIRED_VALIDATOR:' + name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def classify_faces(rows, *, expected_cards: int) -> list[str]:
    """Pure, testable fail-closed examination of browser-computed print geometry."""
    issues = []
    if not isinstance(rows, list) or len(rows) != expected_cards:
        return ['PRINT_CARD_COUNT_MISMATCH']
    for ci, card in enumerate(rows):
        if not isinstance(card, dict) or len(card.get('faces', [])) != 2:
            issues.append(f'FACE_COUNT:{ci}')
            continue
        width = card.get('width', -1)
        height = card.get('height', -1)
        if not isinstance(width, (float, int)) or abs(width - EXPECTED_CARD_WIDTH_CSS_PX) > 2:
            issues.append(f'CARD_WIDTH_DRIFT:{ci}')
        if not isinstance(height, (float, int)) or abs(height - EXPECTED_CARD_HEIGHT_CSS_PX) > 2:
            issues.append(f'CARD_HEIGHT_DRIFT:{ci}')
        for fi, face in enumerate(card['faces']):
            tag = f'{ci}:{fi}'
            if face.get('notice_count') != 1 or face.get('notice_text') != NOTICE:
                issues.append('NOTICE_MISSING_OR_CHANGED:' + tag)
            if not face.get('visible') or not face.get('inside'):
                issues.append('NOTICE_OUTSIDE_TRIM_OR_HIDDEN:' + tag)
            if not face.get('legible_size'):
                issues.append('NOTICE_FONT_BELOW_FLOOR:' + tag)
            if face.get('clipped') or face.get('overflow'):
                issues.append('FACE_CONTENT_OVERFLOW:' + tag)
            if not face.get('fold_fit'):
                issues.append('FACE_FOLD_OVERLAP:' + tag)
    return sorted(set(issues))


def proposed_trim_fix(prior_candidate: str, original: str) -> str:
    """Deterministic minimal private CSS candidate, never writes actual source.

    Reject rebase ambiguity and any changes beyond the one print declaration.
    Prior must be R371's warning-on-detached-face proposal, not a live page.
    """
    if not isinstance(prior_candidate,str) or not isinstance(original,str):
        raise ValueError('INVALID_SOURCE_TYPE')
    if prior_candidate.count(FACE_CSS) != 1 or original.count(FACE_CSS) != 1:
        raise ValueError('PRINT_CSS_ANCHOR_CHANGED_REBASE_REQUIRED')
    if FACE_CSS_FIXED in prior_candidate:
        raise ValueError('TRIM_FIX_ALREADY_APPLIED')
    if prior_candidate.count('pa-card-caution') != 4:
        raise ValueError('REQUIRED_R371_CARD_NOTICE_MISSING')
    new = prior_candidate.replace(FACE_CSS, FACE_CSS_FIXED, 1)
    if new.replace(FACE_CSS_FIXED, FACE_CSS, 1) != prior_candidate:
        raise ValueError('MORE_THAN_ONE_CSS_CHANGE')
    for pat in (r'{{cite:[^}]+}}',r'{{link:[^}]+}}'):
        if re.findall(pat,new) != re.findall(pat,original):
            raise ValueError('SOURCE_CITATION_DESTINATION_CUSTODY_FAILURE')
    if new.count('<form') != original.count('<form'):
        raise ValueError('FORM_CUSTODY_FAILURE')
    if len(new) - len(prior_candidate) != len(' box-sizing: border-box;'):
        raise ValueError('UNEXPECTED_PATCH_SIZE')
    return new


def inspect(document: str, *, js: bool = False, copies: int = 1,
            dense: bool = False, chromium: str = '/usr/bin/chromium') -> dict:
    """Offline synthetic print CSS and PDF proof. NO real contact information entered."""
    out = {'errors': [], 'js': js, 'copies': copies, 'dense': dense,
           'cards': 0, 'faces': 0, 'pdf_pages': 0,
           'pdf_notice_count': 0, 'network_attempts': 0}
    if not isinstance(document, str) or len(document) > 250_000 or not document:
        out['errors'] = ['BAD_HTML_INPUT']; return out
    if type(copies) is not int or copies < 1 or copies > 4 or not isinstance(js, bool):
        out['errors'] = ['BAD_BOUNDED_BROWSER_INPUT']; return out
    if not Path(chromium).is_file():
        out['errors'] = ['CHROMIUM_MISSING']; return out
    if '{{inline-js:' in document and js:
        # Only the source's deterministic isolated test-model is substituted;
        # this is not evidence of real source JS behavior.
        stub = """function rcModel(f,minimal){let x=v=>v||'SYNTHETIC TEST ONLY';
        let a=[{k:'Household',v:x(f.hhName)},{k:'Out of area',v:x(f.outName)},
        {k:'Phone',v:x(f.outPhone)},{k:'Meet first',v:x(f.meet1)},
        {k:'If not',v:x(f.meet2)}];let b=minimal?[{k:'Reviewed',v:x(f.reviewed)}]:
        [{k:'School',v:x(f.school)},{k:'Plan',v:x(f.schoolPlan)},
        {k:'Pickup',v:x(f.pickup)},{k:'Care',v:x(f.careName)},
        {k:'Phone',v:x(f.carePhone)},{k:'Access',v:x(f.access)},
        {k:'Reviewed',v:x(f.reviewed)}];return {front:a,back:b}}
        function rcWarnings(){return [];}"""
        document = document.replace('{{inline-js:shelter_common.js}}', stub).replace('{{inline-js:reunion_card.js}}', '')
    try:
        import fitz
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, executable_path=chromium,
                 args=['--no-sandbox', '--disable-gpu', '--disable-background-networking'])
            try:
                ctx = browser.new_context(offline=True, java_script_enabled=js,
                     service_workers='block', viewport={'width':1200,'height':900})
                ctx.route('**/*', lambda route: route.abort())
                try:
                    page = ctx.new_page()
                    attempted = []
                    page.on('request', lambda req: attempted.append(req.url))
                    page.set_content(document, wait_until='domcontentloaded', timeout=15000)
                    if js:
                        page.locator('#rc-copies').select_option(str(copies))
                        if dense:
                            for key in ('hhName','outName','outPhone','meet1','meet2',
                                        'school','schoolPlan','pickup','careName','carePhone','access'):
                                page.locator('#rc-' + key).fill('SYNTHETIC LONG CONTACT TEST ' + key)
                    page.emulate_media(media='print')
                    rows = page.evaluate('''() => {
                      const visible = el => {for(let n=el;n&&n.nodeType===1;n=n.parentElement){
                        const s=getComputedStyle(n);if(s.display==='none'||s.visibility==='hidden'||n.hidden)return false;
                      }return true};
                      return [...document.querySelectorAll('.pa-foldcard')].filter(visible).map(card=>{
                        const cr=card.getBoundingClientRect();
                        return {width:cr.width,height:cr.height,faces:[...card.querySelectorAll('.pa-face')].map(face=>{
                          const fr=face.getBoundingClientRect(), cs=face.querySelectorAll('.pa-card-caution');
                          const w=cs[0],wr=w?.getBoundingClientRect(),font=w?parseFloat(getComputedStyle(w).fontSize):0;
                          const paras=[...face.querySelectorAll('p')];
                          return {notice_count:cs.length,notice_text:w?.textContent?.trim()||'',
                           visible:!!(w&&visible(w)&&wr&&wr.height>0),
                           inside:!!(wr&&wr.left>=fr.left+0.8&&wr.right<=fr.right-0.8&&wr.top>=fr.top+0.8&&wr.bottom<=fr.bottom-0.8),
                           legible_size:font>=8.6666,
                           clipped:paras.some(e=>{const r=e.getBoundingClientRect();return r.top<fr.top-1||r.bottom>fr.bottom+1||r.left<fr.left-1||r.right>fr.right+1;}),
                           overflow:face.scrollHeight>face.clientHeight+1||face.scrollWidth>face.clientWidth+1,
                           fold_fit:fr.left>=cr.left-1&&fr.right<=cr.right+1&&fr.top>=cr.top-1&&fr.bottom<=cr.bottom+1};
                        })};
                      });
                    }''')
                    out['cards'] = len(rows)
                    out['faces'] = sum(len(r.get('faces',[])) for r in rows)
                    out['errors'].extend(classify_faces(rows, expected_cards=(copies if js else 1)))
                    pdf = page.pdf(format='Letter', print_background=True,
                                   prefer_css_page_size=False, scale=1)
                    doc = fitz.open(stream=pdf, filetype='pdf')
                    try:
                        out['pdf_pages'] = len(doc)
                        # A digital PDF is a proof-of-render, not paper. The actual
                        # warning may wrap lines: normalize whitespace when counting.
                        body = ' '.join(' '.join(pg.get_text().split()) for pg in doc)
                        out['pdf_notice_count'] = body.count(NOTICE)
                    finally: doc.close()
                    out['network_attempts'] = len(attempted)
                    if attempted: out['errors'].append('NETWORK_ATTEMPTED')
                    # One page-level notice plus one inside each of 2*cards faces.
                    # Chromium pagination may repeat the header. Under-count
                    # always fails; over-count requires human duplicate review.
                    if out['pdf_notice_count'] < 2 * out['cards']:
                        out['errors'].append('PDF_LOST_FACE_WARNINGS')
                finally: ctx.close()
            finally: browser.close()
    except Exception as exc:
        out['errors'].append('BROWSER_OR_PDF_PROBE_FAILED:' + type(exc).__name__)
    out['errors'] = sorted(set(out['errors']))
    return out


def review(root: Path, *, browser: bool = False, chromium: str = '/usr/bin/chromium') -> dict:
    out = {'schema':SCHEMA,'status':'INVALID_HARD_HOLD','errors':[],
           'evidence':{}, **RELEASE}
    try:
        root = Path(root)
        if not root.is_dir() or root.is_symlink():
            raise ValueError('AUTHENTIC_CHECKOUT_MISSING')
        p, m = root / PATH, root / META
        if not p.is_file() or not m.is_file() or p.is_symlink() or m.is_symlink():
            raise ValueError('SOURCE_OR_METADATA_MISSING')
        b, mb = p.read_bytes(), m.read_bytes()
        if blob(b) != PIN_BODY or blob(mb) != PIN_META:
            raise ValueError('AUTHENTIC_SOURCE_PIN_DRIFT_REBASE_REQUIRED')
        meta = json.loads(mb)
        if (meta.get('n') != 104 or meta.get('slug') != 'family-reunification-card'
            or meta.get('status') != {'editorial':'drafted','publish':'draft'}
            or meta.get('safety_review',{}).get('state') != 'pending'):
            raise ValueError('SAFETY_DRAFT_STATE_DRIFT')
        r370 = _load(root,'r370_card_privacy_print_review_candidate')
        r371 = _load(root,'r371_detached_card_print_custody')
        source = b.decode('utf-8')
        prior = r371.build_candidate(source,r370)
        candidate = proposed_trim_fix(prior,source)
        if re.findall(r'{{cite:[^}]+}}',candidate) != re.findall(r'{{cite:[^}]+}}',source):
            raise ValueError('CITATION_ORDER_LOST')
        if re.findall(r'{{link:[^}]+}}',candidate) != re.findall(r'{{link:[^}]+}}',source):
            raise ValueError('DESTINATION_ORDER_LOST')
        r371.static_card_inventory(candidate)
        out['evidence']['source_git_blob'] = blob(b)
        out['evidence']['meta_git_blob'] = blob(mb)
        out['evidence']['candidate_sha256'] = hashlib.sha256(candidate.encode()).hexdigest()
        out['evidence']['candidate_only'] = True
        out['evidence']['original_print_face_box_sizing'] = 'content-box (implicit)'
        out['evidence']['review_css_box_sizing'] = 'border-box'
        out['evidence']['print_geometry_candidate_diff_only'] = True
        if browser:
            checks = {}
            for js in (False,True):
                for cp in ((1,) if not js else (1,4)):
                    for dense in (False,True):
                        key = f'js{int(js)}_copies{cp}_dense{int(dense)}'
                        checks[key] = inspect(candidate,js=js,copies=cp,dense=dense,chromium=chromium)
                        if checks[key]['errors']:
                            out['errors'].append('RENDER_PROBE_REVIEW:' + key + ':' + ','.join(checks[key]['errors']))
            out['evidence']['synthetic_probes'] = checks
        else:
            out['errors'].append('BROWSER_PDF_PROOFS_NOT_EXECUTED')
        if blob(p.read_bytes()) != PIN_BODY:
            raise ValueError('SOURCE_WRITTEN_UNEXPECTEDLY')
        out['status'] = 'REVIEW_REQUIRED_HARD_HOLD' if not out['errors'] else 'INVALID_HARD_HOLD'
    except (OSError, ValueError, TypeError, KeyError, UnicodeError, json.JSONDecodeError) as exc:
        out['errors'].append(type(exc).__name__ + ':' + str(exc))
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--browser', action='store_true')
    parser.add_argument('--chromium', default='/usr/bin/chromium')
    args = parser.parse_args(argv)
    print(json.dumps(review(args.root,browser=args.browser,chromium=args.chromium), indent=2,sort_keys=True))
    return 2

if __name__ == '__main__':sys.exit(main())
