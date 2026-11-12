#!/usr/bin/env node
'use strict';
/*
 * FV Mind R307 pre-release source-only validator. Run:
 *   node mind/r307/verify_r307.cjs
 * This is NOT browser WCAG, WordPress sanitization, real video playback,
 * affiliate approval, provider settlement or commercial release evidence.
 */
const fs=require('node:fs');
const path=require('node:path');
const dir=__dirname;
const names={
  article:'WHEN-THE-HYPNOTIST-BECAME-HIS-OWN-SUBJECT-UNPUBLISHED.md',
  a:'ZEN12-A-TEXT-GUIDE-REVIEW-ONLY.html',
  b:'ZEN12-B-OPTIONAL-FILM-STORYBOARD-REVIEW-ONLY.html',
  hub:'MIND-FOUR-STREAM-ARCHIVE-REVIEW-ONLY.html',
  matrix:'SELF-HYPNOSIS-SOURCES-CLAIMS-AND-COMMERCE-HOLDS.json',
  plan:'ONE-OFFER-CONVERSION-MEASUREMENT-AND-RELEASE-ACCEPTANCE.md'
};
const load=()=>Object.fromEntries(Object.entries(names).map(([k,f])=>[k,fs.readFileSync(path.join(dir,f),'utf8')]));
const filmRe=/<section class="band" id="optional-film"[\s\S]*?<\/section>/;
function validate(f){
 const err=[];
 const check=(condition,id)=>{if(!condition)err.push(id)};
 let m;try{m=JSON.parse(f.matrix)}catch(e){return ['INVALID_MATRIX_JSON']}
 check(m.schema==='FV-MIND-R307-v1','MATRIX_SCHEMA');
 check(m.published===false&&m.commercial_status==='HARD_HOLD'&&m.publisher_accepted==='UNVERIFIED','MATRIX_HOLD');
 const srcs=m.sources||[],claims=m.claims||[],gates=m.gates||[];
 check(srcs.length===22&&new Set(srcs.map(x=>x.id)).size===22&&new Set(srcs.map(x=>x.url)).size===22,'SOURCES_UNIQUE');
 check(srcs.every(s=>/^https:\/\//.test(s.url)&&s.reading_scope&&s.kind),'SOURCE_PROVENANCE');
 const ids=new Set(srcs.map(s=>s.id));
 check(claims.length===30&&new Set(claims.map(c=>c.id)).size===30,'CLAIM_COUNT');
 check(claims.every(c=>ids.has(c.source_id)&&c.scope&&c.status),'CLAIM_REFERENCES');
 check(gates.length===18&&new Set(gates.map(g=>g.id)).size===18&&gates.every(g=>g.status==='HARD_HOLD'&&g.required_proof),'GATE_HARD_HOLD');
 check((m.creator_paths||[]).length===3&&(m.creator_paths||[]).every(p=>p.asset_id===null),'CREATOR_IDS_UNVERIFIED');
 check(m.financial_status?.net_revenue_per_1000_humans===null&&m.financial_status?.cleared_affiliate_commission===null,'NET_REVENUE_UNKNOWN');
 for(const key of ['a','b','hub']){
  const h=f[key];
  check(/<html lang="en">/.test(h)&&/name="viewport"/.test(h)&&/name="robots" content="noindex,nofollow"/.test(h),'HTML_META_'+key);
  check(/class="skip" href="#main"/.test(h)&&/<main id="main"/.test(h),'SKIP_MAIN_'+key);
  check(/<button\s+type="button"\s+disabled\b/.test(h),'ACTUALLY_DISABLED_'+key);
  check(/potential affiliate disclosure/i.test(h)&&/may earn a commission at no additional cost to you/i.test(h),'ADJACENT_DISCLOSURE_'+key);
  check(/aria-describedby="(?:withheld|hold-hub)"/.test(h),'BUTTON_DESCRIPTION_'+key);
  check(!/<script\b|<iframe\b|<form\b|<input\b|<video\b|<audio\b/i.test(h),'NO_FORMS_SCRIPT_OR_MEDIA_'+key);
  check(!/\bon(?:click|load|error|submit|play)\s*=|<meta[^>]+http-equiv=["']refresh|<link[^>]+rel=["']preload/i.test(h),'NO_EVENT_OR_REDIRECT_'+key);
  check(!/<a[^>]+href=["'][^"']*(?:zen12\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)/i.test(h),'NO_MERCHANT_LINK_'+key);
  check(!/<(?:button|a)[^>]+(?:hidden\b|style=["'][^"']*display\s*:\s*none)/i.test(h),'NO_HIDDEN_PURCHASE_CONTROL_'+key);
  check(/prefers-reduced-motion:reduce/.test(h)&&/@media\(max-width:720px\)/.test(h),'CSS_MOBILE_REDUCED_'+key);
 }
 check(!filmRe.test(f.a)&&filmRe.test(f.b),'FILM_VARIANT');
 check(f.a===f.b.replace(filmRe,''),'A_B_COPY_IDENTICAL_EXCEPT_FILM');
 check(/42-second/.test(f.b)&&/caption concept/.test(f.b)&&/<svg\b/.test(f.b)&&/<details open>/.test(f.b),'B_STATIC_ACCESSIBLE_FILM');
 check(/No video player is present/.test(f.b)&&/NOT an encoded, playable or hosted video/i.test(f.plan),'NO_FALSE_VIDEO');
 check(/<h1>Don't buy twelve minutes of a promise\.<\/h1>/.test(f.a),'BUYER_HOOK');
 check(/12 levels and 48 MP3 recordings/.test(f.a),'EXACT_PACKAGE');
 check(/33 minutes and 47 MB/.test(f.a)&&/15- and 30-minute/.test(f.a),'PRODUCTS_DISTINCT');
 check(/seller's “one hour in twelve minutes” equivalence/.test(f.a),'FALSE_EQUIVALENCE_REJECTED');
 check(!/zen12 is clinically proven|zen12 guarantees focus|brainwave shots cures/i.test(f.a+f.b+f.article),'NO_UNSUPPORTED_EFFICACY');
 check(/Braid/.test(f.article)&&/Puységur/.test(f.article)&&/1843/.test(f.article)&&/2023 systematic review/.test(f.article),'ARTICLE_SOURCES');
 check(/Bibliographic record accessed/.test(f.article)&&/full data not independently assessed/.test(f.article),'SOURCE_DEPTH_DISCLOSED');
 check(/NOT COMPUTABLE/.test(f.plan)&&/affiliate_outbound/.test(f.plan)&&/cleared commission/.test(f.plan),'REALIZED_METRIC_CONTRACT');
 check(/FTC/.test(f.plan)&&/Founder/.test(f.plan)&&/PR #172/.test(f.plan),'GOVERNANCE');
 return err;
}
const base=load();
const baseline=validate(base);
if(baseline.length){console.error('BASELINE FAILED',baseline);process.exitCode=1;}
else console.log('R307 source baseline PASS');
const mutations=[
 ['remove actual disabled','a',/<button type="button" disabled/,'<button type="button"','ACTUALLY_DISABLED_a'],
 ['remove B disabled','b',/<button type="button" disabled/,'<button type="button"','ACTUALLY_DISABLED_b'],
 ['remove hub disabled','hub',/<button type="button" disabled/,'<button type="button"','ACTUALLY_DISABLED_hub'],
 ['remove disclosure A','a',/Potential affiliate disclosure/g,'Unlabeled relationship','ADJACENT_DISCLOSURE_a'],
 ['remove disclosure B','b',/Potential affiliate disclosure/g,'Unlabeled relationship','ADJACENT_DISCLOSURE_b'],
 ['remove hub disclosure','hub',/Potential affiliate disclosure/g,'Unlabeled relationship','ADJACENT_DISCLOSURE_hub'],
 ['insert A merchant link','a',/<\/body>/,'<a href="https://zen12.com/getstarted">BUY</a></body>','NO_MERCHANT_LINK_a'],
 ['insert B merchant link','b',/<\/body>/,'<a href="https://zen12.com/getstarted">BUY</a></body>','NO_MERCHANT_LINK_b'],
 ['insert script','hub',/<\/body>/,'<script src="https://tracker.example/x.js"></script></body>','NO_FORMS_SCRIPT_OR_MEDIA_hub'],
 ['insert extra signup','hub',/<\/body>/,'<form><input name="email"></form></body>','NO_FORMS_SCRIPT_OR_MEDIA_hub'],
 ['insert iframe','a',/<\/body>/,'<iframe src="https://example.com"></iframe></body>','NO_FORMS_SCRIPT_OR_MEDIA_a'],
 ['insert autoplaying video','b',/<\/body>/,'<video autoplay src="x.mp4"></video></body>','NO_FORMS_SCRIPT_OR_MEDIA_b'],
 ['insert click handler','a',/<\/body>/,'<button onclick="track()">Click</button></body>','NO_EVENT_OR_REDIRECT_a'],
 ['insert page redirect','b',/<\/head>/,'<meta http-equiv="refresh" content="0;url=https://example.com"></head>','NO_EVENT_OR_REDIRECT_b'],
 ['change B buyer copy','b',/Buy a recording library only if/,'Buy a miracle library only if','A_B_COPY_IDENTICAL_EXCEPT_FILM'],
 ['remove film poster','b',/<svg[\s\S]*?<\/svg>/,'','B_STATIC_ACCESSIBLE_FILM'],
 ['remove B caption text','b',/caption concept/g,'moving visuals','B_STATIC_ACCESSIBLE_FILM'],
 ['remove NO VIDEO caveat','b',/No video player is present/,'Already a live video','NO_FALSE_VIDEO'],
 ['destroy source ID','matrix',/"source_id": "B1843"/,'"source_id": "FICTITIOUS"','CLAIM_REFERENCES'],
 ['approve gate','matrix',/"status": "HARD_HOLD"/,'"status": "APPROVED"','GATE_HARD_HOLD'],
 ['fabricate paid revenue','matrix',/"net_revenue_per_1000_humans": null/,'"net_revenue_per_1000_humans": 750','NET_REVENUE_UNKNOWN'],
 ['fabricate creator asset','matrix',/"asset_id": null/,'"asset_id": "invented"','CREATOR_IDS_UNVERIFIED'],
 ['remove source scope','matrix',/"reading_scope": "Braid 1843 publication record, not full-book transcription"/,'"reading_scope": ""','SOURCE_PROVENANCE'],
 ['remove free alternative','a',/12 levels and 48 MP3 recordings/,'12 incredible levels','EXACT_PACKAGE'],
 ['overstate study','a',/seller's “one hour in twelve minutes” equivalence/,'verified one-hour equivalence','FALSE_EQUIVALENCE_REJECTED'],
 ['erase article provenance','article',/Bibliographic record accessed/,'Full book independently transcribed','SOURCE_DEPTH_DISCLOSED'],
 ['erase financial caveat','plan',/NOT COMPUTABLE/g,'$0','REALIZED_METRIC_CONTRACT'],
 ['drop publisher hard hold','matrix',/"publisher_accepted": "UNVERIFIED"/,'"publisher_accepted": "APPROVED"','MATRIX_HOLD']
];
let passed=0;
if(!baseline.length) for(const [label,key,find,replacement,expected] of mutations){
 const test={...base},before=test[key],after=before.replace(find,replacement);
 if(after===before){console.error('MUTATION NOT APPLIED',label);process.exitCode=1;continue;}
 test[key]=after;
 const failures=validate(test);
 if(failures.includes(expected)){passed++;}
 else {console.error('WRONG OR MISSED GUARD',label,expected,failures);process.exitCode=1;}
}
console.log('R307 mutation guards '+passed+'/'+mutations.length+' expected rejections');
if(passed!==mutations.length)process.exitCode=1;
