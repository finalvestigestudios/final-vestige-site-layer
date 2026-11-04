'use strict';
/** Native reproduction: node --test mind/r117/check-r117.test.cjs . No network or paid service. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {test}=require('node:test');
const d=__dirname, root=path.resolve(d,'..','..');
const read=(p)=>fs.readFileSync(path.join(d,p),'utf8');
const article=read('the-choice-you-never-made.md');
const plan=read('one-offer-conversion-and-ux-plan.md');
const matrix=JSON.parse(read('source-claims-gates.json'));
const box=read('zen12-conditional-cta.fragment.html');
const a=fs.readFileSync(path.join(root,'mind/r114/zen12-text-A.html'),'utf8');
const b=fs.readFileSync(path.join(root,'mind/r114/zen12-film-B.html'),'utf8');
const vtt=fs.readFileSync(path.join(root,'mind/r114/film-40s.vtt'),'utf8');
const math=require('../r114/revenue-math.cjs');
test('original 1900-plus-word investigation has primary source trail',()=>{
 assert.ok(article.split(/\s+/).length>=1900);
 for(const id of ['10.1126/science.1111709','10.1371/journal.pone.0045457','23799197','23593244'])assert.ok(article.includes(id),id);
});
test('historic and experimental limitations are explicit',()=>{
 for(const v of ['69%','at least one of two','22%','70%','not a validated psychological test'])assert.ok(article.includes(v),v);
});
test('independent article is not affiliate advertorial',()=>{
 assert.ok(!/https?:\/\/(zen12|brainwaveshots|hypnosislive|affiliates.inspire3)/i.test(article));
 assert.ok(!/may earn a commission|buy now|limited-time offer/i.test(article));
});
test('article and commercial plan remain unpublished',()=>{assert.ok(article.includes('UNPUBLISHED'));assert.ok(plan.includes('UNPUBLISHED'));});
test('seller, primary-study, FTC and site proof are represented',()=>{
 for(const t of ['primary','systematic_review','seller','seller_policy','regulatory','authenticated_site'])assert.ok(matrix.source_records.some(x=>x.type===t),t);
 assert.ok(matrix.source_records.length>=18);
});
test('registered claims all have resolved source IDs',()=>{
 const keys=new Set(matrix.source_records.map(s=>s.id));
 assert.ok(matrix.claims.length>=20);
 assert.equal(new Set(matrix.claims.map(c=>c.id)).size,matrix.claims.length);
 for(const cl of matrix.claims){assert.ok(cl.proof.length);for(const p of cl.proof)assert.ok(keys.has(p),p);}
});
test('no invented offer, qualified sessions or revenue',()=>{
 for(const k of ['affiliate_approval_id','affiliate_url','approved_paid_offer','merchant_order_evidence','qualified_human_sessions','realized_net_revenue','net_revenue_per_1000_qualified_human_sessions'])assert.equal(matrix.metadata[k],null,k);
});
test('all commercial and release permissions closed',()=>{
 assert.ok(Object.values(matrix.closed_gates).length>=12);
 assert.ok(Object.values(matrix.closed_gates).every(x=>x===false));
});
test('unverified product efficacy cannot be used as independent proof',()=>{
 for(const id of ['CL08','CL10','CL17','CL24'])assert.ok(matrix.claims.find(c=>c.id===id).status.startsWith('EXCLUDE_'));
});
test('focus shot conflicting seller price kept out of checkout claim',()=>{
 assert.ok(matrix.claims.find(c=>c.id==='CL18').status.startsWith('EXCLUDE_'));
 assert.ok(plan.includes('inconsistent'));
});
test('Grok content IDs not fabricated and no fake live article',()=>{
 assert.equal(matrix.entry_route_hypotheses.length,3);
 assert.ok(matrix.entry_route_hypotheses.every(x=>x.grok_asset_id===null));
 assert.equal(matrix.entry_route_hypotheses[2].published_article,null);
});
test('prospective FTC disclosure next to disabled purchasing button',()=>{
 const i=box.lastIndexOf('commission at no additional cost');
 const j=box.indexOf('button disabled');
 assert.ok(i>0&&j>i&&j-i<350);
 assert.ok(box.includes('aria-describedby="fv-mind-r117-disclosure fv-mind-r117-blocker"'));
});
test('no script, iframe, signup form, tracking or active merchant link in fragment',()=>{
 assert.ok(!/<form\b|<script\b|<iframe\b|autoplay\s*=/i.test(box));
 assert.ok(!/<a\b[^>]+href=["']https?:\/\/(?:zen12\.com|brainwaveshots\.com)/i.test(box));
 assert.ok(box.includes('disabled type="button"'));
});
test('fragment: 48px touch, focus-visible and reduced-motion',()=>{
 for(const marker of ['min-height:48px','focus-visible','prefers-reduced-motion'])assert.ok(box.includes(marker));
});
test('existing R114 buyer guide variants preserve offline release hold',()=>{
 for(const h of [a,b]){
  assert.ok(h.includes('noindex,nofollow'));
  assert.ok(!/<iframe\b|<form\b|<script\b|autoplay\s*=/i.test(h));
  assert.ok(/<button\b[^>]*disabled/i.test(h));
 }
});
test('optional film B remains storyboard, A text-only, complete VTT',()=>{
 assert.ok(!a.includes('id="optional-film"'));
 assert.ok(b.includes('id="optional-film"'));
 assert.ok(b.includes('storyboard-only'));
 assert.ok(vtt.startsWith('WEBVTT'));
});
test('existing analytics contract rejects personal information',()=>{
 assert.ok(math.validateSafeEvent({event_name:'affiliate_outbound_click',utm_source:'youtube',utm_medium:'organic_social',utm_content_asset_id:'asset_1234'}));
 assert.equal(math.validateSafeEvent({event_name:'affiliate_outbound_click',email:'test@example.com'}),false);
});
test('existing revenue math refuses to fabricate results from click-only data',()=>{
 const r=math.confirmedRevenue({cohort_days:7,qualified_human_sessions:1000,confirmed_paid_orders:10});
 assert.equal(r.status,'NOT_COMPUTABLE');
 assert.equal(r.net_per_1000_cents,null);
});
test('business prioritization references authorized owners, cohort and hold',()=>{
 for(const s of ['7/30-day','Grok','Praxxis','Site QA','Dispatch','Jetpack','PR #49','PR #172','HARD HOLD','NOT COMPUTABLE'])assert.ok(plan.includes(s),s);
});
