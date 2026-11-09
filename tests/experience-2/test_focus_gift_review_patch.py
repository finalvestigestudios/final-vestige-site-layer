#!/usr/bin/env python3
"""Synthetic, fail-closed preservation tests for guarded Page 1579 patcher."""
import importlib.util
import hashlib
import json
import sys
from pathlib import Path
tool=Path(__file__).resolve().parents[2]/'tools/experience-2/patch_focus_gift_review_only.py'
spec=importlib.util.spec_from_file_location('focus',tool)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
live='\n'.join([
"(function(){var g=document.getElementById('fvf-gift');if(!g){return;}",
"var bad=['invalid_email','error','blocked_email','opted_out','blocked'];",
"function show(){g.hidden=false;}",
"var q=null;try{q=new URLSearchParams(window.location.search).get('subscribe');}catch(e){}",
"if(q){if(bad.indexOf(q)<0){show();}}",
"var c=document.querySelector('.wp-block-jetpack-subscriptions__container');",
"function check(){if(c){if(/\\bis-subscriber\\b/.test(c.className)){show();}}}",
"check();if(c){if(window.MutationObserver){new MutationObserver(check).observe(c,{attributes:true,attributeFilter:['class']});}}})();"
])
assert hashlib.sha256(live.encode()).hexdigest()==m.EXACT_LIVE_SHA256
base='''<!-- wp:paragraph --><p>A 52-page practical guide.</p><!-- /wp:paragraph -->
<!-- wp:jetpack/subscriptions {"submitButtonText":"Send me the fieldbook"} /-->
<div id="fvf-gift" hidden><a href="/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf">Download</a></div>
<script id="fvf-gift-v2">'''+live+'''</script>'''
cases=[]
def check(label,src,expected):
    try:
        out,receipt=m.build(src)
        ok=(out.replace(m.REVIEW_SCRIPT,live)==src and
            out.count('<!-- wp:jetpack/subscriptions ')==1 and
            receipt['substituted_script_count']==1)
    except m.SourceDrift: ok=False
    cases.append({'label':label,'pass':ok==expected})
check('positive exact source',base,True)
check('irrelevant prefix preserved',base.replace('A 52-page','The 52-page'),True)
check('irrelevant suffix preserved',base+'<p>UNCHANGED</p>',True)
check('script already edited rejects',base.replace(live,m.REVIEW_SCRIPT),False)
check('source changed rejects',base.replace('if(q){if(bad.indexOf(q)<0){show();}}','if(q){show();}'),False)
check('script duplicated rejects',base+'<script id="fvf-gift-v2">'+live+'</script>',False)
check('script missing rejects',base.replace('<script id="fvf-gift-v2">'+live+'</script>',''),False)
check('Jetpack removed rejects',base.replace('<!-- wp:jetpack/subscriptions ','<!-- wp:jetpack/other '),False)
check('Jetpack duplicated rejects',base+'<!-- wp:jetpack/subscriptions {} /-->',False)
check('52-page claim missing rejects',base.replace('52-page','50-page'),False)
check('PDF filename drift rejects',base.replace('Complete_Edition.pdf','Unverified.pdf'),False)
check('gift element missing rejects',base.replace('id="fvf-gift"','id="other"'),False)
for label,data in [('wrong-page',{'id':6,'status':'publish','content':base}),
                   ('draft-page',{'id':1579,'status':'draft','content':base}),
                   ('no-content',{'id':1579,'status':'publish'})]:
    try: m.editor_source({'data':data});okay=False
    except m.SourceDrift:okay=True
    cases.append({'label':label,'pass':okay})
print(json.dumps({'total':len(cases),'passed':sum(x['pass'] for x in cases),'cases':cases},indent=2))
if not all(x['pass'] for x in cases):sys.exit(1)
