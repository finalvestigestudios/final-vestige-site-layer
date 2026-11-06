/* R179 reproducible source-security and editorial checks. No dependencies beyond Node fs/path.
 * Native: node mind/r179/test_mind_r179.cjs from a local clone.
 * This does NOT replace browser, a11y, performance, real video or merchant tests.
 */
'use strict';
const fs=require('fs'), path=require('path');
const names={
 article:'ganzfeld-the-room-that-drew-its-own-pictures-INVESTIGATION-UNPUBLISHED.md',
 claims:'offer-claims-pricing-and-merchant-eligibility-matrix.json',
 guideA:'zen12-premium-A-text-UNPUBLISHED.html',
 guideB:'zen12-premium-B-optional-video-UNPUBLISHED.html',
 hub:'mind-four-stream-archive-UNPUBLISHED-WORDPRESS-DRAFT.html',
 plan:'creator-offer-funnel-conversion-and-ab-acceptance-UNPUBLISHED.md'
};
const files=Object.fromEntries(Object.entries(names).map(([k,v])=>[k,fs.readFileSync(path.join(__dirname,v),'utf8')]));
function verify(f){
 let checks=0;function ok(desc,val){checks++;if(!val)throw Error('FAILED '+desc);}
 const matrix=JSON.parse(f.claims);
 ok('claim source ledger',matrix.linked_sources.length>=15);
 ok('claim decisions',matrix.claims.length>=32);
 ok('authorization gates',matrix.required_go_no_go.length>=10);
 ok('no approval implied',matrix.required_go_no_go.some(x=>x.gate==='partner_identity'&&x.state==='HARD_HOLD'));
 ok('exact offer authorization hold',matrix.required_go_no_go.some(x=>x.gate==='exact_zen12_offer'&&x.state==='HARD_HOLD'));
 ok('specific competing price observations',f.claims.includes('$87.99')&&f.claims.includes('$87'));
 ok('no fixed checkout claim',f.claims.includes('final checkout')&&f.claims.includes('BLOCK'));
 ok('stale promotion risk',f.claims.includes('June 30, 2026'));
 ok('no fake payout record',f.claims.includes('payout')&&f.claims.includes('PAYOUT_UNVERIFIED'));
 ok('article substantive original',f.article.trim().split(/\s+/).length>2000);
 ok('primary ganzfeld study',f.article.includes('https://doi.org/10.1093/nc/niaf021'));
 ok('exact recruited and interview counts',f.article.includes('28')&&f.article.includes('45')&&f.article.includes('67')&&f.article.includes('27')&&f.article.includes('41')&&f.article.includes('66'));
 ok('no product trial inference',f.article.includes('not an experiment on Zen12')||f.article.includes('not about improved concentration'));
 ok('no dangerous home instructions',f.article.includes('do not recommend attempting prolonged sensory deprivation'));
 ok('independent editorial-only',f.article.includes('contains no commercial link or endorsement'));
 ok('published free lead path',f.article.includes('https://finalvestige.com/focus/'));
 ok('other peer-reviewed review',f.article.includes('https://doi.org/10.1016/j.jbtep.2020.101635'));
 ok('no invented affiliate earning URL',!f.article.includes('awin1.com'));
 ok('hub four streams', ['Perception & Attention','History of Suggestion','Practice & Reflection','Tools Under Review'].every(x=>f.hub.includes(x)));
 ok('hub existing Focus',f.hub.includes('https://finalvestige.com/focus/'));
 ok('hub no second form',!/<form\b/i.test(f.hub));
 ok('hub unpublished',f.hub.includes('noindex,nofollow')&&f.hub.includes('Unpublished concept'));
 ok('hub no JS',!/<script\b/i.test(f.hub));
 ok('hub source route',f.hub.includes('puysegurs-animal-magnetism-files'));
 for (const name of ['guideA','guideB']){
  const t=f[name];
  ok(name+' no script',!/<script\b/i.test(t));
  ok(name+' no external affiliate earning URL',!/(awin1\.com|cread\.php|affiliate_id=)/i.test(t));
  ok(name+' no duplicate signup',!/<form\b/i.test(t));
  ok(name+' noindex',t.includes('noindex,nofollow'));
  ok(name+' focus live path',t.includes('https://finalvestige.com/focus/'));
  ok(name+' native disabled button',/<button\b[^>]*\sdisabled(?:\s|>|=)/i.test(t));
  ok(name+' plain disclosure adjacent',/class="disclosure"[\s\S]{0,500}<button/i.test(t));
  ok(name+' price conflict visible',t.includes('$87.99')&&t.includes('$87'));
  ok(name+' no product outcome guarantee',t.includes('does not endorse medical'));
  ok(name+' official seller source citation',t.includes('href="https://zen12.com/"'));
  ok(name+' skip link',t.includes('Skip to main content'));
  ok(name+' responsive media rule',t.includes('@media(max-width:730px)'));
 }
 const m=f.guideB.match(/<section class="section" id="optional-film">[\s\S]*?<\/section>/);
 ok('optional video section exists',!!m);
 ok('text-only control no video',!f.guideA.includes('optional-film'));
 ok('A/B only added optional video',!!m&&f.guideB.replace(m[0],'')===f.guideA);
 ok('video transcript included',f.guideB.includes('42-second')&&f.guideB.includes('0–7s'));
 ok('video never autoplay',!/<video[^>]*autoplay/i.test(f.guideB));
 ok('video poster accessible',f.guideB.includes('role="img"')&&f.guideB.includes('poster-d'));
 ok('nonpublication plan',f.plan.includes('HARD HOLD')&&f.plan.includes('NOT COMPUTABLE'));
 ok('creator handoff without invented IDs',f.plan.includes('media ID')&&f.plan.includes('UNKNOWN'));
 ok('net outcome not click',f.plan.includes('affiliate_outbound')&&f.plan.includes('commissions actually settled'));
 ok('preserve negative net',f.plan.includes('Preserve negative results'));
 ok('owned product fallback not invented',f.plan.includes('No invented price, product, or paid checkout path'));
 ok('no new signup instrumentation',f.plan.includes('No new cookies'));
 ok('source claimed no publication',f.plan.includes('UNPUBLISHED'));
 return checks;
}
const mutations=[
 ['guideA','<button type="button" disabled','<button type="button"'],
 ['guideB','<button type="button" disabled','<button type="button"'],
 ['guideA','<div class="disclosure">','<div>'],
 ['guideB','<div class="disclosure">','<div>'],
 ['guideA','<title>','<script>alert(1)</script><title>'],
 ['guideB','<title>','<script>alert(1)</script><title>'],
 ['hub','<main id="main">','<form><main id="main">'],
 ['guideA','<main id="main">','<form><main id="main">'],
 ['guideB','<main id="main">','<form><main id="main">'],
 ['guideA','noindex,nofollow','index,follow'],
 ['guideB','noindex,nofollow','index,follow'],
 ['hub','noindex,nofollow','index,follow'],
 ['guideA','https://finalvestige.com/focus/','https://example.invalid'],
 ['guideB','https://finalvestige.com/focus/','https://example.invalid'],
 ['hub','https://finalvestige.com/focus/','https://example.invalid'],
 ['article','https://doi.org/10.1093/nc/niaf021','https://invalid.local'],
 ['article','do not recommend attempting prolonged sensory deprivation','recommend attempting prolonged sensory deprivation'],
 ['article','contains no commercial link or endorsement','contains a commercial endorsement'],
 ['claims','"partner_identity"','"product_photo"'],
 ['claims','"exact_zen12_offer"','"random_offer"'],
 ['claims','June 30, 2026','June 30, 2027'],
 ['plan','HARD HOLD','READY'],
 ['plan','NOT COMPUTABLE','ZERO'],
 ['guideB','id="optional-film"','id="anything_else"'],
 ['guideB','0–7s','zero-seven'],
 ['plan','affiliate_outbound','untracked'],
 ['claims','PAYOUT_UNVERIFIED','PAYOUT_VERIFIED'],
 ['hub','History of Suggestion','Commercial Miracles'],
 ['article','https://doi.org/10.1016/j.jbtep.2020.101635','https://invalid.local']
];
const baseline=verify(files);
let caught=0;for(const [key,from,to] of mutations){
 if(!files[key].includes(from))throw Error('MUTATION SOURCE MISSING '+key+' '+from);
 const damaged={...files,[key]:files[key].replace(from,to)};
 try{verify(damaged);}catch(e){caught++;continue;}
 throw Error('UNDETECTED mutation '+key+' '+from);
}
console.log(JSON.stringify({result:'PASS',baseline_assertions:baseline,mutations_rejected:caught,total_mutations:mutations.length}));
