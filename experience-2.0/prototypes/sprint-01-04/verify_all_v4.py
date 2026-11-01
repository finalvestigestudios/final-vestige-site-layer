"""Run all available Experience 2.0 research contract checks. Returns nonzero on failures."""
from pathlib import Path
import subprocess,json,hashlib,sys,datetime
root=Path(__file__).resolve().parent
checks=[
    ['python','verify_concept_board.py'],
    ['python','flagship-apollo1/verify_flagship.py'],
    ['python','verify_atlas_preview.py'],
    ['python','source-ledger/build_ledger.py'],
    ['python','source-ledger/verify_ledger.py'],
    ['php','-l','source-ledger/wp-staging-plugin/final-vestige-ex2-research-desk.php'],
]
results=[]
for check in checks:
    proc=subprocess.run(check,cwd=root,capture_output=True,text=True)
    results.append({'command':' '.join(check),'exit_code':proc.returncode,'summary':(proc.stdout.strip().splitlines() or [''])[0],'stderr_tail':proc.stderr[-1200:]})
    print(('PASS' if proc.returncode==0 else 'FAIL')+' '+ ' '.join(check))
    if proc.returncode: print(proc.stdout[-1800:],proc.stderr[-1800:],file=sys.stderr)
assets=['source-ledger/wordpress-block.html','source-ledger/wp-staging-plugin/final-vestige-ex2-research-desk.php','source-ledger/wp-staging-plugin/templates/ledger.html','source-ledger/wp-staging-plugin/assets/source-ledger.css','source-ledger/wp-staging-plugin/assets/source-ledger.js','source-ledger/source-ledger.css','source-ledger/source-ledger.js','source-ledger/index.html','source-ledger/QA_RESULTS.json','flagship-apollo1/source_manifest.json']
hashes={path:{'bytes':(root/path).stat().st_size,'sha256':hashlib.sha256((root/path).read_bytes()).hexdigest()} for path in assets}
summary={'project':'Final Vestige Experience 2.0 — research prototypes','status':'no production deployment or independent release approval','checks':results,'artifacts':hashes,'all_passed':all(x['exit_code']==0 for x in results),'environment_limitations':['Chromium browser tests only, not Safari or actual screen reader','External NASA assets blocked in capture environment','WordPress shortcode adapter not installed in WP staging','No field Core Web Vitals measured']}
(root/'QA_V4_MANIFEST.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
if not summary['all_passed']:sys.exit(1)
print('QA V4 MANIFEST: all six command checks passed; SHA-256 recorded for',len(assets),'key files')
