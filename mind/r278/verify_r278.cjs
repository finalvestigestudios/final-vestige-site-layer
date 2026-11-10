'use strict';
/* Final Vestige Mind R278 — reproducible offline source-contract verification.
 Run at repository root: node mind/r278/verify_r278.cjs
 Reads local files only; no network calls, tracking, signups or paid services.
 Negative cases are deliberate mutations; no production deployment.
*/
const fs = require('node:fs');
const path = require('node:path');
const root = __dirname;
const get = name => fs.readFileSync(path.join(root,name),'utf8');
const names = {
  article:'THE-SONG-THAT-PLAYED-WITHOUT-A-SPEAKER-UNPUBLISHED.md',
  matrix:'EARWORM-PRODUCT-SCIENCE-CLAIMS-AND-REVENUE-GATES.json',
  A:'ZEN12-EARWORM-BUYER-PILOT-A-UNPUBLISHED.html',
  B:'ZEN12-EARWORM-BUYER-PILOT-B-UNPUBLISHED.html',
  plan:'CONVERSION-AND-RELEASE-ACCEPTANCE.md'
};
function assert(check, name){if(!check)throw Error('R278 FAIL: '+name);}
const gateIds=['publisher_identity_verified','named_inspire3_acceptance','signed_partner_terms','approved_promotion_channels','issued_account_tracking_url','offer_slug_exact','final_checkout_total_verified','tax_fees_terms_verified','refund_policy_offer_specific_verified','customer_delivery_tested','claims_substantiated_or_excluded','ftc_near_cta_disclosure','no_merchant_newsletter_consent_transfer','privacy_no_pii_transfer','founder_release_approval','merchant_commission_settlement_evidence'];
function validate(b){
const {article,A,B,plan}=b,m=JSON.parse(b.matrix);
assert(m.schema==='fv_mind_r278_claims_consent_revenue_v1'&&m.status==='UNPUBLISHED_SOURCE_CONTROLLED_DRAFT'&&m.commercial==='HARD_HOLD','matrix identity/release hold');
assert(m.sources.length>=20 && new Set(m.sources.map(s=>s.id)).size===m.sources.length,'source ledger identities');
assert(m.sources.every(s=>/^https:\/\//.test(s.url)&&s.notes),'valid source URLs and annotations');
assert(m.claims.length>=30 && m.claims.every(c=>c.id&&c.statement&&Array.isArray(c.source_ids)&&c.assessment),'classified claims complete');
assert(new Set(m.claims.map(c=>c.id)).size===m.claims.length,'unique claims');
for(const id of ['C04','C06','C08','C10','C12','C13','C16','C18','C20','C21','C22','C24','C25','C28','C29','C30','C31','C32']){
  const x=m.claims.find(c=>c.id===id);
  assert(x && /unsubstantiated|unsupported|unverified|false/.test(x.assessment)&&x.editorial_use==='exclude','unsafe claim '+id+' must stay excluded');
}
assert(m.commercial_gates.length===16&&new Set(m.commercial_gates.map(g=>g.id)).size===16&&gateIds.every(g=>m.commercial_gates.find(x=>x.id===g)),'exact gate identity');
assert(m.commercial_gates.every(g=>g.status==='HARD_HOLD'&&g.verified===false&&g.approval_evidence===null),'no fabricated authorization');
assert(m.offers.length===6&&m.offers.every(o=>o.commercial_authorized===false && o.pricing_checkout_verified===false),'all offers appropriately inactive');
assert(m.consumer_consent.length===4&&m.consumer_consent.find(x=>x.id==='zen12_freeaudio').merchant_newsletter===true&&m.consumer_consent.find(x=>x.id==='fv_focus').merchant_newsletter===false,'separate consent boundaries');
assert(Object.values(m.release_guards).every(x=>x===false),'all releases and events disabled');
assert(m.revenue.label==='NOT_COMPUTABLE_NOT_ZERO'&&m.revenue.qualified_human_sessions===null && m.revenue.verified_paid_orders===null&&m.revenue.cleared_commissions===null&&m.revenue.realized_net_revenue===null&&m.revenue.net_revenue_per_1000_qualified_sessions===null,'unknown metrics NOT zero');
assert(m.creator_to_product_fit.length===3 && m.creator_to_product_fit.every(t=>t.actual_grok_asset_id===null),'no invented Grok IDs');
assert(article.split(/\s+/).length>=2000 && /earworm/i.test(article)&&/NOT a|not a|not an/i.test(article),'substantial original editorial');
for(const url of ['doi.org/10.3758/s13423-020-01750-7','doi.org/10.1037/aca0000090','doi.org/10.1177/0305735613511506','doi.org/10.1525/mp.2025.2330968','pubmed.ncbi.nlm.nih.gov/40031136','finalvestige.com/focus/','finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'])
assert(article.includes(url),'source/reference missing '+url);
for (const [variant,html] of [['A',A],['B',B]]){
  assert(/<html lang="en">/.test(html)&&/name="viewport"/.test(html)&&/name="robots" content="noindex,nofollow"/.test(html),'document identity '+variant);
  assert(!/<(?:script|iframe|form|video|audio)\b/i.test(html),'no scripts/media/form '+variant);
  assert(!/\b(?:autoplay|autofocus|onload|onclick|onerror)\s*=/i.test(html),'no forced behaviour '+variant);
  assert(!/\b(?:src|srcset|action)\s*=\s*["']https?:/i.test(html),'no external active fetch '+variant);
  assert(!/<(?:link|img|source)\s/i.test(html),'no external media dependencies '+variant);
  assert((html.match(/<button\b/g)||[]).length===1 && /<button\s+type="button"\s+disabled\s+aria-disabled="true">/.test(html),'held only CTA '+variant);
  const commerce=html.split('<section aria-labelledby="commerce">')[1]?.split('</section>')[0]||'';
  assert(commerce.includes('may receive a commission')&&commerce.includes('No affiliate earning link')&&commerce.indexOf('may receive a commission')>commerce.indexOf('<button')&&commerce.indexOf('may receive a commission')<commerce.indexOf('</div>'),'adjacent FTC disclosure '+variant);
  assert(html.includes('seller\'s own newsletter')&&html.includes('existing Dispatch')&&html.includes('no-account')===false /* no extra form */,'seller / FV consent distinctions '+variant);
  assert(html.includes('zen12.com/hnp') && html.includes('zen12.com/secret/') && html.includes('hypnosislive.com/mental-skills/total-focus'),'exact public seller offers '+variant);
  assert(html.includes('No Final Vestige-specific partner acceptance') && html.includes('not a clinical promise'),'no implicit seller auth or cure '+variant);
}
assert(!A.includes('id="optional-film"')&&B.includes('id="optional-film"'),'film only B');
const film=B.split('<section id="optional-film"')[1]?.split('</section>')[0]||'';
assert(/STATIC POSTER/.test(film)&&/No hosted video/.test(film)&&!/<(?:video|iframe)\b/.test(film),'honest poster, no video');
for(let i=0;i<7;i++){const a=String(i*6).padStart(2,'0'),z=String((i+1)*6).padStart(2,'0');assert(film.includes('00:'+a+'–00:'+z),'caption interval '+i);}
const commercial = h => h.split('<section aria-labelledby="commerce">')[1]?.split('</section>')[0];
assert(commercial(A)===commercial(B),'identical commercial decisions, A and B');
for(const x of ['HARD HOLD','affiliate_outbound_click','merchant_confirmed_paid_order','refunds','360','390','768','1440','no-JS'])assert(plan.includes(x),'plan missing '+x);
return true;
}
function load(){return {article:get(names.article),matrix:get(names.matrix),A:get(names.A),B:get(names.B),plan:get(names.plan)};}
function clone(b){return JSON.parse(JSON.stringify(b));}
function run(){
const base=load();validate(base);
const changes=[
 ['unlock button',b=>b.A=b.A.replace('type="button" disabled','type="button"')],
 ['remove disclosure',b=>b.A=b.A.replace(/If you purchase through a future authorized earning link,[^<]+/,'')],
 ['fake offer auth',b=>{const m=JSON.parse(b.matrix);m.commercial_gates[1].verified=true;b.matrix=JSON.stringify(m);} ],
 ['fake cleared gate',b=>{const m=JSON.parse(b.matrix);m.commercial_gates[1].status='PASS';b.matrix=JSON.stringify(m);} ],
 ['drop gate',b=>{const m=JSON.parse(b.matrix);m.commercial_gates.pop();b.matrix=JSON.stringify(m);} ],
 ['duplicate gate',b=>{const m=JSON.parse(b.matrix);m.commercial_gates[1].id=m.commercial_gates[0].id;b.matrix=JSON.stringify(m);} ],
 ['fake net',b=>{const m=JSON.parse(b.matrix);m.revenue.realized_net_revenue=100;b.matrix=JSON.stringify(m);} ],
 ['fake commission',b=>{const m=JSON.parse(b.matrix);m.revenue.cleared_commissions=10;b.matrix=JSON.stringify(m);} ],
 ['fake creator ID',b=>{const m=JSON.parse(b.matrix);m.creator_to_product_fit[0].actual_grok_asset_id='invented';b.matrix=JSON.stringify(m);} ],
 ['fake eligibility',b=>{const m=JSON.parse(b.matrix);m.offers[0].commercial_authorized=true;b.matrix=JSON.stringify(m);} ],
 ['fake price',b=>{const m=JSON.parse(b.matrix);m.offers[0].pricing_checkout_verified=true;b.matrix=JSON.stringify(m);} ],
 ['merchant consent transfer',b=>{const m=JSON.parse(b.matrix);m.consumer_consent[1].merchant_newsletter=true;b.matrix=JSON.stringify(m);} ],
 ['unexclude health claim',b=>{const m=JSON.parse(b.matrix);m.claims.find(c=>c.id==='C20').assessment='independent_supported';b.matrix=JSON.stringify(m);} ],
 ['external script',b=>b.B=b.B.replace('</body>','<script src="https://vendor.example/tracker.js"></script></body>')],
 ['external pixel',b=>b.A=b.A.replace('</body>','<img src="https://vendor.example/pixel"></body>')],
 ['new signup form',b=>b.A=b.A.replace('</body>','<form action="/signup"><input name="email"></form></body>')],
 ['host autoplay',b=>b.B=b.B.replace('</body>','<video autoplay src="/media.mp4"></video></body>')],
 ['remote CSS',b=>b.A=b.A.replace('</body>','<link rel="stylesheet" href="https://remote.example/x.css"></body>')],
 ['caption drift',b=>b.B=b.B.replace('00:36–00:42','00:40–00:42')],
 ['film in A',b=>b.A=b.A.replace('</main>','<section id="optional-film"></section></main>')],
 ['commercial variant changed',b=>b.B=b.B.replace('possible <em>format fit</em>','guaranteed <em>treatment</em>')],
 ['unchecked provenance',b=>b.article=b.article.replace('doi.org/10.1525/mp.2025.2330968','example.invalid/no-source')],
 ['fake paid status',b=>{const m=JSON.parse(b.matrix);m.release_guards.merchant_link_live=true;b.matrix=JSON.stringify(m);} ],
 ['fake subscribed',b=>{const m=JSON.parse(b.matrix);m.release_guards.email_sent=true;b.matrix=JSON.stringify(m);} ],
 ['missing product source',b=>b.A=b.A.replace('zen12.com/hnp','seller.example/not-exact')],
 ['claims prematurely approved',b=>{const m=JSON.parse(b.matrix);m.claims.find(c=>c.id==='C28').editorial_use='qualified editorial';b.matrix=JSON.stringify(m);} ],
 ['new tracking iframe',b=>b.B=b.B.replace('</body>','<iframe src="https://vendor.example"></iframe></body>')],
 ['missing mobile QA plan',b=>b.plan=b.plan.replace('390','not-measured')]
];
let rejected=0;
for(const [name,mutate] of changes){const b=clone(base);mutate(b);try{validate(b);}catch(e){rejected++;continue;}throw Error('Unsafe mutation accepted: '+name);}
return {baseline:'PASS',rejected,total:changes.length,source_files:Object.keys(names).length};
}
if(require.main===module){const result=run();process.stdout.write(JSON.stringify(result)+'\n');}
module.exports={validate,run,load};
