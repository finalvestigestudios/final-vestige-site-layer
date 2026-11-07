'use strict';
/* R191: Pure, read-only source/activation contract tests.
   Run: node mind/r191/test_mind_r191.cjs from repository root.
   No external dependencies, no production HTTP/network writes. */
const FILES = {
 article:'mind/r191/the-face-you-didnt-choose-CHOICE-BLINDNESS-INVESTIGATION-UNPUBLISHED.md',
 ledger:'mind/r191/source-claim-merchant-authorization-gates.json',
 plan:'mind/r191/ONE-AUTHORIZED-OFFER-CREATOR-FIT-PAID-REVENUE-EXPERIMENT.md',
 hub:'mind/r191/mind-archive-four-stream-WP-DRAFT-UNPUBLISHED.html',
 A:'mind/r188/zen12-variant-A-independent-text-UNPUBLISHED.html',
 B:'mind/r188/zen12-variant-B-optional-42s-storyboard-UNPUBLISHED.html',
 r189:'mind/r189/verified-claims-merchant-permissions-revenue-gates.json',
 r190:'mind/r190/the-recording-is-not-the-experiment-SELF-HYPNOSIS-EVIDENCE-UNPUBLISHED.md'
};
function removeFilm(s) {
 return s.replace(/<section id="optional-film" class="film"[\s\S]*?<\/section>/, '');
}
function tags(s,tag){return Array.from(s.matchAll(new RegExp('<'+tag+'\\b[^>]*>', 'gi')),x=>x[0]);}
function nativeDisabled(t){return /\sdisabled(?=[\s=>])/i.test(t);}
function clean(s) {return s.replace(/\s+/g,' ');}
function check(files) {
 const checks=[]; const assert=(test,label)=>checks.push({label,pass:!!test});
 const a=files.article,l=files.ledger,p=files.plan,h=files.hub,A=files.A,B=files.B,r189=files.r189,r190=files.r190;
 let data=null; try{data=JSON.parse(l);}catch(e){}
 let prior=null;try{prior=JSON.parse(r189)}catch(e){}
 assert(a.split(/\s+/).length>1950,'research article substantive');
 assert(a.includes('Johansson')&&a.includes('Hall')&&a.includes('Sikström'),'2005 primary researchers');
 assert(a.includes('https://doi.org/10.1126/science.1111709'),'2005 DOI');
 assert(a.includes('https://pubmed.ncbi.nlm.nih.gov/20637455/'),'2010 primary');
 assert(a.includes('https://doi.org/10.1371/journal.pone.0045457'),'2012 primary');
 assert(a.includes('69%')&&a.includes('no more than one third'),'numerical studies accurately bounded');
 assert(a.includes('not an observed effect')&&a.includes('not a validated cognitive test'),'generalization limitations');
 assert(a.includes('UNPUBLISHED'),'article not represented live');
 assert(a.includes('https://finalvestige.com/focus/')&&a.includes('https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'),'existing internal link sources');
 assert(!/href=["'][^"']*(?:awin1|clickbank|hoplink)/i.test(a),'no secret earning link in article');
 assert(!/guaranteed improvements|proved Zen12 works|all shoppers are deceived/i.test(a),'article avoids ungrounded claims');
 assert(!!data&&data.milestone==='R191','new JSON register parse');
 assert(!!data&&data.source_links.length>=18,'substantial source trail');
 assert(!!data&&data.claim_decisions.length>=20,'substantial claim map');
 assert(!!data&&data.release_gates.length>=12,'commercial gates enumerated');
 const ids=new Set((data?.source_links||[]).map(x=>x.id));
 assert(!!data&&data.claim_decisions.every(x=>ids.has(x.source_id)),'every claim resolves a source');
 assert(!!data&&ids.size===data.source_links.length,'unique source identifiers');
 assert(!!data&&data.release_gates.some(x=>x.id==='publisher_named_acceptance'&&x.status==='BLOCKED'),'named affiliate approval hard blocked');
 assert(!!data&&data.release_gates.some(x=>x.id==='authorized_url'&&x.status==='BLOCKED'),'earning URL hard blocked');
 assert(!!data&&data.claim_decisions.some(x=>x.id==='zen_hour'&&x.decision.startsWith('REJECT')),'no audio equivalence guarantee');
 assert(!!data&&data.claim_decisions.some(x=>x.id==='paid_metric'&&x.decision.startsWith('NOT_COMPUTABLE')),'no invented paid KPI');
 assert(p.includes('real merchant')||p.includes('merchant reconciliation'),'merchant verification required');
 assert(p.includes('Grok owns video production')&&p.includes('Praxxis owns source QA'),'creator owner preserved');
 assert(p.includes('NOT COMPUTABLE'),'missing paid KPI acknowledged');
 assert(p.includes('settled_affiliate_commission')&&p.includes('merchant_confirmed_paid_order'),'clicks separated from sales');
 assert(p.includes('utm_content=REAL_GROK_ASSET_ID'),'no fabricated media identifier');
 assert(p.includes('7-day')&&p.includes('30-day'),'time cohorts documented');
 assert(p.includes('https://finalvestige.com/focus/'),'reuses Focus');
 assert(p.includes('No'), 'sanity text guard');
 assert(p.includes('not a sale')||p.includes('still not a sale'),'affiliate click does not imply sale');
 assert(p.includes('video')&&p.includes('A/B'),'controlled video hypothesis included');
 assert(h.includes('id="main"')&&h.includes('class="skip"'),'semantic main and keyboard skip');
 assert(h.includes('name="robots" content="noindex,nofollow"'),'prototype noindex');
 assert(tags(h,'button').length===1&&tags(h,'button').every(nativeDisabled),'all hub merchant controls natively disabled');
 assert(h.includes('id="r191-affiliate-disclosure"')&&h.includes('aria-describedby="r191-affiliate-disclosure"'),'hub adjacent disclosure associated');
 assert(h.indexOf('may earn a commission')>=0&&h.indexOf('may earn a commission')<h.indexOf('<button'),'disclosure before button');
 assert(!/<(?:script|form|iframe|video|input)\b/i.test(h),'hub no javascript, signup, embedded tracking or autoplay video');
 assert(!/href="https?:\/\/(?:zen12\.com|affiliates\.inspire3\.com|www\.awin1\.com)/i.test(h),'hub no merchant outbound links');
 assert(h.includes('prefers-reduced-motion')&&h.includes('@media(max-width:800px)'),'mobile and reduced motion styles');
 assert(h.includes('https://finalvestige.com/2026/11/02/mesmerism/'),'correct Mesmerism canonical slug');
 assert(h.includes('https://finalvestige.com/2026/11/02/change-blindness/'),'source-linked existing perception route');
 assert(h.includes('https://finalvestige.com/focus/')&&!h.includes('mailto:'),'one free published focus destination');
 assert(!h.includes('/2026/11/02/mesmerism-and-the'),'no obsolete Mesmerism slug');
 assert(tags(A,'button').length===1&&tags(A,'button').every(nativeDisabled),'A purchasing CTA native disabled');
 assert(tags(B,'button').length===1&&tags(B,'button').every(nativeDisabled),'B purchasing CTA native disabled');
 assert(A.includes('may earn')&&B.includes('may earn'),'A/B adjacent affiliate statement present');
 assert(!/<(?:script|form|iframe|video|input)\b/i.test(A+B),'A/B no new subscriber/tracker/video injection');
 assert(removeFilm(B)===A,'A/B textual and offer parity apart from optional film');
 assert(B.includes('00:35–00:42')&&B.includes('transcript'),'42s original storyboard/transcript');
 assert(prior&&prior.claim_decisions.some(x=>x.id==='field_gaze'&&x.claim.includes('same participants')),'inherited within-subject eye tracking correction');
 assert(r190.includes('may reflect differences'),'inherited review heterogeneity appropriately hedged');
 return {passed:checks.filter(c=>c.pass).length,total:checks.length,failed:checks.filter(c=>!c.pass).map(c=>c.label)};
}
function mutations(files){
 const m=[
 ['A native disabled',f=>{f.A=f.A.replace(/ class="disabled" type="button" disabled /,' class="disabled" type="button" ')}],
 ['B native disabled',f=>{f.B=f.B.replace(/ class="disabled" type="button" disabled /,' class="disabled" type="button" ')}],
 ['hub native disabled',f=>{f.hub=f.hub.replace(/<button type="button" disabled /,'<button type="button" ')}],
 ['hub disclosure removed',f=>{f.hub=f.hub.replace('may earn a commission','an unrelated service note')}],
 ['hub wrong Mesmerism route',f=>{f.hub=f.hub.replace('/2026/11/02/mesmerism/','/2026/11/02/mesmerism-and-the-mystery/')}],
 ['hub active advertiser link',f=>{f.hub=f.hub.replace('href="#buyer-review"','href="https://zen12.com/hnp"')}],
 ['hub duplicate signup form',f=>{f.hub=f.hub.replace('</main>','<form><input type="email"></form></main>')}],
 ['hub inline script',f=>{f.hub=f.hub.replace('</head>','<script>navigator.sendBeacon("/track","x")</script></head>')}],
 ['hub iframe autoplay',f=>{f.hub=f.hub.replace('</main>','<iframe src="about:blank" autoplay></iframe></main>')}],
 ['hub missing noindex',f=>{f.hub=f.hub.replace('content="noindex,nofollow"','content="index,follow"')}],
 ['A/B text parity broken',f=>{f.B=f.B.replace('Before you buy a quieter mind','Before you buy an improved mind')}],
 ['B storyboard removed',f=>{f.B=f.B.replace('00:35–00:42','no video timing')}],
 ['ledger bad source FK',f=>{f.ledger=f.ledger.replace('"source_id": "choice_2005"','"source_id": "invented_study"')}],
 ['ledger affiliate approval invented',f=>{f.ledger=f.ledger.replace('"status": "BLOCKED",\n      "owner": "Founder / Mind"','"status": "APPROVED",\n      "owner": "Founder / Mind"')}],
 ['ledger hour claim accepted',f=>{f.ledger=f.ledger.replace('"REJECT_NO_BRAND_SPECIFIC_PROOF"','"PROVEN"')}],
 ['ledger paid results invented',f=>{f.ledger=f.ledger.replace('"NOT_COMPUTABLE_UNVERIFIED_DENOMINATOR_AND_ORDERS"','"PAID_CONFIRMED"')}],
 ['plan fake Grok asset',f=>{f.plan=f.plan.replace('utm_content=REAL_GROK_ASSET_ID','utm_content=guessed_tracking_id')}],
 ['plan wrong creator owner',f=>{f.plan=f.plan.replace('Grok owns video production','Mind owns video production')}],
 ['article missing 2012 reference',f=>{f.article=f.article.replace('https://doi.org/10.1371/journal.pone.0045457','unverified-political-study')}],
 ['article promotional equivalence',f=>{f.article=f.article.replace('The protection isn\'t to stop making decisions.','Zen12 proved Zen12 works. The protection isn\'t to stop making decisions.')}],
 ['prior gaze group error',f=>{f.r189=f.r189.replace('The same participants looked ahead','Ouija group looked ahead')}],
 ['prior review unhedged',f=>{f.r190=f.r190.replace('may reflect differences','reflects differences')}]
 ];
 const failures=[];let detected=0;
 for(const [name,fn] of m){const clone={...files};fn(clone);if(Object.keys(clone).every(k=>clone[k]===files[k])){failures.push(name+' did not mutate');continue}const x=check(clone);if(x.failed.length>0)detected++;else failures.push(name+' escaped');}
 return {detected,total:m.length,failures};
}
module.exports={FILES,check,mutations};
if(typeof require!=='undefined' && typeof module!=='undefined' && require.main===module){
 const fs=require('node:fs'),path=require('node:path');
 const root=path.resolve(__dirname,'../..');
 const values=Object.fromEntries(Object.entries(FILES).map(([k,v])=>[k,fs.readFileSync(path.join(root,v),'utf8')]));
 const x=check(values),y=mutations(values);
 process.stdout.write('R191 source '+x.passed+'/'+x.total+'\n');
 process.stdout.write('R191 adversarial '+y.detected+'/'+y.total+'\n');
 if(x.failed.length||y.failures.length){process.stderr.write(JSON.stringify({failed:x.failed,mutations:y.failures},null,2)+'\n');process.exitCode=1;}
}
