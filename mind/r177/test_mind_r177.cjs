'use strict';
/**
 * R177 source-only regression. RUN: node mind/r177/test_mind_r177.cjs
 * No CMS/network calls, external packages, browser, or merchant endpoints.
 * Source checks do NOT certify browser accessibility, checkout, or affiliate acceptance.
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const dir = __dirname;
const read = name => fs.readFileSync(path.join(dir,name),'utf8');
const investigation = read('coue-autosuggestion-from-nancy-to-the-headphones-INVESTIGATION-UNPUBLISHED.md');
const guide = read('zen12-coue-verified-claim-buyers-guide-VIDEO-PILOT-UNPUBLISHED.html');
const hub = read('mind-archive-no-sales-inference-HUB-UNPUBLISHED.html');
const matrixText = read('zen12-autosuggestion-claims-sources-CLOSED-GATES.json');
const plan = read('ONE-offer-creator-fit-ab-and-paid-conversion-ACCEPTANCE.md');
const matrix = JSON.parse(matrixText);
let baseline=0, mutants=0;
const check=(ok,msg)=>{assert.ok(ok,msg);baseline++;};
const has=(s,q)=>s.includes(q);
const guard=(html,j,docs)=>{
 const errors=[];
 if(!/<button\b[^>]*\bdisabled\b[^>]*>/is.test(html))errors.push('disabled merchant button missing');
 if(/<a\b[^>]*href\s*=\s*["'][^"']*(?:zen12\.com|inspire3\.com|awin1\.com|clickbank\.com)/i.test(html))errors.push('live merchant anchor');
 if(/<form\b/i.test(html))errors.push('duplicate conversion form');
 if(/<script\b/i.test(html))errors.push('unexpected script');
 if(/<iframe\b/i.test(html))errors.push('unexpected iframe');
 if(!/may earn a commission/i.test(html))errors.push('adjacent earning disclosure missing');
 if(!/commercial link|affiliate link|link or product-purchase CTA/i.test(html))errors.push('inactive link warning missing');
 if(!/href="https:\/\/finalvestige.com\/focus\/"/i.test(html))errors.push('single Focus destination missing');
 if(!/42.second|42 seconds|42-second|42-second/i.test(html))errors.push('video treatment missing');
 if(!/transcript/i.test(html)||!/<details>/.test(html))errors.push('accessible text treatment missing');
 if(!/noindex,nofollow/i.test(html))errors.push('indexable unapproved preview');
 if(!/prefers-reduced-motion/i.test(html))errors.push('reduced motion support missing');
 if(j.commercial_state!=='HARD_HOLD')errors.push('commercial gate open');
 if(j.approved_affiliate_url!==null)errors.push('affiliate url injected');
 if(j.qualified_human_sessions!==null||j.attributed_net_revenue_per_1000!==null)errors.push('invented actual results');
 if(!j.gates.every(x=>x.open===false))errors.push('permission gate opened');
 if(!j.claims.some(x=>x.id==='z07'&&x.status.startsWith('UNSUBSTANTIATED')))errors.push('unsupported one-hour claim reclassified');
 if(!j.claims.some(x=>x.id==='a01'&&x.status==='NOT_VERIFIED'))errors.push('publisher approval invented');
 if(!/NOT COMPUTABLE/.test(docs))errors.push('unknown revenue not acknowledged');
 if(!/Grok\/Praxxis|Grok.*Praxxis/.test(docs))errors.push('creator ownership missing');
 return errors;
};
check(/Project Gutenberg/.test(investigation),'primary history named');
check(/pubmed\.ncbi\.nlm\.nih\.gov\/16466414/.test(investigation),'study DOI/research source');
check(/6 November 2026/.test(investigation),'draft dated');
check(/No affiliate link/.test(investigation),'editorial-commercial separation');
check(/not a medical guide/.test(investigation),'not medical advice');
check(/noindex,nofollow/.test(guide),'buyer draft noindexed');
check(/<main id="main">/.test(guide),'main landmark');
check(/href="#main"/.test(guide),'skip navigation');
check(/role="img"/.test(guide),'SVG accessible role');
check(/aria-labelledby=/.test(guide),'SVG described');
check(/type="button" disabled aria-disabled="true"/.test(guide),'native disabled CTA');
check(/may earn a commission/.test(guide),'adjacent conditional disclosure');
check(/Money Back Guarantee|money-back guarantee/.test(guide),'seller refund framed');
check(/has not independently verified/.test(guide),'limit clearly stated');
check(!/<script\b/i.test(guide),'no script');
check(!/<iframe\b/i.test(guide),'no embedded stream');
check(!/<form\b/i.test(guide),'no second opt-in form');
check(/prefers-reduced-motion/.test(guide),'reduced motion');
check(/42-second/.test(guide),'optional video storyboard');
check(/<details>/.test(guide)&&/transcript/.test(guide),'no JS transcript');
check(/href="https:\/\/finalvestige.com\/focus\/"/.test(guide),'existing focus link');
check(/noindex,nofollow/.test(hub),'hub preview noindexed');
check(/History of Suggestion/.test(hub),'hub streams');
check(!/<form\b/i.test(hub),'hub no duplicate form');
check(!/zen12\.com/.test(hub),'hub no merchant link');
check(/Current checkout|checkout/.test(plan),'checkout gate');
check(/HARD HOLD/.test(plan),'hold in dossier');
check(/qualified_human_sessions/.test(plan),'denominator defined');
check(/affiliate_outbound/.test(plan),'affiliate event segregated');
check(/double-counting/.test(plan),'double count guard');
check(matrix.sources.length>=12,'source inventory');
check(matrix.claims.length>=20,'claim inventory');
check(matrix.gates.length>=10,'closed gate inventory');
check(matrix.claims.some(x=>x.id==='z05'&&x.status==='dated_seller_display_not_checkout'),'dated price proof');
check(matrix.claims.some(x=>x.id==='a07'&&x.status==='NOT_VERIFIED'),'Payhip fallback not invented');
check(guard(guide,matrix,plan).length===0,'composite prelaunch guard');
const bad=[
 ['enabled button',guide.replace('type="button" disabled aria-disabled="true"','type="button"'),matrix,plan],
 ['merchant link',guide.replace('</button>','</button><a href="https://zen12.com/">Buy</a>'),matrix,plan],
 ['script injection',guide+'<script>alert(1)</script>',matrix,plan],
 ['iframe',guide+'<iframe src="https://example.com"></iframe>',matrix,plan],
 ['duplicate form',guide+'<form><input type="email"></form>',matrix,plan],
 ['missing disclosure',guide.replace('may earn a commission','can earn something'),matrix,plan],
 ['Focus hijack',guide.replaceAll('https://finalvestige.com/focus/','https://unknown.example/focus/'),matrix,plan],
 ['missing video',guide.replaceAll('42-second','fortyish').replaceAll('42 seconds','fortyish'),matrix,plan],
 ['no noindex',guide.replace('noindex,nofollow','index,follow'),matrix,plan],
 ['no reduced motion',guide.replace('prefers-reduced-motion','prefers-motion'),matrix,plan],
 ['approved merchant',guide,{...matrix,commercial_state:'APPROVED'},plan],
 ['injected affiliate URL',guide,{...matrix,approved_affiliate_url:'https://example.test/'},plan],
 ['fake revenue',guide,{...matrix,attributed_net_revenue_per_1000:250},plan],
 ['opened permission',guide,{...matrix,gates:matrix.gates.map((x,i)=>i===0?{...x,open:true}:x)},plan],
 ['product benefit fabricated',guide,{...matrix,claims:matrix.claims.map(x=>x.id==='z07'?{...x,status:'VERIFIED'}:x)},plan],
 ['publisher approved fabricated',guide,{...matrix,claims:matrix.claims.map(x=>x.id==='a01'?{...x,status:'APPROVED'}:x)},plan],
 ['revenue unknown omitted',guide,matrix,plan.replace('NOT COMPUTABLE','fully known')],
 ['creator ownership omitted',guide,matrix,plan.replaceAll('Grok/Praxxis','creator')],
];
for(const [label,h,j,d] of bad){assert.ok(guard(h,j,d).length>0,'unsafe mutation escaped: '+label);mutants++}
console.log(JSON.stringify({status:'PASS',baseline_assertions:baseline,unsafe_mutations_detected:mutants,notes:'Source-only tests; real browser, Node-in-connected-repo, merchant, and live revenue NOT verified.'}));
