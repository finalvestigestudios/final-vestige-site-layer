import fs from 'node:fs';
import assert from 'node:assert/strict';
const read=n=>fs.readFileSync(new URL(n,import.meta.url),'utf8');
const a=read('ZEN12_A_TEXT.html'), b=read('ZEN12_B_FILM_CONCEPT.html');
const hub=read('MIND_HUB_WORDPRESS_SOURCE_ONLY.html'), article=read('THE_SLEEPING_WITNESS.md');
const vtt=read('film.vtt'), plan=read('CONVERSION_ACCEPTANCE.md');
const matrix=JSON.parse(read('CLAIM_SOURCE_PERMISSION_MATRIX.json'));
let n=0; const check=(condition,description)=>{assert.ok(condition,description);n++};
for(const [name,html] of [['A',a],['B',b],['hub',hub]]){
 check(html.startsWith('<!doctype html>'),name+' HTML5');
 check(html.includes('<html lang="en">'),name+' language');
 check(html.includes('name="viewport"'),name+' viewport');
 check(html.includes('name="robots" content="noindex,nofollow"'),name+' unpublished noindex');
 check(html.includes('prefers-reduced-motion'),name+' respects reduced motion');
 check(html.includes('focus-visible'),name+' focus outline');
 check(!/<(?:script|iframe|form|video)\b/i.test(html),name+' no scripts/iframes/forms/fake video');
 check(!/<a\b[^>]*\b(?:href=["'][^"']*(?:affiliate_id|ref=|hop=|tag=))/.test(html),name+' no unauthorized earning link');
}
for(const html of [a,b]){
 check(html.includes('Prospective affiliate disclosure:'),'near-link prospective disclosure');
 check(html.includes('Purchase link unavailable'),'inactive merchant');
 check(html.includes('no approved earning link activated'),'disclosure not false approval');
 check(!/<a[^>]*>\s*(?:Purchase|Buy|Unlock)/i.test(html),'no click-to-buy CTA');
 check(html.includes('52-page Seven Day Focus Fieldbook'),'existing single lead magnet');
 check(html.includes('12 levels'),'seller-described SKU');
 check(html.includes('twelve-minute sessions'),'merchant format exact');
 check(html.includes('minute'),'substantive guide');
}
check(!a.includes('Optional original 42-second film'),'A no film');
check(b.includes('Optional original 42-second film'),'B optional film concept');
check(b.includes('Complete voice transcript'),'B transcript');
check(b.includes('<svg role="img"'),'B poster with alt');
check(vtt.startsWith('WEBVTT'),'VTT header');
check((vtt.match(/-->/g)||[]).length===6,'six caption cues');
check(vtt.includes('00:00:42.000'),'film is 42 seconds');
check(article.trim().split(/\s+/).length>=1800,'deep investigation');
check(article.includes('Burgess and Kirsch'),'study comparison');
check(article.includes('Crabtree'),'history source');
check(article.includes('HARD HOLD')===false,'article independent of commerce');
check(matrix.source_list.length>=15,'provenance');
check(matrix.claim_matrix.length>=30,'claim matrix size');
check(matrix.release_gates.length===28,'28 release gates');
check(matrix.release_gates.every(g=>g.status==='HOLD'),'all release gates closed');
check(matrix.claim_matrix.find(x=>x.id==='zen_equivalence')?.editorial_status==='PROHIBITED_AS_EDITORIAL','brand equivalence rejected');
check(matrix.claim_matrix.find(x=>x.id==='partner_acceptance')?.editorial_status==='HOLD','partner acceptance hold');
check(plan.includes('net_revenue_per_1000'),'net revenue method');
check(plan.includes('UNMATCHED'),'no invented creator asset');
check(plan.includes('NOT COMPUTABLE'),'no invented payout');
console.log('PASS '+n+'/'+n+' static source assertions; all '+matrix.release_gates.length+' commerce/release gates HOLD');
