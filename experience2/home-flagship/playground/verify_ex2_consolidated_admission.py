#!/usr/bin/env python3
"""Offline evidence admission for FV's protected seven-chapter flagship.

This script cannot authorize release. It distinguishes proven offline observations
from native WordPress, real-network, WCAG, commercial and founder acceptance.
Does not make network requests, touch a CMS, or submit a subscriber form.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

PINNED_BLUEPRINT = '9833800a112027b17dfec154358d7b630e258feb581820b749ca26ab88ffe69d'
PINNED_PLUGIN = '91adf4e42a711bf253370a706b29d1428131051333e470af4a841948d1e97b04'
WIDTHS = {320, 360, 390, 768, 1024, 1440, 1920}
INTERACTIONS = ('case_switch_to_franklin', 'chronicle_1848', 'observer_b', 'chapter_navigation')
NEGATIVES = ('missing_margin', 'missing_focus', 'missing_chapter_target')


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def load_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def fact(name, ok, finding, scope='OFFLINE'):
    return {'gate': name, 'pass': bool(ok), 'scope': scope, 'finding': finding}


def inspect(blueprint, php, browser, media):
    """Prove source custody and offline results; never upgrade fixtures into live proof."""
    findings=[]
    blob=Path(blueprint).read_bytes()
    bundle_hash=sha256(blob)
    findings.append(fact('protected_zip_sha256',bundle_hash==PINNED_BLUEPRINT, bundle_hash))
    plugin_hash=None
    try:
        with zipfile.ZipFile(blueprint) as z:
            paths=z.namelist()
            plugin=z.read('mu-plugins/fv-ex2-playground-review.php')
            plugin_hash=sha256(plugin)
            # A fake ZIP with a single copied plugin is not a usable WordPress blueprint.
            expected={'blueprint.json','mu-plugins/fv-ex2-playground-review.php',
                      'mu-plugins/fv-ex2-private-browser-receipt.php','SOURCE_CUSTODY.json'}
            bundle_complete=expected.issubset(paths)
            manifest=json.loads(z.read('SOURCE_CUSTODY.json'))
            custody_ok=(bundle_complete and manifest.get('files_sha256',{}).get(
                'mu-plugins/fv-ex2-playground-review.php')==plugin_hash and
                manifest.get('local_only_preflight_first') is True)
    except (zipfile.BadZipFile,KeyError,ValueError,json.JSONDecodeError):
        custody_ok=False
    findings.append(fact('protected_plugin_source_custody',custody_ok and plugin_hash==PINNED_PLUGIN,
                         f'plugin_sha256={plugin_hash}; complete_manifest={custody_ok}'))
    try:
        p=load_json(php)
        scenarios={s['scenario']:s for s in p['scenarios']}
        php_ok=(p.get('identity')=='OFFLINE_PHP_HOOK_STUB_NOT_WORDPRESS_CORE' and
                p.get('baseline_sha256')==PINNED_BLUEPRINT and
                p.get('plugin_sha256')==PINNED_PLUGIN and
                scenarios['valid']['pass'] is True and scenarios['valid']['html_bytes']>45000 and
                scenarios['flag_off']['pass'] is True and scenarios['flag_off']['html_bytes']==0 and
                scenarios['wrong_page']['pass'] is True and scenarios['wrong_page']['html_bytes']==0)
    except (KeyError,TypeError,ValueError,FileNotFoundError):
        php_ok=False
    findings.append(fact('isolated_php_hook_admission',php_ok,
                         'Actual candidate PHP with WordPress callbacks stubbed; not WordPress-core execution'))
    try:
        b=load_json(browser)
        configs=b['results']
        grid={(i['width'],i['zoom'],i['javascript']) for i in configs if i.get('pass') is True}
        browser_ok=(b.get('bundle_sha256')==PINNED_BLUEPRINT and
                    'NOT WordPress' in b.get('scope','') and
                    b.get('configs')==28 and b.get('passed')==28 and len(configs)==28 and
                    grid=={(w,z,j) for w in WIDTHS for z in (1,2) for j in (False,True)} and
                    all(i['measurements'].get('chapters')==7 and
                        i['measurements'].get('margins')==72 and
                        i['measurements'].get('focus_count')==5 and
                        i['measurements'].get('chapter_targets_present') is True and
                        i['measurements'].get('overflow') is False and
                        i['measurements'].get('firstscreen_focus',0)>=1 for i in configs) and
                    all(b['interactions'][key]['pass'] is True for key in INTERACTIONS) and
                    all(b['negative_controls'][key]['correctly_rejected'] is True for key in NEGATIVES))
    except (KeyError,TypeError,ValueError,FileNotFoundError):
        browser_ok=False
    findings.append(fact('full_source_chromium_offline',browser_ok,
                         '28 JS/no-JS/zoom modes, 4 interactions and 3 negative controls; offline only'))
    try:
        m=load_json(media)
        results=m.get('results',[])
        media_ok=(m.get('candidate_plugin_sha256')==PINNED_PLUGIN and
                  m.get('bundle_sha256')==PINNED_BLUEPRINT and
                  'OFFLINE_NOT_WORDPRESS_ASSEMBLER' in m.get('identity','') and
                  len(results)>=10 and
                  {x['scenario'] for x in results}=={'offline-blocked','fixture-valid'} and
                  all(x.get('image_gate_pass_on_real_host') is False and
                      x.get('release_pass') is False for x in results))
    except (KeyError,TypeError,ValueError,FileNotFoundError):
        media_ok=False
    findings.append(fact('synthetic_media_controls_admitted',media_ok,
                         'Fixture-valid images are NOT evidence of historical media network transfer'))

    # Explicitly non-inferable from offline source fixtures. These cannot turn green
    # merely because a JSON receipt names them PASS; independent QA is required.
    missing=[
        ('actual_wordpress_assembler','Isolated WordPress core + pinned Assembler theme render not executed'),
        ('actual_archival_image_bytes','Apollo and Franklin original/CDN bytes not downloaded and decoded in browser'),
        ('independent_axe_wcag_2_2_aa','Real integrated axe and manual WCAG 2.2 AA evidence unavailable'),
        ('lighthouse_cwv','Real Lighthouse lab and field Core Web Vitals unavailable'),
        ('live_jetpack_conversion','No verified live Jetpack signup interaction or confirmed lead'),
        ('paid_order_net_revenue','No independently verified orders/fees/refunds or realized net revenue'),
        ('asset_rights_approval','Final rights review incomplete; NYPL remains excluded'),
        ('exact_head_ci_and_qd','CI green on exact head and independent QD PASS outstanding'),
        ('founder_visual_and_release','Founder art-direction acceptance and exact release authorization outstanding')
    ]
    for gate,reason in missing:
        findings.append(fact(gate,False,reason,scope='RELEASE'))
    offline_ok=all(f['pass'] for f in findings if f['scope']=='OFFLINE')
    return {
        'decision':'HOLD', 'offline_evidence_integrity':'PASS' if offline_ok else 'FAIL',
        'release_authorized':False, 'source_bundle_sha256':bundle_hash,
        'expected_source_bundle_sha256':PINNED_BLUEPRINT,
        'protected_source_plugin_sha256':plugin_hash,
        'evidence_count':len(findings), 'findings':findings,
        'funnel':{'offer':'52-page Focus Fieldbook',
                  'step':'homepage evidence -> Focus /focus/ -> verified Jetpack lead -> confirmed paid order',
                  'blocker':'live signup confirmation, real integrated homepage, and paid-order attribution not proven',
                  'change':'single fail-closed release decision from multiple prior offline suites',
                  'pass_fail_evidence': 'Offline source accepted only; all unverified release gates remain HOLD',
                  'owner':'FV interim homepage + Site QA; Claude owns live Jetpack/checkout/attribution'},
        'kpi_net_revenue_per_1000_qualified_human_sessions':None,
        'kpi_caveat':'No qualifying-session counts or independently confirmed paid conversions supplied.',
    }


def as_markdown(report):
    x=['# Experience 2.0 — seven-chapter consolidated admission', '',
       '**Decision: HOLD. Not a WordPress staging or release certificate.**', '',
       f"Source-custody and prior offline evidence: **{report['offline_evidence_integrity']}**", '',
       '| Gate | Scope | Evidence |', '|---|---|---|']
    for f in report['findings']:
        x.append('| '+f['gate']+' | '+f['scope']+' | '+('PASS' if f['pass'] else 'HOLD' if f['scope']=='RELEASE' else 'FAIL')+' — '+f['finding'].replace('|','/').replace('\n',' ')+' |')
    x+=['','## Commercial decision','',
         '**Offer:** existing 52-page Focus Fieldbook. **Funnel:** social traffic → source-led homepage → Focus → independently confirmed subscriber → independently confirmed paid order.',
         '', '**Blocker:** Real signup, image delivery, integrated WordPress, and paid attribution remain unverified.',
         '', '**Change:** This artifact gathers actual offline receipts and refuses to promote synthetic results into production evidence.',
         '', '**Experiment:** On an authorized isolated WordPress/Assembler instance, run the exact candidate with real archival image responses, keyboard/no-JS/axe, Lighthouse, and read-only Focus control checks; route actual paid-order attribution to Claude.',
         '', '**Owner:** Interim homepage engineering / independent Site QA; Claude owns Jetpack/checkout/analytics; Grok and Praxxis own acquisition.',
         '', '**Net revenue per 1,000 qualified sessions:** unknown; no commerce source ingested.',
         '', '**Safety:** no CMS write, subscription submission, affiliate activation, public staging, deployment, or approval.', '']
    return '\n'.join(x)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for field in ['blueprint','php','browser','media']:
        parser.add_argument('--'+field,required=True)
    parser.add_argument('--output',required=True)
    ns=parser.parse_args()
    report=inspect(ns.blueprint,ns.php,ns.browser,ns.media)
    out=Path(ns.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    out.with_suffix('.md').write_text(as_markdown(report),encoding='utf-8')
    print(f"{report['decision']}: offline evidence {report['offline_evidence_integrity']}; {len(report['findings'])} gates; {out}")
    # Exit non-zero for tampered/broken offline evidence. HOLD itself is the expected
    # output in a nonproduction environment, not an executable failure.
    return 0 if report['offline_evidence_integrity']=='PASS' else 2


if __name__=='__main__':
    sys.exit(main())
