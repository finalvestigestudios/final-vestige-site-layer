#!/usr/bin/env python3
"""R368: read-only, fail-closed private-print disclosure gate for Tool #104.

Screenshots, browser state, publication, health or data-safety approval are NOT
produced. An isolated Chromium print-media visibility probe is *not* a physical
print test. This verifier intentionally returns a HARD HOLD on every outcome.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

SCHEMA = 'fv-preparedness-r368-print-disclosure-custody-v1'
BODY_PATH = 'content/tools/family-reunification-card.body.html'
META_PATH = 'content/tools/family-reunification-card.meta.json'
SLUG = 'family-reunification-card'
ALERT = 'A printed card can be lost'
PRIVACY = 'Anyone who finds it can read it.'
PIN_BODY = 'be8698ac5d020476ff649d85813810e2000c6f98'
PIN_META = '47da1e7e20e39f0ea85e26d54a8d58301f6e0a15'
HOLD = dict(may_publish=False, may_merge=False, qd_pass=False,
            physical_print_verified=False, child_privacy_verified=False,
            medical_safety_verified=False, independent_safety_approved=False,
            paid_sku_verified=False, verified_paid_orders=False, revenue_verified=False)


def git_blob(content: bytes) -> str:
    return hashlib.sha1(f'blob {len(content)}\0'.encode('ascii')+content).hexdigest()


def report(errors=(), evidence=None, review=()):
    return dict(schema=SCHEMA, status='INVALID_HARD_HOLD' if errors else 'REVIEW_REQUIRED_HARD_HOLD',
                errors=sorted(set(errors)), human_review=sorted(set(review)),
                evidence=evidence or {}, **HOLD)


def read_original(root: Path):
    """Pinned exact Git source identity, no network or mutation."""
    errors=[]; evidence={}
    if root.is_symlink() or not root.is_dir():
        return ['MISSING_AUTHENTIC_PREPAREDNESS_ROOT'],evidence,None
    paths=[root/BODY_PATH,root/META_PATH]
    if any(p.is_symlink() or not p.is_file() for p in paths):
        return ['MISSING_OR_SYMLINKED_SOURCE'],evidence,None
    try:
        raw=paths[0].read_bytes(); meta_raw=paths[1].read_bytes()
        source=raw.decode('utf-8'); meta=json.loads(meta_raw.decode('utf-8'))
        evidence.update(source_blob=git_blob(raw),metadata_blob=git_blob(meta_raw),
                        original_warning_occurrences=source.count(ALERT),
                        privacy_sentence_occurrences=source.count(PRIVACY))
        if evidence['source_blob']!=PIN_BODY or evidence['metadata_blob']!=PIN_META:
            errors.append('PINNED_ORIGINAL_SOURCE_IDENTITY_CHANGED')
        if meta.get('slug')!=SLUG or meta.get('n')!=104:
            errors.append('TOOL104_IDENTITY_DRIFT')
        if meta.get('status',{}).get('publish')!='draft':
            errors.append('TOOL104_MUST_REMAIN_DRAFT')
        if meta.get('safety_review',{}).get('state')!='pending':
            errors.append('TOOL104_SAFETY_REVIEW_STATE_DRIFT')
        if source.count(ALERT)!=1 or source.count(PRIVACY)!=1:
            errors.append('ORIGINAL_PRIVACY_DISCLOSURE_ANCHOR_DRIFT')
        return errors,evidence,source
    except (OSError,UnicodeError,ValueError,TypeError,AttributeError) as exc:
        return ['UNREADABLE_OR_MALFORMED_ORIGINAL:'+type(exc).__name__],evidence,None


def _display_state(page):
    """Computed CSS and layout in an offline, JS-disabled Chromium document.

    Print visibility cannot be inferred from raw HTML or a screen-only snapshot.
    Browser-only assertions remain limited to rendered visibility, not paper.
    """
    return page.evaluate('''() => {
      const arr = [...document.querySelectorAll('p.pa-alert-title')]
          .filter(x => x.textContent.trim() === 'A printed card can be lost');
      const targets = arr.map(el => {
        const parent = el.closest('.pa-alert') || el;
        const s = getComputedStyle(parent), t = getComputedStyle(el);
        const r = el.getBoundingClientRect();
        const hiddenAncestor = (() => {
          let n=el; while(n && n.nodeType === 1) {
            const z=getComputedStyle(n);
            if(z.display === 'none' || z.visibility === 'hidden' ||
               z.visibility === 'collapse' || z.contentVisibility === 'hidden' ||
               Number(z.opacity) === 0 || n.hidden || n.hasAttribute('inert')) return true;
            n=n.parentElement;
          } return false;
        })();
        return {visible:!hiddenAncestor && r.width>0 && r.height>0,
          parentDisplay:s.display, ownDisplay:t.display,
          box:[Math.round(r.width),Math.round(r.height)]};
      });
      const alert=arr.length===1 ? arr[0].closest('.pa-alert') : null;
      const text=alert ? alert.textContent.replace(/\\s+/g,' ').trim() : '';
      const ns=[...document.querySelectorAll('noscript')];
      const noJsRendered=ns.some(n=>{const r=n.getBoundingClientRect();return r.width>0&&r.height>0;});
      return {matches:arr.length,targets,privacyStatement:text.includes('Anyone who finds it can read it.'),
              noJsRendered,hadScripts:document.querySelectorAll('script').length>0};
    }''')


def browser_probe(source: str, wp: str, preview: str, *, executable='/usr/bin/chromium'):
    """No outbound network requests; no clicks, forms, script execution or writes."""
    errors=[]; states={}
    if not isinstance(source,str) or not isinstance(wp,str) or not isinstance(preview,str):
        return ['BAD_BROWSER_INPUT'],states
    if any(len(s)>2_000_000 for s in (source,wp,preview)):
        return ['BROWSER_INPUT_TOO_LARGE'],states
    if not Path(executable).is_file():
        return ['CHROMIUM_UNAVAILABLE'],states
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=executable,headless=True,
                args=['--no-sandbox','--disable-gpu','--disable-background-networking'])
            try:
                context=browser.new_context(java_script_enabled=False,service_workers='block',offline=True)
                context.route('**/*',lambda route:route.abort())
                try:
                    for name,doc in [('original',source),('wordpress',wp),('preview',preview)]:
                        page=context.new_page()
                        try:
                            page.set_content(doc,wait_until='domcontentloaded',timeout=12000)
                            per_media={}
                            for media in ('screen','print'):
                                page.emulate_media(media=media)
                                per_media[media]=_display_state(page)
                            states[name]=per_media
                            for media,s in per_media.items():
                                if s['matches']!=1 or not s['privacyStatement']:
                                    errors.append('DISCLOSURE_MISSING_OR_MULTIPLE:'+name+':'+media)
                                elif not s['targets'][0]['visible']:
                                    errors.append('DISCLOSURE_HIDDEN:'+name+':'+media)
                            if not per_media['screen']['noJsRendered']:
                                errors.append('NOJS_FALLBACK_NOT_RENDERED:'+name)
                        finally:page.close()
                finally:context.close()
            finally:browser.close()
    except Exception as exc:
        errors.append('CHROMIUM_PROBE_FAILURE:'+type(exc).__name__)
    return sorted(set(errors)),states


def audit(root: Path, build: Path | None=None, *, executable='/usr/bin/chromium'):
    """Full audit requires R367's complete 50-pair read-only source/output gate."""
    root=Path(root);build=Path(build) if build is not None else root/'build'
    errs,ev,source=read_original(root)
    if source is None:return report(errs,ev)
    gatefile=root/'tools'/'r367_wp_preview_source_custody.py'
    if gatefile.is_symlink() or not gatefile.is_file():
        return report(errs+['R367_DEPENDENCY_MISSING'],ev)
    try:
        spec=importlib.util.spec_from_file_location('_r367_readonly',gatefile)
        if not spec or not spec.loader:raise ValueError('bad module')
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        earlier=mod.audit(root,build)
        ev['r367_status']=earlier['status']
        ev['r367_errors']=earlier['errors']
        ev['r367_paired_exports']=earlier['evidence'].get('paired_exports_inspected')
        if earlier['status']!='REVIEW_REQUIRED_HARD_HOLD' or ev['r367_paired_exports']!=50:
            errs.append('INHERITED_R367_NATIVE_OUTPUT_HARD_HOLD')
        files=[build/'wp'/f'{SLUG}.html',build/'preview'/f'{SLUG}.html']
        if any(p.is_symlink() or not p.is_file() for p in files):
            return report(errs+['TOOL104_PRIVATE_OUTPUT_PAIR_MISSING'],ev)
        wp,preview=[p.read_text('utf8') for p in files]
        visibility_errors,states=browser_probe(source,wp,preview,executable=executable)
        errs+=visibility_errors
        ev['offline_chromium_media_observations']=states
    except Exception as exc:
        errs.append('INTEGRATION_PROBE_FAILURE:'+type(exc).__name__)
    return report(errs,ev,review=['Qualified print/child-data/emergency-source review required',
                                  'Verify mobile keyboard, print/PDF and physical paper separately'])


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--build',type=Path)
    parser.add_argument('--chromium',default='/usr/bin/chromium')
    a=parser.parse_args(argv)
    result=audit(a.root,a.build,executable=a.chromium)
    print(json.dumps(result,sort_keys=True,indent=2))
    return 2  # ALWAYS HARD HOLD, never approval or publication


if __name__=='__main__':sys.exit(main())
