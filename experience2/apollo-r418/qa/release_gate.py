"""Fail-closed readiness evaluator; must NOT interpret fixtures as installed WordPress acceptance."""
import json
import sys
from pathlib import Path

REQUIRED = ('installed_wordpress_staging_url', 'navigated_playwright', 'axe_core_violations',
            'lcp_ms', 'cls', 'keyboard_screenreader_review', 'independent_qd_approval',
            'exact_head_ci_green', 'founder_release_authorization')

def evaluate(payload):
    missing=[key for key in REQUIRED if key not in payload]
    problems=['missing '+item for item in missing]
    if payload.get('installed_wordpress_staging_url') in (None,'',False): problems.append('no installed WordPress staging URL')
    for key in ('navigated_playwright','keyboard_screenreader_review','independent_qd_approval',
                'exact_head_ci_green','founder_release_authorization'):
        if payload.get(key) is not True: problems.append(key+' not verified')
    if type(payload.get('axe_core_violations')) is not int or payload.get('axe_core_violations') != 0:
        problems.append('genuine axe-core zero-violation result not verified')
    try:
        lcp=payload.get('lcp_ms');cls=payload.get('cls')
        if type(lcp) not in (int,float) or lcp <=0 or lcp>2500: problems.append('LCP is missing or exceeds 2500ms')
        if type(cls) not in (int,float) or cls<0 or cls>0.1: problems.append('CLS is missing or exceeds 0.1')
    except TypeError:
        problems.append('performance measurements invalid')
    # Authenticated human acceptance and exact-head status must be checked externally;
    # JSON alone cannot establish an independently verified release authorization.
    problems.append('offline acceptance cannot authenticate founder, QD or exact-head CI status')
    return {'decision':'HOLD','release_permitted':False,'blockers':sorted(set(problems))}

if __name__=='__main__':
    path=Path(sys.argv[1]) if len(sys.argv)>1 else None
    data=json.loads(path.read_text()) if path else {}
    result=evaluate(data)
    print(json.dumps(result,indent=2,sort_keys=True))
    sys.exit(2)
