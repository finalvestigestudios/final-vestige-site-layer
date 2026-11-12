#!/usr/bin/env node
// FV Mind R305 — deterministic source-only gate validator.
// Run in repository checkout: node mind/r305/verify_r305.cjs
// Passes here do NOT mean native WCAG/browser tests, WordPress approval or merchant authorization.
'use strict';
const fs = require('node:fs'), path = require('node:path');
const read = (rel) => fs.readFileSync(path.join(__dirname,rel),'utf8');
const baseline = {
 buyer: read('../r304/ZEN12-TRUTHFUL-BUYER-HYBRID-REVIEW-ONLY.html'),
 hub: read('MIND-EVIDENCE-BEFORE-INFLUENCE-WP-HTML-CANDIDATE.html'),
 article: read('THE-REFUSAL-THE-MAGNETIZER-RECORDED-UNPUBLISHED.md'),
 dossier: read('ONE-OFFER-CLAIM-CORRECTION-CONVERSION-ACCEPTANCE.md'),
 matrix: JSON.parse(read('CONSENT-SUGGESTION-ZEN12-CLAIMS-AND-COMMERCE-GATES.json'))
};
function requireTrue(label,yes){if(!yes)throw new Error(label);}
function verify(f){
 const m=f.matrix;
 requireTrue('SCHEMA',m.schema==='fv-mind-r305-evidence-commerce-v1');
 requireTrue('SOURCES',Array.isArray(m.sources)&&m.sources.length===20&&new Set(m.sources.map(s=>s.id)).size===20&&m.sources.every(s=>/^https:\/\//.test(s.url)&&s.reading_scope));
 requireTrue('CLAIMS',Array.isArray(m.claims)&&m.claims.length===30&&new Set(m.claims.map(c=>c.id)).size===30&&m.claims.every(c=>m.sources.some(s=>s.id===c.source_id)&&c.decision&&c.statement));
 requireTrue('GATES',m.commercial_gates.length===18&&m.commercial_gates.every(g=>g.status==='HARD_HOLD'&&g.proof===null));
 requireTrue('AFFILIATE_URL',m.product_candidate.approved_earning_url===null&&m.product_candidate.promotional_permission===null);
 requireTrue('REVENUE_NULL',m.realized_revenue.status==='NOT_COMPUTABLE'&&m.realized_revenue.net_revenue_per_1000===null&&m.realized_revenue.cleared_affiliate_commissions===null&&m.realized_revenue.confirmed_paid_orders===null);
 requireTrue('CREATOR_UNKNOWN',m.creator_paths.length===3&&m.creator_paths[1].owner_documented_asset_id===null&&m.creator_paths[2].owner_documented_asset_id===null);
 requireTrue('MEASUREMENT_SAFE',m.attribution_contract.affiliate_click_is_sale===false&&m.attribution_contract.cohorts_days.join(',')==='7,30');
 requireTrue('SOURCE_INSTRUMENT',m.claims.find(c=>c.id==='H09').decision==='EXCLUDE_INCORRECT_INSTRUMENT'&&m.claims.find(c=>c.id==='H08').statement.includes('Ouija'));
 requireTrue('PARTNER_STATUS',m.canonical_zen12_approval==='NOT_ESTABLISHED'&&m.commerce_status==='HARD_HOLD');
 requireTrue('EDITORIAL_LENGTH',f.article.trim().split(/\s+/).length>=1850);
 requireTrue('EDITORIAL_SOURCE',f.article.includes('https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/')&&f.article.includes('https://www.gutenberg.org/files/78413/78413-h/78413-h.htm'));
 requireTrue('EDITORIAL_DISTINCTION',f.article.includes('d\'Eslon')&&f.article.includes('did not experimentally audit every individual account'));
 requireTrue('EDITORIAL_NO_SALES',!/(affiliate commission|buy zen12|affiliate link|click here to purchase)/i.test(f.article));
 requireTrue('BUYER_2012_CORRECTION',f.buyer.includes('a 2012 Ouija-board experiment')&&f.buyer.includes('A 2022 pendulum study')&&!f.buyer.includes('earlier claim that pendulum responses could reveal answers'));
 requireTrue('BUYER_SELLER_FORMAT',f.buyer.includes('twelve levels and 48 MP3 recordings')&&f.buyer.includes('Not every recording is a guided session.'));
 for(const [prefix,html] of [['BUYER',f.buyer],['HUB',f.hub]]){
   requireTrue(prefix+'_DOCTYPE',/^<!doctype html>/i.test(html));
   requireTrue(prefix+'_LANG',/<html lang="en">/.test(html));
   requireTrue(prefix+'_VIEWPORT',/name="viewport"/.test(html));
   requireTrue(prefix+'_NOINDEX',/noindex,nofollow/.test(html));
   requireTrue(prefix+'_MAIN',/<main\b/.test(html)&&/class="skip"/.test(html));
   requireTrue(prefix+'_MOBILE',/@media\(max-width:/.test(html));
   requireTrue(prefix+'_REDUCED_MOTION',/prefers-reduced-motion:reduce/.test(html));
   requireTrue(prefix+'_NO_UNAUTH_CODE',!/<script\b|<iframe\b|<form\b|<object\b|<embed\b|<audio\b|<video\b/i.test(html));
   requireTrue(prefix+'_NO_JS_HANDLER',!/\bon(?:click|load|error|mouseover|submit|focus)\s*=/i.test(html));
   requireTrue(prefix+'_NO_REFRESH',!/<meta[^>]+http-equiv\s*=\s*["']?refresh/i.test(html));
   requireTrue(prefix+'_NO_MERCHANT_HREF',!/<a\b[^>]*href\s*=\s*["'][^"']*(?:zen12\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)/i.test(html));
   requireTrue(prefix+'_DISABLED',/<button\b[^>]*\sdisabled(?:\s|>)/.test(html));
   requireTrue(prefix+'_DISCLOSED',/may earn a commission at no additional cost to you/.test(html));
   requireTrue(prefix+'_FOCUS',/https:\/\/finalvestige\.com\/focus\//.test(html));
   requireTrue(prefix+'_NO_UNVERIFIED_PLAYBACK',!/autoplay|we tested|guaranteed focus|buy now/i.test(html));
 }
 requireTrue('HUB_PROXIMITY',/Prospective affiliate disclosure:[\s\S]{0,350}<\/div>[\s\S]{0,120}<p><button\b[^>]*disabled/.test(f.hub));
 requireTrue('BUYER_PROXIMITY',/class="disclosure"[\s\S]{0,1000}<button\b[^>]*disabled/.test(f.buyer));
 requireTrue('HUB_FOUR_STREAMS', ['PERCEPTION &amp; ATTENTION','HISTORY OF SUGGESTION','PRACTICE &amp; REFLECTION','TOOLS UNDER REVIEW'].every(s=>f.hub.includes(s)));
 requireTrue('HUB_STATIC_VIDEO',f.hub.includes('no playable file')&&f.hub.includes('0–10 seconds:'));
 requireTrue('DOSSIER_EXPERIMENT',f.dossier.includes('Variant A')&&f.dossier.includes('Variant B')&&f.dossier.includes('A/B hypothesis, not prediction'));
 requireTrue('DOSSIER_ACCOUNTING',f.dossier.includes('NOT COMPUTABLE')&&f.dossier.includes('cleared attributable FV commission'));
 requireTrue('DOSSIER_APPROVAL',f.dossier.includes('HARD HOLD')&&f.dossier.includes('No live WordPress'));
 return true;
}
function copy(){return {...baseline,matrix:JSON.parse(JSON.stringify(baseline.matrix))};}
function mutate(name,change,expected){
 const f=copy();change(f);
 try{verify(f);throw new Error('ACCEPTED_UNSAFE_MUTATION:'+name);}
 catch(e){if(e.message==='ACCEPTED_UNSAFE_MUTATION:'+name||e.message!==expected)throw new Error(name+' expected '+expected+' got '+e.message);}
}
const trials=[
 ['gate approved',f=>f.matrix.commercial_gates[0].status='APPROVED','GATES'],
 ['invent gate proof',f=>f.matrix.commercial_gates[0].proof='yes','GATES'],
 ['lose gate',f=>f.matrix.commercial_gates.pop(),'GATES'],
 ['fabricate partner',f=>f.matrix.canonical_zen12_approval='ACCEPTED','PARTNER_STATUS'],
 ['insert earning URL',f=>f.matrix.product_candidate.approved_earning_url='https://example.test/earn','AFFILIATE_URL'],
 ['make sales',f=>f.matrix.realized_revenue.confirmed_paid_orders=3,'REVENUE_NULL'],
 ['fake net',f=>f.matrix.realized_revenue.net_revenue_per_1000=80,'REVENUE_NULL'],
 ['fabricate Grok asset',f=>f.matrix.creator_paths[1].owner_documented_asset_id='UNVERIFIED123','CREATOR_UNKNOWN'],
 ['affiliate click sale',f=>f.matrix.attribution_contract.affiliate_click_is_sale=true,'MEASUREMENT_SAFE'],
 ['remove source',f=>f.matrix.sources.pop(),'SOURCES'],
 ['duplicate source',f=>f.matrix.sources[1].id=f.matrix.sources[0].id,'SOURCES'],
 ['remove claim',f=>f.matrix.claims.pop(),'CLAIMS'],
 ['bad claim source',f=>f.matrix.claims[0].source_id='NO_SOURCE','CLAIMS'],
 ['misstate experiment instrument',f=>f.matrix.claims.find(c=>c.id==='H09').decision='ALLOW_PROVEN','SOURCE_INSTRUMENT'],
 ['remove article source',f=>f.article=f.article.replace('https://www.gutenberg.org/files/78413/78413-h/78413-h.htm',''), 'EDITORIAL_SOURCE'],
 ['shorten article',f=>f.article='tiny article','EDITORIAL_LENGTH'],
 ['replace buyer Ouija',f=>f.buyer=f.buyer.replace('a 2012 Ouija-board experiment','a 2012 pendulum experiment'),'BUYER_2012_CORRECTION'],
 ['turn buyer button on',f=>f.buyer=f.buyer.replace(/<button\b([^>]*?)\sdisabled(?=\s|>)/,'<button$1'),'BUYER_DISABLED'],
 ['turn hub button on',f=>f.hub=f.hub.replace('<button type="button" disabled>','<button type="button">'),'HUB_DISABLED'],
 ['buyer checkout href',f=>f.buyer=f.buyer.replace('</main>','<a href="https://zen12.com/getstarted">Buy now</a></main>'),'BUYER_NO_MERCHANT_HREF'],
 ['hub checkout href',f=>f.hub=f.hub.replace('</main>','<a href="https://zen12.com/getstarted">Shop</a></main>'),'HUB_NO_MERCHANT_HREF'],
 ['hub tracking JS',f=>f.hub=f.hub.replace('</body>','<script src="https://tracking.test/a.js"></script></body>'),'HUB_NO_UNAUTH_CODE'],
 ['buyer new form',f=>f.buyer=f.buyer.replace('</body>','<form><input type="email"></form></body>'),'BUYER_NO_UNAUTH_CODE'],
 ['hub event handler',f=>f.hub=f.hub.replace('<main id="main">','<main id="main" onclick="run()">'),'HUB_NO_JS_HANDLER'],
 ['hub auto video',f=>f.hub=f.hub.replace('</body>','<video autoplay></video></body>'),'HUB_NO_UNAUTH_CODE'],
 ['remove buyer disclosure',f=>f.buyer=f.buyer.replace('may earn a commission at no additional cost to you','might get something'),'BUYER_DISCLOSED'],
 ['remove hub disclosure',f=>f.hub=f.hub.replace('may earn a commission at no additional cost to you','might get something'),'HUB_DISCLOSED'],
 ['remove hub focus',f=>f.hub=f.hub.replaceAll('https://finalvestige.com/focus/','https://example.test/'),'HUB_FOCUS'],
 ['remove hub storyboard',f=>f.hub=f.hub.replace('no playable file','a published film'),'HUB_STATIC_VIDEO'],
 ['remove dose comparison',f=>f.dossier=f.dossier.replace('cleared attributable FV commission','whole merchant gross checkout'),'DOSSIER_ACCOUNTING']
];
verify(baseline);
for(const [name,fn,expected] of trials)mutate(name,fn,expected);
console.log('R305 baseline PASS; '+trials.length+'/'+trials.length+' deliberate negative source mutations rejected for expected reasons. No live or merchant testing.');
module.exports={verify,trialCount:trials.length};
