#!/usr/bin/env python3
"""R403: verify *applied* Apollo gallery CSS, not merely its HTTP delivery.

Installed-staging entrypoint wraps existing R401/R402 inspectors in-process.
Read-only; production deployment is never authorized. Independent fixture
checks can call probe(page) without importing upstream code.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path

REQUIRED_CONTEXTS = ('320','390-touch','768','1440','1920','320-nojs','390-reduced')


def probe(page):
    """Read rendered styles and actual geometry, without injecting or mutating DOM."""
    state = page.evaluate('''() => {
      const one = s => document.querySelector(s);
      const css = e => e && getComputedStyle(e);
      const root = one('.fv-r384'), grid = one('.fv-r384__grid');
      const rail = one('.fv-r384__rail ol');
      const sourceGroups = one('.fv-r384__source-groups');
      const rights = one('.fv-r384__rights');
      const next = one('.fv-r384__next a');
      const cards = [...document.querySelectorAll('.fv-r384__grid > .fv-r384__card')];
      const left = cards[0]?.getBoundingClientRect();
      const right = cards[1]?.getBoundingClientRect();
      const rgb = e => css(e)?.backgroundColor || null;
      const box = e => e ? e.getBoundingClientRect() : null;
      return {
        width:innerWidth, overflow:Math.max(0,document.documentElement.scrollWidth-innerWidth),
        rootColor:rgb(root), gridDisplay:css(grid)?.display, railDisplay:css(rail)?.display,
        sourceDisplay:css(sourceGroups)?.display, rightsBorder:parseFloat(css(rights)?.borderLeftWidth || '0'),
        cardCount:cards.length, first:left ? {x:left.x,y:left.y,w:left.width}:null,
        second:right ? {x:right.x,y:right.y,w:right.width}:null,
        linkHeight:next ? box(next).height:0, linkDisplay:css(next)?.display,
        rootFont:getComputedStyle(document.documentElement).fontSize,
      };
    }''')
    defects = []
    def require(ok, code):
        if not ok: defects.append(code)
    width=state['width']
    require(state['rootColor'] == 'rgb(21, 27, 32)', 'reviewed_background_not_applied')
    require(state['gridDisplay'] == 'grid', 'evidence_grid_css_missing')
    require(state['railDisplay'] == 'grid', 'chronology_css_missing')
    require(state['sourceDisplay'] == 'grid', 'publication_index_css_missing')
    require(state['rightsBorder'] >= 2.9, 'source_rights_boundary_css_missing')
    require(state['linkDisplay'] in ('inline-block','block') and state['linkHeight'] >= 43.5,
            'free_investigation_cta_css_missing')
    require(state['overflow'] <= 1, 'horizontal_overflow')
    if state['cardCount'] >= 2 and state['first'] and state['second']:
        first,second=state['first'],state['second']
        # CSS media queries, not mere viewport size, must control geometry.
        if width <= 740:
            require(second['y'] > first['y'] + 15, 'mobile_evidence_not_stacked')
        else:
            require(abs(second['y'] - first['y']) <= 2 and second['x'] > first['x'] + 15,
                    'desktop_evidence_not_two_columns')
    else:
        defects.append('evidence_cards_missing')
    return {'status': 'PASS' if not defects else 'HOLD', 'defects':defects, 'metrics':state}


def guard(page):
    result=probe(page)
    if result['defects']:
        raise AssertionError('rendered_css_custody:' + ','.join(result['defects']))
    return {'rendered_css_custody':'PASS', 'rendered_css_width':result['metrics']['width'],
            'rendered_css_overflow':result['metrics']['overflow']}


def inspect_receipt(report, staging):
    if not staging: return []
    if report.get('blockers') or report.get('status') != 'PASS_STAGING_BROWSER_GATE_ONLY':
        return ['upstream_staging_gate_not_passed']
    screens=report.get('screens')
    if not isinstance(screens,list) or [x.get('context') for x in screens if isinstance(x,dict)] != list(REQUIRED_CONTEXTS):
        return ['incomplete_rendered_css_contexts']
    if not all(isinstance(x,dict) and x.get('rendered_css_custody')=='PASS'
               and x.get('rendered_css_overflow',99) <= 1 for x in screens):
        return ['rendered_css_effect_not_verified_per_context']
    if report.get('r402_trace_defects'):
        return ['network_custody_not_verified']
    return []


def audit_run(args, overlay, network, base):
    """R401 wraps this exact parent inspector; restore even on exception."""
    name='inspect' if hasattr(base,'inspect') else 'inspect_gallery'
    old=getattr(base,name)
    def inspected(page):
        fields=old(page)
        fields.update(guard(page))
        return fields
    setattr(base,name,inspected)
    try:
        report=network.audit_run(args,overlay,base)
    finally:
        setattr(base,name,old)
    defects=inspect_receipt(report,bool(args.url))
    report['r403_rendered_css_defects']=defects
    report['r403_verified_application_not_only_delivery']=True
    report['release_allowed']=False
    if defects:
        report.setdefault('blockers',[]).extend(defects)
        report['status']='HARD_HOLD_RENDERED_CSS_CUSTODY'
    target=Path(args.out);target.mkdir(parents=True,exist_ok=True)
    (target/'r403-report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    g=p.add_mutually_exclusive_group(required=True);g.add_argument('--url');g.add_argument('--fixture')
    p.add_argument('--host');p.add_argument('--axe');p.add_argument('--axe-sha256')
    p.add_argument('--out',default='experience2/apollo-r403/QA')
    p.add_argument('--chromium',default='/usr/bin/chromium')
    args=p.parse_args()
    root=Path(__file__).resolve().parents[2]
    def load(name,path):
        if not path.is_file():raise SystemExit('HARD HOLD: exact source missing: '+str(path))
        s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
    overlay=load('r401_custody',root/'apollo-r401/qa/custody_overlay.py')
    network=load('r402_network',root/'apollo-r402/qa/network_custody.py')
    base,_=overlay.modules()
    report=audit_run(args,overlay,network,base)
    print(json.dumps({'status':report['status'],'r403_defects':report['r403_rendered_css_defects'],
                      'exact_parent':report.get('exact_remote_upstream'),'release_allowed':False},sort_keys=True))
    return 2 if report.get('blockers') or (args.url and not report.get('exact_remote_upstream')) else 0


if __name__=='__main__':raise SystemExit(main())
