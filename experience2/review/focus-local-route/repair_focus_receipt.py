#!/usr/bin/env python3
"""Repair the *offline* protected Playground receipt after the 5-link Focus isolation.

Only the review-only receipt MU-plugin is modified. Never call a WordPress API,
install a plugin or publish a page. Requires protected parent ZIP from PR #1620.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile

PARENT_SHA256 = 'e3a7f7ef73e7db6f7705b01fd3a0aa52452626dd1a1291f66c11248e7712e9dc'
OLD_RECEIPT_SHA256 = 'b8f2f9585f7ca68101965711b19f5ad0980e895a029b5d81675913193742985f'
RECEIPT = 'mu-plugins/fv-ex2-private-browser-receipt.php'
OLD = '''        const focus = [...root.querySelectorAll('a')].filter(a => {
          try { const u = new URL(a.href, document.baseURI); return u.hostname === 'finalvestige.com' && u.pathname === '/focus/'; }
          catch (_) { return false; }
        });'''
NEW = '''        // PR #1620 moved the FIVE preview-only links to an inert LOCAL route.
        // Do not count production Focus URLs as successful isolated destinations.
        const candidateLinks = [...root.querySelectorAll('a[href]')];
        const reviewOrigin = new URL(document.baseURI).origin;
        const markedFocus = candidateLinks.filter(a => a.getAttribute('data-fv-ex2-isolated-focus') === '1');
        const focus = markedFocus.filter(a => {
          try { const u = new URL(a.href, document.baseURI);
            return u.origin === reviewOrigin && u.pathname === '/fv-ex2-focus-review/' && !u.search && !u.hash;
          } catch (_) { return false; }
        });
        const liveFocusLeaks = candidateLinks.filter(a => {
          try { const u = new URL(a.href, document.baseURI);
            return u.hostname === 'finalvestige.com' && u.pathname === '/focus/';
          } catch (_) { return false; }
        }).length;
        const unmarkedLocalFocus = candidateLinks.filter(a => {
          try { const u = new URL(a.href, document.baseURI);
            return u.origin === reviewOrigin && u.pathname === '/fv-ex2-focus-review/' &&
              a.getAttribute('data-fv-ex2-isolated-focus') !== '1';
          } catch (_) { return false; }
        }).length;'''
OLD_BLOCK = "        if (focus.length !== 5) blockers.push('FOCUS_LINKS_NOT_5');"
NEW_BLOCK = """        if (markedFocus.length !== 5 || focus.length !== 5) blockers.push('FOCUS_LOCAL_LINKS_NOT_5_OR_INVALID');
        if (liveFocusLeaks) blockers.push('FOCUS_PRODUCTION_LEAK');
        if (unmarkedLocalFocus) blockers.push('FOCUS_LOCAL_UNMARKED_LINK');"""
OLD_DATA = 'focus_destinations:focus.length,'
NEW_DATA = ('focus_destinations:focus.length,focus_marked_links:markedFocus.length, '
            'focus_production_leaks:liveFocusLeaks,focus_unmarked_local_links:unmarkedLocalFocus,')

def sha(x): return hashlib.sha256(x).hexdigest()

def repair(source: bytes):
    text = source.decode('utf-8')
    for old,new in [(OLD,NEW),(OLD_BLOCK,NEW_BLOCK),(OLD_DATA,NEW_DATA)]:
        if text.count(old) != 1: raise ValueError('Refuse unexpected receipt-source drift at '+old[:65])
        text = text.replace(old,new,1)
    if text.count('FOCUS_LOCAL_LINKS_NOT_5_OR_INVALID') != 1: raise ValueError('Missing new test')
    return text.encode('utf-8')

def build(parent: bytes):
    if sha(parent) != PARENT_SHA256: raise ValueError('Wrong protected PR #1620 parent ZIP')
    with zipfile.ZipFile(io.BytesIO(parent)) as z:
        if z.testzip() is not None: raise ValueError('CRC failure in protected parent')
        existing={n:z.read(n) for n in z.namelist()}
        if sha(existing[RECEIPT]) != OLD_RECEIPT_SHA256: raise ValueError('Wrong old receipt plugin')
        original=existing[RECEIPT]
        patched=repair(original)
        existing[RECEIPT]=patched
        custody=json.loads(existing['SOURCE_CUSTODY.json'])
        custody['files_sha256'][RECEIPT]=sha(patched)
        custody['receipt_focus_route_repair']={
            'parent_sha256':PARENT_SHA256,
            'old_receipt_sha256':OLD_RECEIPT_SHA256,
            'new_receipt_sha256':sha(patched),
            'change':'Receipt evaluates five local route markers, prohibits production Focus links and forged/unmarked local routes',
            'wordpress_core_executed':False,'jetpack_tested':False,'release_authorized':False}
        existing['SOURCE_CUSTODY.json']=(json.dumps(custody,indent=2,ensure_ascii=False)+'\n').encode()
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as dst:
            for info in z.infolist():
                zi=zipfile.ZipInfo(info.filename,info.date_time)
                zi.compress_type=zipfile.ZIP_DEFLATED
                zi.external_attr=info.external_attr
                dst.writestr(zi,existing[info.filename],compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
        return out.getvalue(),original,patched

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--parent',required=True,type=Path);ap.add_argument('--output',required=True,type=Path)
    args=ap.parse_args();result,old,new=build(args.parent.read_bytes())
    args.output.write_bytes(result)
    print(json.dumps({'parent_sha256':PARENT_SHA256,'patched_sha256':sha(result),
      'receipt_before_sha256':sha(old),'receipt_after_sha256':sha(new),
      'other_source_files_unchanged':True,'release':'HOLD'},indent=2))
if __name__ == '__main__': main()
