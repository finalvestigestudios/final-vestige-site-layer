// Run: node mind/r412/verify.mjs ; source-only guardrail, NOT a browser/merchant/WP test
import {readFileSync} from 'node:fs';
import assert from 'node:assert/strict';
const base=new URL('.',import.meta.url);
const file=n=>readFileSync(new URL(n,base),'utf8');
const a=file('ZEN12_A_TEXT.html'),b=file('ZEN12_B_STORYBOARD.html'),hub=file('MIND_HUB_SOURCE_ONLY.html');
const matrix=JSON.parse(file('CLAIM_PERMISSION_MATRIX.json')),hand=file('CONVERSION_ACCEPTANCE.md'),vtt=file('ORIGINAL_42S.vtt'),article=file('WHAT_THE_LABEL_DOES.md');
let count=0;const check=(fn,message)=>{fn();count++;console.log('PASS',message)};
for(const [name,body] of [['A',a],['B',b],['Hub',hub]]) {
check(()=>assert.match(body,/<html lang="en">/),name+' lang');
check(()=>assert.match(body,/<meta name="viewport"/),name+' viewport');
check(()=>assert.match(body,/noindex,nofollow/),name+' draft-only');
check(()=>assert.doesNotMatch(body,/<script\b|<form\b|<iframe\b|<(?:video|audio)\\b[^>]*\\bautoplay\\b|fetch\(|document\.cookie/i),name+' no scripts/form/autoplay');
check(()=>assert.match(body,/https:\/\/finalvestige\.com\/focus\//),name+' existing Fieldbook');
}
for(const [name,body] of [['A',a],['B',b]]) {
check(()=>assert.match(body,/<button type="button" disabled aria-describedby="offer-gate">/),name+' native disabled CTA');
check(()=>assert.match(body,/Final Vestige may earn a commission at no additional cost/),name+' adjacent earning disclosure');
check(()=>assert.doesNotMatch(body,/href="[^"]*(?:ref=|hop=|affid=|affiliate_id=|utm_source=affiliate)/i),name+' no invented tracking URL');
check(()=>assert.match(body,/https:\/\/zen12\.com\/order/),name+' official seller source');
check(()=>assert.match(body,/2022, researchers/),name+' evidence microstory');
}
check(()=>assert.doesNotMatch(a,/<svg\b|<details\b/), 'A has no film component');
check(()=>assert.match(b,/<svg class="poster"/), 'B original SVG poster');
check(()=>assert.match(b,/<details>/), 'B optional accessible transcript details');
check(()=>assert.match(b,/not a playable or encoded film|not.*created/i), 'B plainly not playable');
check(()=>assert.equal((vtt.match(/--> /g)||[]).length,6), 'six VTT cues');
check(()=>assert.match(vtt,/00:00:42\.000/), '42-second caption total');
check(()=>assert.equal(matrix.gates.every(g=>g.status==='HOLD'&&g.proof===null),true), 'all commercial gates fail closed');
check(()=>assert.equal(matrix.claims.some(c=>c.status==='seller_efficacy_excluded'),true), 'claims separate seller efficacy');
check(()=>assert.match(hand,/NOT COMPUTABLE/), 'net revenue unavailable');
check(()=>assert.match(hand,/immutable_asset_id/), 'first-party attribution includes original media id');
check(()=>assert.match(article,/pubmed\.ncbi\.nlm\.nih\.gov\/39216636/), 'evidence includes contrary 2024 findings');
check(()=>assert.match(article,/Puységur Animal Magnetism Files/), 'historical bridge present');
check(()=>assert.match(hub,/Perception &amp; Attention/), 'four-stream hub includes perception');
check(()=>assert.match(hub,/History of Suggestion/), 'hub includes suggestion history');
check(()=>assert.match(hub,/Practice &amp; Reflection/), 'hub includes free practice');
check(()=>assert.match(hub,/Tools Under Review/), 'hub includes separated commerce');
check(()=>assert.match(hub,/max-width:680px/), 'hub mobile rule');
console.log(count+' static-source assertions passed. This does NOT certify browser, WordPress, consent, affiliate or payment behavior.');
