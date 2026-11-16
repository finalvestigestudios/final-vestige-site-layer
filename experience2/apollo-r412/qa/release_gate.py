#!/usr/bin/env python3
"""Read-only fail-closed acceptance status. Never promotes a fixture to staging."""
from pathlib import Path
import json
import sys

def audit(data: dict) -> dict:
    blockers=[]
    if data.get('chromium_http_navigation',{}).get('status')!='AVAILABLE':
        blockers.append('Chromium real HTTP navigation not verified')
    if not data.get('metrics'):
        blockers.append('Navigated fixture LCP/CLS absent')
    else:
        for entry in data['metrics']:
            if entry.get('lcp_ms') is None or entry.get('cls') is None:
                blockers.append('Missing performance entry');break
    if data.get('axe_core',{}).get('status')!='EXECUTED':
        blockers.append('Genuine axe-core not executed')
    if data.get('axe_core',{}).get('violations') != []:
        blockers.append('No authenticated zero-violation axe report')
    if not data.get('installed_wordpress'):
        blockers.append('Installed WordPress/Assembler staging untested')
    if not data.get('real_production_cwv'):
        blockers.append('Real-origin/p75 Core Web Vitals not established')
    # Independent human review cannot be auto-granted from local source QA.
    blockers.extend(['Independent QD/source-rights review pending','Founder production release approval pending','Exact-head CI evidence pending'])
    return {'release':'HOLD' if blockers else 'ELIGIBLE_FOR_HUMAN_REVIEW', 'blockers':blockers}

if __name__=='__main__':
    base=Path(__file__).resolve().parents[1]
    data=json.loads((base/'QA/http_report.json').read_text(encoding='utf-8'))
    result=audit(data)
    (base/'QA/release_gate.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
    sys.exit(2 if result['release']=='HOLD' else 0)
