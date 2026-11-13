#!/usr/bin/env node
'use strict';
// R334: source-level policy validation. No network, no writes.
// Run locally from repository root: node mind/r334/verify_r334.cjs
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const R=n=>fs.readFileSync(path.join(__dirname,n),'utf8');
const A=R('ZEN12_A_TEXT_REVIEW.html'), B=R('ZEN12_B_OPTIONAL_FILM_REVIEW.html');
const H=R('MIND_HUB_REVIEW.html'), I=R('THE_NAME_THAT_WOULD_NOT_COME.md');
const M=JSON.parse(R('OFFER_EVIDENCE_MATRIX.json')), V=R('ZEN12_42S_CAPTIONS.vtt'), S=R('ZEN12_42S_POSTER.svg');
const film=/<aside class="film"[\s\S]*?<\/aside>/;
const checks=[
 ['buyer A and B are substantively identical',()=>assert.equal(A,B.replace(film,''))],
 ['B adds one optional storyboard',()=>assert.equal((B.match(/<aside class="film"/g)||[]).length,1)],
 ['all essential content exists without JavaScript',()=>{for(const x of [A,B,H])assert.match(x,/<main class="fvm">/)}],
 ['six caption cues',()=>assert.equal((V.match(/--> /g)||[]).length,6)],
 ['caption length is exactly 42 seconds',()=>assert.match(V,/00:00:42\.000/) ],
 ['same disabled merchant button in A/B',()=>{for(const x of [A,B])assert.match(x,/<button type="button" disabled aria-disabled="true">/)}],
 ['prospective disclosure near purchase control',()=>{for(const x of [A,B]){const p=x.indexOf('<button type="button" disabled');const d=x.lastIndexOf('Prospective commission disclosure:',p);assert.ok(d>=0&&p-d<850);}}],
 ['no merchant anchors in unpublished prototypes',()=>{for(const x of [A,B,H])assert.doesNotMatch(x,/href="https?:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|brainwaveshots|affiliates\.inspire3)\./i)}],
 ['no forms scripts frames video audio',()=>{for(const x of [A,B,H])assert.doesNotMatch(x,/<(?:script|form|iframe|object|embed|video|audio)\b/i)}],
 ['mobile responsive token and reduced motion',()=>{for(const x of [A,B,H])assert.ok(x.includes('name="viewport"')&&x.includes('prefers-reduced-motion'))}],
 ['original artwork has accessible title and desc',()=>assert.ok(S.includes('<title id="t">')&&S.includes('<desc id="d">'))],
 ['all 18 partner gates closed',()=>assert.equal(M.commercial_release_gates.filter(x=>x.cleared===false).length,18)],
 ['no inferred partner approval or URL',()=>{assert.equal(M.affiliate_url,null);assert.equal(M.account_specific_inspire3_status,'NOT_AUTHENTICATED');assert.equal(M.assumed_commission,null)}],
 ['research article explicitly bounds product inference',()=>assert.ok(I.includes('None of the studies cited here tested Zen12')&&I.includes('1966')&&I.includes('2023')&&I.includes('2025'))],
 ['no false profit KPI',()=>assert.equal(M.realized_net_revenue_per_1000_qualified_human_sessions,null)],
 ['source register contains five distinct research sources and FTC',()=>assert.ok(M.claim_proof.filter(x=>/^S0[1-5]$/.test(x.id)).length===5&&M.claim_proof.filter(x=>x.class==='FTC').length===2)],
 ['candidate hub respects canonical PR #172',()=>assert.ok(H.includes('PR #172')&&H.includes('Tools Under Review'))],
 ['single original fieldbook route',()=>{for(const x of [A,B])assert.ok(x.includes('https://finalvestige.com/focus/'))}],
 ['no seller benefit as publisher-proven',()=>assert.ok(M.claim_proof.filter(x=>x.class==='PRODUCT_EFFICACY_UNSUBSTANTIATED').length>=3)]
];
let passed=0;for(const [name,fn] of checks){try{fn();passed++;console.log('PASS:',name)}catch(e){console.error('FAIL:',name,e.message);process.exitCode=1}}
console.log('R334 baseline:',passed,'/',checks.length);
