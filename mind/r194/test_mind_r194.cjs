'use strict';
/* R194 source-level regression & adversarial tests; do NOT confuse with native
   browser/merchant/Jetpack testing.
   Run from the repository root: node mind/r194/test_mind_r194.cjs
*/
const files={
  article:'mind/r194/the-face-that-looked-normal-upside-down-THATCHER-INVESTIGATION-UNPUBLISHED.md',
  hub:'mind/r194/mind-four-stream-hub-WORDPRESS-UNPUBLISHED-PREVIEW.html',
  ledger:'mind/r194/CLAIM-PROOF-PUBLISHER-ELIGIBILITY-REVENUE-GATES.json',
  plan:'mind/r194/OFFER-FIRST-CREATOR-FIT-AB-AND-PAID-ACCEPTANCE.md',
  priorArticle:'mind/r193/the-gorilla-was-right-there-EXPERT-INATTENTION-UNPUBLISHED.md',
  priorLedger:'mind/r193/VERIFIED-SOURCES-CLAIMS-AUTHORIZATION-GATES.json',
  A:'mind/r188/zen12-variant-A-independent-text-UNPUBLISHED.html',
  B:'mind/r188/zen12-variant-B-optional-42s-storyboard-UNPUBLISHED.html'
};
function checks(f){
  const results=[],ok=(pass,name)=>results.push({pass:!!pass,name});
  let ledger={},old={};try{ledger=JSON.parse(f.ledger)}catch(e){}try{old=JSON.parse(f.priorLedger)}catch(e){}
  const src=ledger.sources||[],cl=ledger.claims||[],gates=ledger.gates||[],sourceIds=new Set(src.map(v=>v.id));
  const gate=(x)=>gates.find(v=>v.id===x);
  ok(f.article.trim().split(/\s+/).length>=1900,'original deep investigation >=1900 words');
  ok(/1980/.test(f.article),'1980 origin');
  ok(/1993/.test(f.article),'1993 study');
  ok(/1997/.test(f.article),'1997 study');
  ok(/2001/.test(f.article),'2001 study');
  for(const s of ['10.1068/p090483','8354050','10.1068/p260225','10.1068/p3174'])ok(f.article.includes(s),'primary source '+s);
  ok(/but not.*grotesque-expression/i.test(f.article),'distinct expression-control result');
  ok(/gradual/i.test(f.article)&&/abrupt/i.test(f.article),'angles not a magic switch');
  ok(/copyright|rights-cleared/i.test(f.article),'portrait image rights boundary');
  ok(/not.*(clinical|diagnostic)/i.test(f.article),'not a clinical test');
  ok(/seller claims|seller advertising|marketing/i.test(f.article),'commercial scientific firewall');
  ok(!/https?:\/\/(?:www\.)?awin1\.com\/cread|partnerid=|affiliate_id=/i.test(f.article),'no earning URLs in research');
  ok(src.length>=15,'documented sources >=15');
  ok(cl.length>=18,'claim decisions >=18');
  ok(gates.length>=17,'release gates >=17');
  ok(src.every(v=>v.id&&/^https:\/\//.test(v.url)),'all sources real https URLs');
  ok(sourceIds.size===src.length,'unique source ids');
  ok(cl.every(v=>v.source_ids?.length&&v.source_ids.every(x=>sourceIds.has(x))),'all claim source refs resolve');
  ok(new Set(cl.map(v=>v.id)).size===cl.length,'unique claim ids');
  ok(gates.every(v=>v.pass===false),'all commercial/release gates false');
  for(const id of ['publisher_acceptance','allowed_channels','earning_url','merchant_price','merchant_refunds','merchant_paid_order','net_settlement','qualified_sessions','founder_release'])
    ok(gate(id)?.pass===false,'hard hold '+id);
  ok(ledger.net_revenue_per_1000_qualified_humans==='NOT_COMPUTABLE','net revenue unknown not fake zero');
  ok(ledger.paid_orders_verified===null,'paid orders unknown');
  ok(ledger.commission_received_verified===null,'commission received unknown');
  ok(ledger.privacy?.no_new_script===true,'no analytics scripts');
  ok(!ledger.privacy?.UTM_fields?.some(x=>/email|user_id|ip_address/i.test(x)),'no user PII in attribution');
  ok(/<!doctype html>/i.test(f.hub),'standalone hub HTML');
  ok(/<html lang="en">/i.test(f.hub),'language for screen readers');
  ok(/<meta name="viewport"/i.test(f.hub),'responsive viewport');
  ok(/<meta name="robots" content="noindex,nofollow"/i.test(f.hub),'unpublished noindex');
  ok(/class="skip"/.test(f.hub),'skip navigation');
  ok(/id="content"/.test(f.hub),'skip target');
  ok(/focus-visible/.test(f.hub),'visible keyboard focus');
  ok(/prefers-reduced-motion/.test(f.hub),'reduced motion');
  ok(/@media\(max-width:720px\)/.test(f.hub),'mobile layout');
  ok(!/<script\b/i.test(f.hub),'no Javascript');
  ok(!/<form\b/i.test(f.hub),'no second signup form');
  ok(!/<(?:iframe|video|audio)\b/i.test(f.hub),'no embeds or autoplay');
  ok(/finalvestige\.com\/focus\//.test(f.hub),'existing one Focus funnel');
  ok(/puysegurs-animal-magnetism-files/.test(f.hub),'published historical archive destination');
  ok(/2026\/11\/02\/mesmerism\//.test(f.hub),'correct Mesmerism slug');
  ok(/2026\/11\/02\/change-blindness\//.test(f.hub),'correct Change Blindness slug');
  ok(/https:\/\/zen12\.com\/hnp/.test(f.hub),'exact public vendor for independent information');
  ok(/non-affiliate informational link/.test(f.hub),'merchant-info non earning label');
  ok(/Final Vestige may earn a commission/i.test(f.hub),'clear prospective FTC disclosure');
  const b=[...f.hub.matchAll(/<button\b[^>]*>/gi)].map(x=>x[0]);
  ok(b.length===1,'exactly one placeholder purchase control');
  ok(b.every(x=>/\sdisabled(?:\s|=|>)/i.test(x)),'native disabled attribute');
  ok(b.every(x=>!/onclick|formaction|href=/i.test(x)),'no active purchase action');
  const disclose=f.hub.indexOf('Final Vestige may earn a commission'),button=f.hub.indexOf('<button type="button"');
  ok(disclose>=0&&button>disclose&&button-disclose<750,'disclosure proximate to merchant CTA');
  ok(f.plan.includes('NOT COMPUTABLE'),'plan reports unknown revenue honestly');
  ok(f.plan.includes('affiliate_outbound'),'click not paid sale');
  ok(f.plan.includes('merchant')&&f.plan.includes('Grok'),'purchase + creator ownership');
  ok(f.plan.includes('Variant')||f.plan.includes('42-second'),'A/B hypothesis present');
  ok(f.plan.includes('non-PII')&&f.plan.includes('utm_content'),'nonpersonal attribution');
  ok(f.plan.includes('HARD HOLD'),'commercial authorization hold');
  ok(/rectangular bounding box of more than 7,400 mm³/.test(f.priorArticle)&&/153 mm³/.test(f.priorArticle),'R193 gorilla box versus actual mean nodule volume');
  ok(/gaze dwell time/i.test(f.priorArticle),'R193 dwell rather than single fixation');
  ok(/gaze dwell time/.test(JSON.stringify(old.claim_decisions||[])),'R193 ledger dwell correction');
  const nativeDisabled=(s)=>/\sdisabled(?=\s|=|>)/i.test([...s.matchAll(/<button\b[^>]*>/gi)].map(x=>x[0]).join(' '));
  ok(nativeDisabled(f.A),'existing A natively disabled');
  ok(nativeDisabled(f.B),'existing B natively disabled');
  ok(/42.second|42s|00:42/.test(f.B),'existing B optional film length');
  ok(/<title>/.test(f.A)&&/<title>/.test(f.B),'existing guides complete titles');
  return results;
}
function mutationTests(f){
  const out=[],mutate=(name,k,fn)=>{const copy={...f,[k]:fn(f[k])};const failures=checks(copy).filter(c=>!c.pass).map(c=>c.name);out.push({name,detected:failures.length>0,failures})};
  mutate('source corruption','ledger',s=>s.replace('https://doi.org/10.1068/p090483','javascript:alert(1)'));
  mutate('missing claim reference','ledger',s=>s.replace('"source_ids": [\n        "thompson1980"','"source_ids": [\n        "unlisted_source"'));
  mutate('false publisher approval','ledger',s=>s.replace('"id": "publisher_acceptance",\n      "pass": false','"id": "publisher_acceptance",\n      "pass": true'));
  mutate('invent paid order','ledger',s=>s.replace('"paid_orders_verified": null','"paid_orders_verified": 3'));
  mutate('fake net revenue','ledger',s=>s.replace('"net_revenue_per_1000_qualified_humans": "NOT_COMPUTABLE"','"net_revenue_per_1000_qualified_humans": 20'));
  mutate('enable merchant CTA','hub',s=>s.replace('<button type="button" disabled','<button type="button"'));
  mutate('remove affiliate disclosure','hub',s=>s.replace('Final Vestige may earn a commission','Final Vestige has nothing to disclose'));
  mutate('insert second subscription','hub',s=>s.replace('</footer>','<form method="post"><input type="email"></form></footer>'));
  mutate('activate JS','hub',s=>s.replace('</footer>','<script src="https://track.example/test.js"></script></footer>'));
  mutate('insert autoplay embed','hub',s=>s.replace('</footer>','<video autoplay src="film.mp4"></video></footer>'));
  mutate('remove noindex','hub',s=>s.replace('<meta name="robots" content="noindex,nofollow">',''));
  mutate('remove focus keyboard','hub',s=>s.replace('a:focus-visible,button:focus-visible','a:hover,button:hover'));
  mutate('break actual history link','hub',s=>s.replace('/2026/11/02/mesmerism/','/2026/11/02/mesmerism-wrong/'));
  mutate('break existing Focus','hub',s=>s.replaceAll('finalvestige.com/focus/','finalvestige.com/nonexistent/'));
  mutate('erase science link','article',s=>s.replace('10.1068/p260225','incorrect-doi'));
  mutate('remove research origin','article',s=>s.replaceAll('1980','nineteenth-century'));
  mutate('corrupt R193 dwell','priorArticle',s=>s.replace('gaze dwell time','single uninterrupted fixation'));
  mutate('corrupt R193 ledger','priorLedger',s=>s.replace('gaze dwell time','single fixation'));
  mutate('remove A disabled','A',s=>s.replace(/(<button\b[^>]*?)\sdisabled(?=\s|=|>)/i,'$1'));
  mutate('remove B disabled','B',s=>s.replace(/(<button\b[^>]*?)\sdisabled(?=\s|=|>)/i,'$1'));
  mutate('replace no-money condition','plan',s=>s.replaceAll('NOT COMPUTABLE','0.00'));
  return out;
}
module.exports={files,checks,mutationTests};
if(require.main===module){
 const fs=require('node:fs');
 const f=Object.fromEntries(Object.entries(files).map(([k,p])=>[k,fs.readFileSync(p,'utf8')]));
 const actual=checks(f),mut=mutationTests(f);
 const pass=actual.filter(x=>x.pass).length,det=mut.filter(x=>x.detected).length;
 console.log(JSON.stringify({assertions_passed:pass,assertions_total:actual.length,mutations_detected:det,mutations_total:mut.length,failures:actual.filter(x=>!x.pass),undetected:mut.filter(x=>!x.detected)},null,2));
 if(pass!==actual.length||det!==mut.length)process.exitCode=1;
}
