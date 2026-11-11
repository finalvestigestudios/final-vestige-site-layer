'use strict';
/**
 * Reproducible source-only validator for isolated FV Mind R284.
 * Run: node mind/r284/verify_r284.cjs
 * No package dependencies, no network, no merchant/test purchases.
 * Checks static source contracts only, NOT browser a11y/CWV, WordPress sanitization,
 * merchant authorization, genuine newsletter opt-in, or settled paid conversion.
 */
const fs=require('node:fs'); const path=require('node:path'); const assert=require('node:assert/strict');
const dir=__dirname;
const names={
 article:'THE-SOUND-THAT-PROMISED-HOURS-OF-FOCUS-UNPUBLISHED.md',
 matrix:'OFFER-CLAIM-SOURCE-AND-REVENUE-GATES.json',
 a:'ZEN12-BUYER-GUIDE-A-TEXT-ONLY-UNPUBLISHED.html',
 b:'ZEN12-BUYER-GUIDE-B-FILM-STORYBOARD-UNPUBLISHED.html',
 hub:'MIND-CANONICAL-HUB-INSERT-CANDIDATE-UNPUBLISHED.html',
 plan:'CONVERSION-ACCEPTANCE-AB-CREATOR-HANDOFF.md'
};
function read(){return Object.fromEntries(Object.entries(names).map(([k,v])=>[k,fs.readFileSync(path.join(dir,v),'utf8')]));}
const badTags=/<\s*(?:script|iframe|form|video|audio|object|embed)\b/i;
const forbiddenAttrs=/\b(?:onload|onclick|onerror|onmouseover|formaction)\s*=|\b(?:src|href)\s*=\s*["']?\s*javascript:/i;
const externalPaidHref=/href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com|payhip\.com)\b/i;
function assertAll(d){
 const m=JSON.parse(d.matrix);
 assert.equal(m.revision,'r284');
 assert.equal(m.status,'DRAFT_UNPUBLISHED_COMMERCIAL_HARD_HOLD');
 assert.equal(m.verified_account_permission,false);
 assert.equal(m.external_affiliate_urls_active,false);
 assert.equal(m.commercial_gates.length,16);
 assert.equal(new Set(m.commercial_gates.map(g=>g.id)).size,16);
 for(const g of m.commercial_gates) assert.equal(g.state,'HARD_HOLD','all commercial authorization gates fail closed');
 assert.ok(m.source_register.length>=16,'source bibliography');
 assert.ok(m.claims.length>=24,'classified claims');
 assert.ok(m.offer_candidates.length>=5);
 assert.ok(m.offer_candidates.every(x=>x.id==='focus_fieldbook'?x.commercial_state==='FREE_LEAD_NOT_SALE':x.commercial_state==='HARD_HOLD'),'all proposed paid offers stay hard-held');
 assert.ok(m.creator_routes.length===3);
 assert.ok(m.creator_routes.every(x=>x.grok_media_id===null),'no invented internal IDs');
 assert.ok(m.claims.some(x=>x.id==='brainwave_refund_cap'&&x.decision==='MUST_DISCLOSE_IF_COMPARING'));
 assert.ok(m.claims.some(x=>x.id==='brainwave_precautions'&&x.decision==='MUST_DISCLOSE'));
 assert.ok(m.claims.some(x=>x.id==='zen12_equivalence'&&x.decision==='EXCLUDE_AS_FACT'));
 assert.ok(m.claims.some(x=>x.id==='affiliate_acceptance'&&x.decision==='HARD_HOLD'));
 assert.ok(m.events.affiliate_click.includes('not sale'));
 assert.ok(m.events.net_revenue_per_1000.includes('NULL'));
 assert.ok(d.article.split(/\s+/).length>=2100,'substantial independent evidence manuscript');
 for(const phrase of ['five reported','eight','one yielded mixed','one refund within any six-month','five refunded sessions',"the seller's newsletter",'No affiliate link is active','not a clinical trial']){
  assert.ok(d.article.toLowerCase().includes(phrase.toLowerCase()),'article required evidence: '+phrase);
 }
 for(const phrase of ['https://pubmed.ncbi.nlm.nih.gov/37205669/','https://brainwaveshots.com/faq','https://zen12.com/hnp','https://hypnosislive.com/faq','https://www.ftc.gov/']){
  assert.ok(d.article.includes(phrase),'article source '+phrase);
 }
 for(const k of ['a','b']){
  const h=d[k];
  assert.ok(/<html\s+lang="en"/i.test(h),'language');
  assert.ok(/<meta\s+name="viewport"/i.test(h),'responsive');
  assert.ok(/<main\s+id="main"/i.test(h),'main landmark');
  assert.ok(/href="#main"/i.test(h),'skip link');
  assert.ok(/:focus-visible/.test(h),'focus outline');
  assert.ok(/prefers-reduced-motion/.test(h),'reduced-motion');
  assert.ok(/<button\s+type="button"\s+disabled\s+aria-describedby="prospective-disclosure"/.test(h),'paid CTA disabled');
  assert.ok(/id="prospective-disclosure"/.test(h),'near-link disclosure id');
  assert.ok(/may earn a commission at no additional cost to you/i.test(h),'clear prospective disclosure');
  assert.ok(/authorization pending/i.test(h),'no authorized offer');
  assert.ok(/https:\/\/finalvestige\.com\/focus\//.test(h),'one existing FV Focus funnel');
  assert.ok(/seller's newsletter/i.test(h),'merchant vs FV consent');
  assert.ok(/not a playable video or a live user test|not an MP4|no video file/i.test(h)||k==='a','not falsely depicting film as built');
  assert.ok(!badTags.test(h),'no media/script/embedded forms');
  assert.ok(!forbiddenAttrs.test(h),'no inline JS or JS scheme');
  assert.ok(!externalPaidHref.test(h),'no premature merchant navigation');
  assert.ok(!/\b(?:gtag|fbq|dataLayer|pixel_id|shopify|onetrust)\s*\(/i.test(h),'no extra trackers');
 }
 assert.ok(!d.a.includes('class="film"'),'text A no visual');
 assert.ok(d.b.includes('class="film"'),'B only includes optional storyboard');
 assert.ok(d.b.includes('Storyboard only — no playable video yet'),'no false hosted film');
 const markers=['00:00–00:06','00:06–00:12','00:12–00:18','00:18–00:24','00:24–00:30','00:30–00:36','00:36–00:42'];
 assert.equal((d.b.match(/<time>/g)||[]).length,7,'film seven segments');
 for(const t of markers) assert.ok(d.b.includes(t),'timecode '+t);
 function normalize(h){return h.replace(/<aside class="film"[\s\S]*?<\/aside>/,'').replace(/Variant B \/ optional film concept/g,'Variant A / text only');}
 assert.equal(normalize(d.b),normalize(d.a),'A and B copy and purchasing contract identical except optional visual');
 assert.ok(!badTags.test(d.hub));
 assert.ok(!externalPaidHref.test(d.hub));
 assert.ok(!forbiddenAttrs.test(d.hub));
 assert.ok(/UNPUBLISHED/.test(d.hub));
 assert.ok(/not yet a public URL/.test(d.hub),'no unapproved new public guide');
 assert.ok(/existing.*Dispatch/i.test(d.hub),'single lead funnel');
 for(const phrase of ['one refund within any six-month','five refunded sessions','NOT COMPUTABLE','No new pixels','NO VERIFIED MATCH']){
  assert.ok(d.plan.toLowerCase().includes(phrase.toLowerCase()),'plan '+phrase);
 }
}
const fixture=read();
assertAll(fixture);
let rejected=0;
const attempts=[
 ['matrix',s=>s.replace('"verified_account_permission": false','"verified_account_permission": true')],
 ['matrix',s=>s.replace('"external_affiliate_urls_active": false','"external_affiliate_urls_active": true')],
 ['matrix',s=>s.replace('"state": "HARD_HOLD"','"state": "APPROVED"')],
 ['matrix',s=>s.replace('"grok_media_id": null','"grok_media_id": "invented_asset_999"')],
 ['matrix',s=>s.replace('"affiliate_click": "outbound intent only; not sale"','"affiliate_click": "verified sale"')],
 ['matrix',s=>s.replace('NULL when either verified input unavailable','0 whenever evidence unavailable')],
 ['matrix',s=>s.replace('EXCLUDE_AS_FACT','PROVEN')],
 ['matrix',s=>s.replace('MUST_DISCLOSE_IF_COMPARING','OPTIONAL')],
 ['matrix',s=>s.replace('MUST_DISCLOSE','OPTIONAL')],
 ['matrix',s=>s.replace('"HARD_HOLD"','"ACTIVE"')],
 ['article',s=>s.replace('Five reported','all fourteen studies')],
 ['article',s=>s.replace('eight reported','none reported')],
 ['article',s=>s.replace('one yielded mixed','none yielded mixed')],
 ['article',s=>s.replace('one refund within any six-month','unlimited refunds')],
 ['article',s=>s.replace('five refunded sessions','unlimited refunded sessions')],
 ['article',s=>s.replace("the seller's newsletter",'Final Vestige newsletter')],
 ['article',s=>s.replace('No affiliate link is active','Affiliate link is active')],
 ['article',s=>s.replace('not a clinical trial','a clinical trial')],
 ['article',s=>s.replace('https://brainwaveshots.com/faq','https://wrong-site.invalid/refund')],
 ['a',s=>s.replace(' disabled aria-describedby',' aria-describedby')],
 ['b',s=>s.replace(' disabled aria-describedby',' aria-describedby')],
 ['a',s=>s.replace('may earn a commission at no additional cost to you','affiliate link')],
 ['b',s=>s.replace('may earn a commission at no additional cost to you','affiliate link')],
 ['a',s=>s.replace('href="https://finalvestige.com/focus/"','href="https://zen12.com/secret/"')],
 ['b',s=>s.replace('href="https://finalvestige.com/focus/"','href="https://brainwaveshots.com/focus-shot"')],
 ['a',s=>s.replace('</main>','<script src="https://track.invalid/pixel.js"></script></main>')],
 ['b',s=>s.replace('</main>','<iframe src="https://seller.invalid"></iframe></main>')],
 ['hub',s=>s.replace('</section>','<form action="/newlist"></form></section>')],
 ['a',s=>s.replace('</main>','<a onclick="buy()">buy</a></main>')],
 ['b',s=>s.replace('</main>','<img src="x" onerror="fetch(1)"></main>')],
 ['a',s=>s.replace('seller\'s newsletter','Final Vestige newsletter')],
 ['b',s=>s.replace('seller\'s newsletter','Final Vestige newsletter')],
 ['a',s=>s.replace('https://finalvestige.com/focus/','https://zen12.com/hnp')],
 ['b',s=>s.replace('https://finalvestige.com/focus/','https://zen12.com/hnp')],
 ['b',s=>s.replace('00:36–00:42','00:36–00:49')],
 ['b',s=>s.replace('<time>00:00–00:06</time>','<p>00:00–00:06</p>')],
 ['b',s=>s.replace('Storyboard only — no playable video yet','Video now LIVE!')],
 ['hub',s=>s.replace('not yet a public URL','now live at /mind/')],
 ['plan',s=>s.replace('NOT COMPUTABLE','ZERO REVENUE')],
 ['plan',s=>s.replace('NO VERIFIED MATCH','VERIFIED MATCH')],
 ['plan',s=>s.replace('one refund within any six-month','unlimited')],
 ['plan',s=>s.replace('five refunded sessions','unlimited sessions')],
 ['a',s=>s.replace(':focus-visible',':focus-within')],
 ['b',s=>s.replace('prefers-reduced-motion','prefers-constant-motion')],
 ['matrix',s=>s.replace('"commercial_gates": [','"commercial_gates": [] , "deleted_gates": [')]
];
for(const [target,mutate] of attempts){
 const altered=mutate(fixture[target]);
 assert.notEqual(altered,fixture[target],'mutation fixture must actually change source: '+target);
 try{assertAll({...fixture,[target]:altered});}catch(e){rejected++;continue;}
 throw new Error('Unsafe mutation slipped past validator: '+target+' '+altered.slice(0,80));
}
console.log('R284 BASELINE PASS; '+rejected+'/'+attempts.length+' unsafe mutations rejected; 16/16 gates HARD HOLD; A/B buyer copy parity PASS; commercial links inactive. SOURCE ONLY; real-browser/merchant/CI untested.');
