'use strict';
/*
 * FV Mind R286 source-only commercial/editorial validator.
 * Run from a full checkout: node mind/r286/verify_r286.cjs
 * Does not load external modules, contact network, alter site, or execute HTML.
 * It is NOT a replacement for browser WCAG, WP sanitization, merchant/cart,
 * account acceptance, payout or paid order confirmation.
 */
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const dir=__dirname;
const names={
article:'THE-SMALL-EFFECT-BEHIND-A-BIG-MEDITATION-PROMISE-UNPUBLISHED.md',
matrix:'NEW-SCIENCE-CLAIM-PROOF-AND-EIGHTEEN-COMMERCIAL-GATES.json',
hub:'CANONICAL-MIND-HUB-NEW-EVIDENCE-INSERT-UNPUBLISHED.html',
a:'../r284/ZEN12-BUYER-GUIDE-A-TEXT-ONLY-UNPUBLISHED.html',
b:'../r284/ZEN12-BUYER-GUIDE-B-FILM-STORYBOARD-UNPUBLISHED.html'
};
const gateIds='merchant_account_acceptance merchant_identity_matches_fv affiliate_terms_current permitted_traffic_channels approved_presell_placement issued_earning_url test_tracking_accepted offer_route_exact checkout_price_and_charges returns_eligibility_restrictions seller_creative_rights original_video_media_rights product_specific_claims_review adjacent_disclosure_qa browser_mobile_accessibility conversion_reporting_access founder_live_release_approval founder_commercial_activation_approval'.split(' ');
const sourceIds='meta_2026 meta_program_2024 eeg_review_2023 zen12_standard zen12_promotion zen12_free hl_product hl_faq bw_product bw_faq inspire3 partner_public ftc_disclosure ftc_health fv_focus fv_change fv_mesmer fv_puy fv_journal fv_collection yt_topic'.split(' ');
const offerIds='zen12_standard zen12_promotion hypnosis_total_focus brainwave_focus_shot fv_free_focus fv_owned_paid_mind'.split(' ');
const topics='change_blindness mesmerism_puysegur brief_mindfulness_2026'.split(' ');
function reads(){return Object.fromEntries(Object.entries(names).map(([k,v])=>[k,fs.readFileSync(path.join(dir,v),'utf8')]));}
function sameIds(actual,expected,label){assert.equal(actual.length,expected.length,label+' number');assert.deepEqual([...new Set(actual)].sort(),expected.slice().sort(),label+' exact IDs');}
function safeHtml(s,label){
 assert.ok(s.length>4000,label+' content absent');
 assert.ok(!/<(?:script|iframe|form|input|video|audio|object|embed|link|base|meta[\s>])/i.test(s) || label!=='hub',label+' injection'); // Hub fragment only.
 assert.ok(!/<(?:script|iframe|form|input|video|audio|object|embed|link|base)\b/i.test(s),label+' active/unsafe HTML');
 assert.ok(!/\son[a-z]+\s*=/i.test(s),label+' inline handler');
 assert.ok(!/\b(?:javascript|data|vbscript)\s*:/i.test(s),label+' unsafe scheme');
 assert.ok(!/@import\b|url\s*\(|expression\s*\(/i.test(s.replace(/https?:\/\/[^\s"'<>]+/g,'')),label+' CSS external resources');
 assert.ok(!/<a\b[^>]*\bhref\s*=\s*["']?\s*(?:https?:\/\/)?(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com|brainwaveshots\.com|hypnosislive\.com)/i.test(s),label+' unauthorized merchant anchor');
 assert.ok(/<button\b[^>]*\sdisabled\b/i.test(s),label+' affiliate control enabled');
 assert.ok(s.includes('Prospective affiliate disclosure:'),label+' missing adjacent disclosure');
 assert.ok(s.includes('https://finalvestige.com/focus/'),label+' free alternative removed');
 assert.ok(!/no active affiliate link[^\n]*https:\/\/zen12\.com/i.test(s),label+' contradictory active link');
}
function audit(s){
 for(const k of Object.keys(names))assert.equal(typeof s[k],'string',k+' file unreadable');
 const m=JSON.parse(s.matrix);
 assert.equal(m.version,'R286');assert.equal(m.commercial,'HARD_HOLD');assert.equal(m.publication,'UNPUBLISHED');
 assert.equal(m.parent_frozen_r285_sha,'1606906f75dd25b23c707f7db03f040be0205e3f');
 sameIds(m.source_registry.map(x=>x.id),sourceIds,'sources');
 for(const x of m.source_registry){assert.ok(/^https:\/\//.test(x.url),x.id+' invalid source');}
 sameIds(m.claims.map(x=>x.id),Array.from({length:22},(_,i)=>'R286-'+String(i+1).padStart(2,'0')),'claims');
 const src=new Set(sourceIds);
 for(const c of m.claims){assert.ok(src.has(c.source_id),c.id+' orphaned evidence');assert.ok(c.decision && c.limit && c.statement,c.id+' unsupported classification');}
 const mandatory={'R286-02':'ALLOW_WITH_SMALL_EFFECT_CONTEXT','R286-05':'MUST_DISCLOSE_WHEN_CITING','R286-08':'EXCLUDE_AS_FACT','R286-12':'MUST_DISCLOSE_IF_COMPARING','R286-14':'MUST_DISCLOSE_IF_COMPARING','R286-15':'MUST_ATTRIBUTE_SELLER','R286-17':'EXCLUDE_AS_FACT','R286-19':'REQUIRE_NEAR_CTA','R286-20':'REQUIRE_PRODUCT_SPECIFIC_PROOF','R286-22':'EXCLUDE_AS_FACT'};
 for(const [id,decision] of Object.entries(mandatory))assert.equal(m.claims.find(c=>c.id===id)?.decision,decision,id+' required policy');
 sameIds(m.offers.map(x=>x.id),offerIds,'offer identity');
 for(const o of m.offers){assert.ok(src.has(o.source_id),o.id+' missing source');assert.equal(o.issued_link,null,o.id+' active link');assert.equal(o.verified_merchant_paid_order,null,o.id+' fabricated sale');assert.equal(o.authorization,o.id==='fv_free_focus'?'FREE_NOT_SALE':'HARD_HOLD',o.id+' unauthorized');}
 sameIds(m.commercial_gates.map(x=>x.id),gateIds,'commercial gates');
 for(const g of m.commercial_gates){assert.equal(g.state,'HARD_HOLD',g.id+' unauthorized');assert.equal(g.proof,null,g.id+' invented proof');assert.equal(g.approval_reference,null,g.id+' invented approval');}
 sameIds(m.creator_topic_to_offer_fit.map(x=>x.topic),topics,'creator routes');
 for(const r of m.creator_topic_to_offer_fit){assert.equal(r.grok_internal_asset_id,null,r.topic+' invented Grok ID');assert.ok(offerIds.includes(r.optional_future_offer),r.topic+' invalid product');assert.ok(r.status && !/VERIFIED_ATTRIBUTED/.test(r.status),r.topic+' false attribution');}
 assert.equal(m.authorization_summary.partner_approval,'NOT_AUTHENTICATED');
 assert.equal(m.authorization_summary.issued_earning_url,null);
 assert.equal(m.authorization_summary.settled_commission_report,null);
 assert.equal(m.canonical_offer_test.state,'UNPUBLISHED_HOLD');
 assert.equal(m.canonical_offer_test.buyer_link,null);
 assert.equal(m.canonical_offer_test.variant_b.includes('NOT playable'),true);
 assert.equal(m.measurement_contract.net_revenue_per_1000,null);
 assert.equal(m.measurement_contract.denominator_state,'NOT_VERIFIED');
 assert.equal(m.measurement_contract.missing_value_rule,'NULL_NOT_COMPUTABLE_NOT_ZERO');
 assert.deepEqual(m.measurement_contract.cohorts_days,[7,30]);
 for(const [flag,val] of Object.entries(m.branch_governance))assert.equal(val,false,'governance: '+flag);
 const a=s.article;
 for(const phrase of ['6 November 2026','66 studies','187 effect sizes','2,503','2,511','g = 0.09','0.03 to 0.16','very limited','excludes one-session','twelve-minute','Puységur'])assert.ok(a.toLowerCase().includes(phrase.toLowerCase()),'article science miss: '+phrase);
 for(const key of ['meta_2026','meta_program_2024','eeg_review_2023'])assert.ok(a.includes(m.source_registry.find(x=>x.id===key).url),key+' missing from article');
 assert.ok(!/affiliate.*(approved|activated)/i.test(a), 'article may not claim an affiliate approval');
 safeHtml(s.hub,'hub');safeHtml(s.a,'a');safeHtml(s.b,'b');
 assert.ok(s.hub.includes('id="mind-r286-heading"') && s.hub.includes('g = 0.09'),'new hub has wrong study');
 assert.ok(s.hub.includes('aria-describedby="fv-r286-disclosure"'),'hub disclosure not connected to disabled control');
 assert.ok(s.hub.indexOf('id="fv-r286-disclosure"')<s.hub.indexOf('Zen12 purchase link unavailable'),'hub disclosure must precede button');
 for(const [k,t] of [['a',s.a],['b',s.b]]){
  assert.ok(/no more than five refunded sessions/i.test(t),k+' Hypnosis Live refund incomplete');
  assert.ok(/one refund within any six-month period/i.test(t),k+' Brainwave refund frequency incomplete');
  assert.ok(/orders exceeding ten items/i.test(t),k+' Brainwave large-order restriction incomplete');
  assert.ok(/epilepsy/i.test(t),k+' seller caution incomplete');
  assert.ok(/<button\b[^>]*disabled/i.test(t),k+' merchant purchase not disabled');
  assert.ok(t.includes('id="prospective-disclosure"'),k+' missing proximity text');
 }
 assert.ok(s.b.includes('Static dark-gradient text poster'),'B poster does not accurately describe visible poster');
 assert.ok(s.b.includes('Storyboard only — no playable video yet'),'B invents hosted media');
 for(let i=0;i<7;i++)assert.ok(s.b.includes('00:'+String(i*6).padStart(2,'0')+'–00:'+String((i+1)*6).padStart(2,'0')), 'B script timestamp '+i);
 return true;
}
function run(){
 const base=reads();audit(base);
 const mutants=[];
 const mutant=(name,fn)=>mutants.push({name,fn});
 for(let i=0;i<gateIds.length;i++)mutant('gate'+i,s=>{const m=JSON.parse(s.matrix);m.commercial_gates[i].state='APPROVED';s.matrix=JSON.stringify(m);});
 mutant('gate ID substitution',s=>{let m=JSON.parse(s.matrix);m.commercial_gates[0].id='new_unknown_gate';s.matrix=JSON.stringify(m);});
 mutant('fake provenance',s=>{let m=JSON.parse(s.matrix);m.claims[0].source_id='fabricated';s.matrix=JSON.stringify(m);});
 mutant('fake science',s=>{let m=JSON.parse(s.matrix);m.claims.find(x=>x.id==='R286-02').decision='GUARANTEED';s.matrix=JSON.stringify(m);});
 mutant('unverified approved offer',s=>{let m=JSON.parse(s.matrix);m.offers[0].authorization='APPROVED';s.matrix=JSON.stringify(m);});
 mutant('merchant payout invented',s=>{let m=JSON.parse(s.matrix);m.authorization_summary.settled_commission_report=99;s.matrix=JSON.stringify(m);});
 mutant('net revenue invented',s=>{let m=JSON.parse(s.matrix);m.measurement_contract.net_revenue_per_1000=0;s.matrix=JSON.stringify(m);});
 mutant('fake Grok ID',s=>{let m=JSON.parse(s.matrix);m.creator_topic_to_offer_fit[0].grok_internal_asset_id='unverified123';s.matrix=JSON.stringify(m);});
 mutant('link approved',s=>{let m=JSON.parse(s.matrix);m.offers[0].issued_link='https://zen12.com/?ref=madeup';s.matrix=JSON.stringify(m);});
 mutant('enabled commerce hub',s=>{s.hub=s.hub.replace(/disabled aria-describedby/,'aria-describedby');});
 mutant('hub disclosure missing',s=>{s.hub=s.hub.replace(/Prospective affiliate disclosure:/,'Disclaimer omitted:');});
 mutant('hub merchant href',s=>{s.hub+= '<a href="https://zen12.com/">shop now</a>';});
 mutant('hub new form',s=>{s.hub+='<form><input></form>';});
 mutant('hub script',s=>{s.hub+='<script>alert(1)</script>';});
 mutant('hub external CSS resource',s=>{s.hub=s.hub.replace('color:var(--m-soft);','background:url(https://example.org/track);color:var(--m-soft);');});
 mutant('buyer A extra merchant link',s=>{s.a+='<a href="https://zen12.com/hnp">Buy</a>';});
 mutant('buyer B extra merchant link',s=>{s.b+='<a href="https://hypnosislive.com/faq">Buy</a>';});
 mutant('buyer both unapproved',s=>{s.a+='<a href="https://zen12.com/hnp">Buy</a>';s.b+='<a href="https://zen12.com/hnp">Buy</a>';});
 mutant('buyer A annual limit removed',s=>{s.a=s.a.replace(/no more than five refunded sessions/g,'some refunds');});
 mutant('buyer B epilepsy removed',s=>{s.b=s.b.replace(/epilepsy/g,'all listeners');});
 mutant('B poster mismatch',s=>{s.b=s.b.replace('Static dark-gradient text poster','Illustrated desk');});
 mutant('B transcript broken',s=>{s.b=s.b.replace('00:12–00:18','00:11–00:18');});
 mutant('new 2026 paper magnitude changed',s=>{s.article=s.article.replace('g = 0.09','g = 0.90');});
 mutant('article no citation',s=>{s.article=s.article.replace('https://link.springer.com/article/10.1007/s11065-026-09714-9','SOURCE MISSING');});
 mutant('shop page false purchase',s=>{let m=JSON.parse(s.matrix);m.offers[0].verified_merchant_paid_order=1;s.matrix=JSON.stringify(m);});
 let rejected=0;
 for(const t of mutants){const s={...base};t.fn(s);try{audit(s);}catch(e){rejected++;continue;}throw Error('UNSAFE MUTATION ACCEPTED: '+t.name);}
 console.log('R286 SOURCE BASELINE PASS; '+rejected+'/'+mutants.length+' adversarial changes rejected; 18/18 exact commercial gates HARD_HOLD; NO native browser/CMS/payment QA');
}
if(require.main===module)run();
module.exports={audit,run,reads};
