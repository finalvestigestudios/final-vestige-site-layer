#!/usr/bin/env python3
"""Apollo R380: conservative dependency-graph security regression + local real Chromium.
Read-only; requires PHP 7.4+, Playwright Chromium. Never touches WordPress or remote services.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'apollo-r379/prehead-template-parts.php'
STUB = ROOT / 'apollo-r379/qa/wp_stub.php'
OUT = HERE.parent / 'QA'
PASS_STYLES = ('part', 'nested', 'reusable', 'duplicate', 'dag_reuse')
REJECT_GRAPH = ('cycle_with_sibling', 'block_cycle_with_sibling', 'missing_with_sibling',
                'draft_with_sibling', 'foreign_with_sibling', 'bad_ref_with_sibling')
REJECT_EXISTING = ('cycle', 'foreign_theme', 'bad_slug', 'wrong_identity', 'draft',
                   'hidden_in_attrs', 'code_sample', 'missing_part', 'wrong_template_type',
                   'oversize', 'foreign_owner', 'production', 'wronghost', 'disabled', 'no_id')


def run(*args):
    p = subprocess.run(list(args), capture_output=True, text=True, timeout=90)
    if p.returncode:
        raise AssertionError(f"{' '.join(args)} failed: {p.stderr[-500:]} {p.stdout[-500:]}")
    return p.stdout.strip().removesuffix('\\n')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for f in (SOURCE, STUB):
        run('php', '-l', str(f))
    rows=[]
    for name in PASS_STYLES + REJECT_GRAPH + REJECT_EXISTING:
        data=json.loads(run('php', str(STUB), name))
        target=1 if name in PASS_STYLES else 0
        ok=not data['failed'] and data['stylesheet_count']==target
        rows.append({'scenario':name,'expected_stylesheets':target,
                     'actual_stylesheets':data['stylesheet_count'],
                     'assertions_passed':data['passed'],'failed':data['failed'],
                     'pass':ok})
    # Exercise exactly the existing NASA source-role fixture; no fake remote staging results.
    browser=subprocess.run([sys.executable,str(ROOT/'apollo-r379/qa/browser_qa.py')],
                           text=True,capture_output=True,timeout=120)
    if browser.returncode:
        raise AssertionError('Chromium suite failed: '+browser.stdout[-1200:]+' '+browser.stderr[-900:])
    inherited=json.loads((ROOT/'apollo-r379/QA/results.json').read_text())
    assert inherited['browser_contexts']==10
    assert inherited['browser_assertions']==inherited['browser_possible_assertions']
    import shutil
    for entry in inherited['browser']:
        screenshot=ROOT/'apollo-r379'/entry['screenshot']
        shutil.copyfile(screenshot,OUT/(entry['name']+'.png'))
    passed=sum(row['pass'] for row in rows)
    report={'result':'R380_LOCAL_PHP_GRAPH_AND_CHROMIUM_FIXTURE_PASS_NOT_STAGING' if passed==len(rows) else 'FAIL',
            'scenarios':rows,'php_scenarios':len(rows),
            'php_assertions_passed':sum(row['assertions_passed'] for row in rows),
            'browser_contexts':inherited['browser_contexts'],
            'browser_assertions':inherited['browser_assertions'],
            'browser_possible_assertions':inherited['browser_possible_assertions'],
            'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            'test_sha256':hashlib.sha256(STUB.read_bytes()).hexdigest(),
            'boundary':'WP API stubs and Chromium set_content, not installed WordPress, real HTTP/CSP or field Core Web Vitals',
            'axe_core':'NOT_EXECUTED', 'native_400_percent_browser_zoom':'NOT_EXECUTED',
            'manual_screen_reader':'NOT_EXECUTED','qualified_sessions_to_paid_orders':'NOT_OBSERVABLE'}
    (OUT/'results.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(report['result'],'PHP:',passed,'/',len(rows),'assertions:',report['php_assertions_passed'],
          'Chromium:',report['browser_assertions'],'/',report['browser_possible_assertions'])
    return 0 if report['result'].startswith('R380_LOCAL') else 1

if __name__=='__main__':
    sys.exit(main())
