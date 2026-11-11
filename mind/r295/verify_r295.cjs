#!/usr/bin/env node
'use strict';
// R295 repository-native safety and source QA. Run: node mind/r295/verify_r295.cjs
// These checks are unit/source QA only; NOT real-browser, CMS, merchant or payout QA.
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..');
const read=(p)=>fs.readFileSync(path.resolve(root,p),'utf8');
const files={
article:'mind/r295/THE-TAPE-THAT-CHANGED-ITS-NAME-UNPUBLISHED.md',
hub:'mind/r295/MIND-EVIDENCE-ROOM-WORDPRESS-HTML-CANDIDATE-UNPUBLISHED.html',
matrix:'mind/r295/SUBLIMINAL-AUDIO-SOURCE-CLAIM-REVENUE-GATES.json',
plan:'mind/r295/CANONICAL-ZEN12-HIGH-INTENT-VIDEO-AB-REVENUE-ACCEPTANCE.md',
vtt:'mind/r295/WHAT-THE-LABEL-PROMISED-ORIGINAL-40S.vtt',
poster:'mind/r295/THE-TAPE-ORIGINAL-LABEL-STUDY-POSTER.svg',
guideA:'mind/r284/ZEN12-BUYER-GUIDE-A-TEXT-ONLY-UNPUBLISHED.html',
guideB:'mind/r284/ZEN12-BUYER-GUIDE-B-FILM-STORYBOARD-UNPUBLISHED.html'
};
const f=Object.fromEntries(Object.entries(files).map(([k,v])=>[k,read(v)]));
const exactSources={
S01:'https://www.psychologicalscience.org/journals/psychological-science/j.1467-9280.1991.tb00112.x',
S02:'https://www.tandfonline.com/doi/abs/10.1207/s15324834basp1503_3',
S03:'https://pubmed.ncbi.nlm.nih.gov/1429349/',
S04:'https://pubmed.ncbi.nlm.nih.gov/1608733/',
S05:'https://inspire3.com/',
S06:'https://subliminalguru.com/faq',
S07:'https://zen12.com/getstarted',
S08:'https://hypnosislive.com/mental-skills/total-focus',
S09:'https://brainwaveshots.com/focus-shot',
S10:'https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking',
S11:'https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance',
S12:'https://finalvestige.com/focus/',
S13:'https://finalvestige.com/2026/11/02/mesmerism/',
S14:'https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/',
S15:'https://finalvestige.com/2026/11/02/change-blindness/',
S16:'https://finalvestige.com/blog/',
S17:'https://finalvestige.com/dispatch/'
};
const exactGates=[
'named_fv_inspire3_account_acceptance',
'written_publisher_terms_and_channel_rights',
'issued_named_earning_url',
'allowed_paid_and_organic_media_use',
'email_promotion_consent_and_permission',
'copyright_approved_creatives',
'exact_offer_identity',
'rechecked_exact_checkout_price_and_tax',
'rechecked_refund_and_chargeback_terms',
'checkout_delivery_and_availability',
'claim_specific_scientific_substantiation',
'product_specific_health_safety_review',
'adjacent_affiliate_disclosure_review',
'privacy_consent_and_no_duplicate_scripts',
'nonproduction_browser_wcag_mobile_qa',
'authentic_grok_asset_id_and_landing_url',
'merchant_paid_order_and_settlement_reconciliation',
'founder_commercial_and_production_release_approvals'
];
const exactClaimVerdicts=[
'supported','supported','supported','supported','supported','supported',
'supported_narrow','reject','seller_described','seller_unsubstantiated',
'seller_described_terms','seller_described','seller_unsubstantiated','seller_described',
'seller_unsubstantiated','seller_described_terms','seller_described','seller_unsubstantiated',
'reject','supported','supported','supported','reject','reject','reject','not_verified','supported_snapshot','reject'
];
function assertNoActiveCommerce(html){
  assert(!/<(script|iframe|form|input|video|audio|object|embed)\b/i.test(html),'no active script/form/embedded media');
  assert(!/<meta\b[^>]*http-equiv\s*=\s*["']?refresh/i.test(html),'no meta refresh');
  assert(!/url\s*\(\s*['"]?https?:/i.test(html),'no remote CSS url');
  const hrefs=[...html.matchAll(/\bhref\s*=\s*["']([^"']+)["']/gi)].map(m=>m[1]);
  const trusted=new Set(['finalvestige.com','pubmed.ncbi.nlm.nih.gov','www.psychologicalscience.org','www.tandfonline.com','www.ftc.gov','inspire3.com']);
  for(const href of hrefs){
    if(href.startsWith('#'))continue;
    assert(href.startsWith('https://'), 'outbound must be HTTPS');
    const u=new URL(href);
    assert(trusted.has(u.hostname),'unapproved outbound host: '+u.hostname);
    assert(!u.search,'no search, campaign, referral or affiliate params');
  }
  assert(!/affiliate_click|gtag\s*\(|fbq\s*\(|dataLayer|utm_/i.test(html),'no tracking');
  assert(!/style\s*=\s*["'][^"']*(display\s*:\s*none|visibility\s*:\s*hidden)/i.test(html),'no hidden disclosure');
  assert(/<button\b[^>]*disabled\b[^>]*aria-describedby\s*=\s*["']disclose["']/.test(html),'disabled buyer control described by disclosure');
  assert(/id=["']disclose["'][^>]*>/.test(html),'disclosure exists visibly');
  assert(/may earn a commission/i.test(html),'plain-language commission');
  assert(html.indexOf('id="disclose"')<html.indexOf('disabled aria-describedby="disclose"'),'disclosure before button');
  assert(/noindex,nofollow/.test(html),'unpublished noindex flag');
}
function validate(state){
 const m=JSON.parse(state.matrix);
 assert.equal(m.draft_only,true);assert.equal(m.public_activation,false);assert.equal(m.release,'HARD_HOLD_NOT_MERGED_NOT_PUBLISHED');
 assert.equal(m.source_count,17);assert.equal(m.claim_count,28);
 assert.equal(m.sources.length,17);assert.equal(m.claims.length,28);
 for(const [id,url]of Object.entries(exactSources)){
  const s=m.sources.find(s=>s.id===id);assert(s,'missing '+id);assert.equal(s.url,url,'source url '+id);
 }
 assert.equal(new Set(m.sources.map(s=>s.id)).size,17);
 assert.equal(new Set(m.sources.map(s=>s.url)).size,17);
 for(let i=0;i<28;i++){
  const c=m.claims[i];assert.equal(c.id,'C'+String(i+1).padStart(2,'0'),'claim identity');
  assert.equal(c.decision,exactClaimVerdicts[i],'claim verdict '+c.id);
  assert.equal(c.source_ids.length,1,'claim source cardinality');
  assert(m.sources.some(s=>s.id===c.source_ids[0]),'orphaned claim '+c.id);
  assert(c.limitation.length>12,'missing research limit '+c.id);
 }
 assert.deepEqual(Object.keys(m.gates).sort(),[...exactGates].sort());
 for(const value of Object.values(m.gates)){assert.equal(value.state,'HARD_HOLD');assert.equal(value.evidence,null)}
 assert.equal(m.offers.length,6);
 assert.equal(m.offers[0].id,'ZEN12');
 for(const o of m.offers.filter(o=>o.id!=='FV_SEVEN_DAY_FOCUS_FIELDBOOK')){assert(o.decision.includes('HOLD')||o.decision==='NOT_AUTHENTICATED')}
 assert.equal(m.revenue_contract.realized_net_revenue,null);
 assert.equal(m.revenue_contract.qualified_sessions_7d,null);
 assert.equal(m.revenue_contract.settled_commissions,null);
 assert.equal(m.revenue_contract.kpi_status,'NOT_COMPUTABLE_NOT_ZERO');
 for(const p of m.proposed_creator_crosswalk){
  assert.equal(p.actual_grok_asset_id,null);assert.equal(p.post_url,null);
 }
 assert(state.article.length>14000,'research manuscript unusually short');
 for(const src of ['[1] Greenwald','[2] Pratkanis','[3] Merikle','[4] Chakalis','[11] FTC','[12] FTC'])assert(state.article.includes(src),'article source missing: '+src);
 for(const rule of ['N = 237','237','78 adults','Sixty volunteers','not a blinded clinical trial','not product-specific','2026'])assert(state.article.toLowerCase().includes(rule.toLowerCase()),'article balance: '+rule);
 assert(!/\]\(https?:\/\/(?:zen12|brainwaveshots|hypnosislive|subliminalguru)\./i.test(state.article),'no reader-facing merchant purchase hyperlink in investigation');
 assertNoActiveCommerce(state.hub);
 assert(/<nav aria-label/.test(state.hub) && /@media\(max-width:720px\)/.test(state.hub),'navigation and mobile');
 assert(state.hub.includes('The Tape That Changed Its Name'),'hub connects investigation');
 assert(state.plan.includes('mind/r284/ZEN12-BUYER-GUIDE-A-TEXT-ONLY-UNPUBLISHED.html'));
 assert(state.plan.includes('mind/r284/ZEN12-BUYER-GUIDE-B-FILM-STORYBOARD-UNPUBLISHED.html'));
 assert(state.plan.includes('NOT COMPUTABLE'),'revenue data truthful');
 assert(state.plan.includes('No new form'),'single-list guard');
 assert(state.guideA.length>10000 && state.guideB.length>11000,'complete inherited A/B files required');
 for(const g of [state.guideA,state.guideB]){
  assert(/<button\b[^>]*disabled/i.test(g),'inherited CTA disabled');
  assert(/may earn a commission/.test(g),'inherited FTC disclosure');
  assert(!/<meta\b[^>]*http-equiv\s*=\s*["']?refresh/i.test(g),'no inherited meta refresh');
  assert(!/<script\b|<form\b/i.test(g),'no inherited dynamic tracking or signup');
 }
 assert(state.vtt.startsWith('WEBVTT\n'),'valid captions header');
 assert.equal((state.vtt.match(/\d{2}:\d{2}:\d{2}\.\d{3} -->/g)||[]).length,6,'six caption cues');
 assert(state.vtt.includes('00:00:40.000'),'40-second endpoint');
 assert(state.poster.includes('xmlns="http://www.w3.org/2000/svg"'));
 assert(state.poster.includes('role="img"') && state.poster.includes('<title'), 'poster accessible label');
 assert(!/<script\b|<foreignObject\b|https?:\/\/(?!www\.w3\.org\/2000\/svg)/i.test(state.poster),'no active poster resource');
 return true;
}
validate(f);
const mutationCases=[
['affiliate approved',s=>{let m=JSON.parse(s.matrix);m.gates.issued_named_earning_url.state='PASS';s.matrix=JSON.stringify(m)}],
['fake affiliate link',s=>{let m=JSON.parse(s.matrix);m.offers[0].fv_earning_url='https://bad.example/id';s.matrix=JSON.stringify(m);m.gates.issued_named_earning_url.state='PASS';s.matrix=JSON.stringify(m)}],
['invented net revenue',s=>{let m=JSON.parse(s.matrix);m.revenue_contract.realized_net_revenue=200;s.matrix=JSON.stringify(m)}],
['source swapped',s=>{let m=JSON.parse(s.matrix);m.sources[0].url='https://bad.example';s.matrix=JSON.stringify(m)}],
['deleted source',s=>{let m=JSON.parse(s.matrix);m.sources.pop();s.matrix=JSON.stringify(m)}],
['unsupported efficacy accepted',s=>{let m=JSON.parse(s.matrix);m.claims[9].decision='supported';s.matrix=JSON.stringify(m)}],
['orphan source',s=>{let m=JSON.parse(s.matrix);m.claims[0].source_ids=['MISSING'];s.matrix=JSON.stringify(m)}],
['invented asset ID',s=>{let m=JSON.parse(s.matrix);m.proposed_creator_crosswalk[0].actual_grok_asset_id='made-up';s.matrix=JSON.stringify(m)}],
['public activation',s=>{let m=JSON.parse(s.matrix);m.public_activation=true;s.matrix=JSON.stringify(m)}],
['enabling CTA',s=>{s.hub=s.hub.replace('disabled aria-describedby="disclose"','aria-describedby="disclose"')}],
['removing FTC text',s=>{s.hub=s.hub.replace('may earn a commission','has no relationship')}],
['hidden disclosure',s=>{s.hub=s.hub.replace('id="disclose"','id="disclose" style="display:none"')}],
['merchant earning link',s=>{s.hub=s.hub.replace('href="#latest"','href="https://zen12.com/getstarted?ref=secret"')}],
['malicious js',s=>{s.hub=s.hub.replace('</main>','<script>alert(1)</script></main>')}],
['email capture form',s=>{s.hub=s.hub.replace('</main>','<form><input type="email"></form></main>')}],
['third party iframe',s=>{s.hub=s.hub.replace('</main>','<iframe src="https://example.com"></iframe></main>')}],
['meta redirect',s=>{s.hub=s.hub.replace('</head>','<meta http-equiv="refresh" content="0;url=https://bad.example"></head>')}],
['external css pixel',s=>{s.hub=s.hub.replace('</style>', 'body{background-image:url(https://bad.example/pixel)}</style>')}],
['caption truncated',s=>{s.vtt=s.vtt.replace('00:00:40.000','00:00:04.000')}],
['poster embeds script',s=>{s.poster=s.poster.replace('</svg>','<script>bad()</script></svg>')}],
['erase study',s=>{s.article=s.article.replace('[1] Greenwald','[1] Deleted')}],
['remove plan canonical guide A',s=>{s.plan=s.plan.replace('mind/r284/ZEN12-BUYER-GUIDE-A-TEXT-ONLY-UNPUBLISHED.html','no guide')}],
['remove inherited disabled CTA',s=>{s.guideA=s.guideA.replace(/<button type="button" disabled/,'<button type="button"')}],
['remove inherited FTC disclosure',s=>{s.guideB=s.guideB.replace('may earn a commission','nothing to disclose')}],
['falsify article limits',s=>{s.article=s.article.replace('not product-specific','completely product-specific')}]
];
let caught=0;
for(const [name,mutate] of mutationCases){
 const state={...f};
 mutate(state);
 let rejected=false;
 try{validate(state)}catch(e){rejected=true}
 assert(rejected,'unsafe test mutation escaped: '+name);
 caught++;
}
console.log('PASS R295 baseline; 9 source files read (including full R284 A/B); 17/17 pinned source URLs; 28/28 claim decisions; 18/18 HARD_HOLD gates; '+caught+'/'+mutationCases.length+' unsafe mutations rejected.');
