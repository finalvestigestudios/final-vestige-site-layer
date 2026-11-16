// R429 local source-only verification. Run: node mind/r429/verify.mjs
// No network, no browser automation, no WordPress, no commission test.
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname,join} from 'node:path';
import assert from 'node:assert/strict';
const here=dirname(fileURLToPath(import.meta.url));
const read=name=>readFileSync(join(here,name),'utf8');
const A=read('ZEN12_A_TEXT_ONLY.html'), B=read('ZEN12_B_OPTIONAL_42S_STORYBOARD.html');
const hub=read('MIND_HUB_WORDPRESS_SOURCE_ONLY.html');
const article=read('THE_HAND_THAT_MOVED_BEFORE_YOU_DECIDED.md');
const vtt=read('ZEN12_STORYBOARD_42S.vtt');
const matrix=JSON.parse(read('CLAIM_SOURCE_PERMISSION_MATRIX.json'));
const plan=read('CONVERSION_ACCEPTANCE_AND_CREATOR_FIT.md');
let pass=0;
const t=(name, condition)=>{assert.ok(condition,name);pass++;};
const body=x=>x.replace(/^<!--[\s\S]*?-->\s*/,'');
const filmRE=/<section class="panel" aria-labelledby="film-title">[\s\S]*?<\/section>/;
const stripFilm=x=>x.replace(filmRE,'');
function disclosureForEveryDisabledCTA(html){
 const buttons=[...html.matchAll(/<button[^>]*disabled[^>]*>/g)];
 return buttons.length===2 && buttons.every(match=>{
   const near=html.slice(Math.max(0,match.index-650),match.index);
   return /Final Vestige may earn a commission/.test(near) && /no additional cost/i.test(near);
 });
}
function safeGuide(html){
 const anchors=[...html.matchAll(/<a\b[^>]*href="([^"]+)"/gi)].map(z=>z[1]);
 return !/<script\b|<iframe\b|<form\b|<video\b|<audio\b|onload=|onclick=|onerror=/i.test(html)
 && !/<(?:video|audio)[^>]*\bautoplay\b/i.test(html)
 && anchors.every(h=>h.startsWith('/')&&!h.startsWith('//'))
 && !/<a[^>]*href="https?:\/\//i.test(html)
 && !/<button(?![^>]*\bdisabled\b)[^>]*>/i.test(html)
 && disclosureForEveryDisabledCTA(html)
 && /No affiliate relationship or earning link has been verified/.test(html)
 && /independently adequate Zen12-specific evidence/.test(html)
 && !/guaranteed (?:cure|results)|buy now|earn \$\d+/i.test(html)
 && !/(?:pixel|gtm|analytics)\.js/.test(html);
}
t('two guide variants differ only by original optional film',body(A)===stripFilm(body(B)));
t('film is present only in B',!filmRE.test(A)&&filmRE.test(B));
t('guide A passes commercial / security invariant',safeGuide(A));
t('guide B passes commercial / security invariant',safeGuide(B));
for(const [i,h] of [A,B,hub].entries()){
 t('one H1: '+i,(h.match(/<h1\b/g)||[]).length===1);
 t('includes label: '+i,/aria-labelledby=/.test(h));
 t('responsive layout: '+i,/@media\(max-width:650px\)/.test(h));
 t('reduced motion: '+i,/@media\(prefers-reduced-motion:reduce\)/.test(h));
 t('focus visible: '+i,/:focus-visible/.test(h));
 t('CSS scope: '+i,/\#fv-mind-r429/.test(h)&&!/(?:^|\n)(?:body|html)\s*\{/m.test(h));
 t('no remote scripts: '+i,!/<script\b|<iframe\b|<link\b/i.test(h));
 t('no auto media: '+i,!/<(?:video|audio)[^>]*\bautoplay\b/i.test(h));
 t('no rendered active affiliate link: '+i,!/<a[^>]*href="https?:\/\/(?:zen12|hypnosislive|brainwaveshots|affiliates)/i.test(h));
 t('existing focus pathway: '+i,/href="\/focus\/"/.test(h));
 t('no duplicate subscribe form: '+i,!/<form\b/i.test(h));
}
t('hub has four distinct streams',(hub.match(/class="eyebrow">0[1-4] \/ /g)||[]).length===4);
t('hub uses only existing public internal routes',!/<a[^>]*href="https?:\/\//i.test(hub));
t('no direct link to unpublished article',!/<a[^>]*href="[^"]*ideomotor/i.test(hub));
t('film explicitly unencoded',/not encoded/i.test(B));
t('film original svg poster',/<svg\b[\s\S]*?<\/svg>/.test(B));
t('transcript present',/Read the full 42-second narration transcript/.test(B));
t('caption WebVTT header',vtt.startsWith('WEBVTT\n'));
const cues=[...vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d{3}) --> (\d\d):(\d\d):(\d\d)\.(\d{3})/g)].map(x=>{const n=v=>Number(v[1])*3600000+Number(v[2])*60000+Number(v[3])*1000+Number(v[4]);return [n(x.slice(1,5)),n(x.slice(5,9))]});
t('six captions',cues.length===6);
t('captions continuous zero to 42 seconds',cues.length===6&&cues[0][0]===0&&cues.at(-1)[1]===42000&&cues.every((r,i)=>r[1]>r[0]&&(!i||r[0]===cues[i-1][1])));
t('no outward unapproved media download',!/<source\b|src="https?:\/\//i.test(B));
t('article full length 2000+ words',(article.match(/\b[\p{L}'’-]+\b/gu)||[]).length>=2000);
t('article visibly unpublished',article.includes('UNPUBLISHED_RESEARCH_DRAFT'));
for(const s of ['Chevreul','Carpenter','Andersen','Puységur','twelve-minute','source ledger']){
 t('manuscript essential '+s,article.toLowerCase().includes(s.toLowerCase()));
}
t('article states no direct study of product',/none of the pendulum or Ouija studies above tested Zen12/i.test(article));
t('article avoids paid endorsement',/commercial_status: NONE_IN_INVESTIGATION/.test(article));
t('matrix 34 claims',matrix.claims.length===34&&matrix.summary.total_claims===34);
t('matrix holds 28 gates',matrix.gates.length===28&&matrix.gates.every(g=>g.status==='HOLD'));
t('no earning link in matrix',matrix.summary.merchant_link===null);
t('no made-up paid conversion',matrix.summary.confirmed_paid_affiliate_sale===null);
t('net metric null not zero',matrix.summary.verified_net_revenue_per_1000_qualified_sessions===null);
t('named publisher unapproved',matrix.summary.known_partner_authorization===false);
t('owned paid SKU unverified',matrix.summary.owned_paid_mind_sku_verified===false);
t('all claims have source or explicit unavailable status',matrix.claims.every(c=>c.sources.length>0||['NOT_VERIFIED','UNMATCHED'].includes(c.status)));
for(const id of ['C19','C20','C21','C23','C25']){
 t('unsupported claims rejected '+id,matrix.claims.find(c=>c.id===id)?.status==='NOT_ADOPTED');
}
for(const k of ['chevreul','carpenter','andersen','zen12','zen12order','ftcendorse','ftchealth']){
 t('required source '+k,/^https:\/\//.test(matrix.source_library[k]));
}
t('3 creator candidates',(plan.match(/\| "Did|\| "What/g)||[]).length===3);
t('creator IDs not fabricated',plan.includes('UNMATCHED'));
t('qualified 7 and 30 day cohorts',/seven-day and thirty-day cohorts/.test(plan));
t('no affiliate click confusion',plan.includes('affiliate_outbound')&&plan.includes('merchant_confirmed_order')&&plan.includes('settled_commission'));
t('disclosure requirement in dossier',plan.includes('may earn a commission at no additional cost'));
t('known ownership line',plan.includes('Claude controls production engineering'));
t('no unauthorized publish',plan.includes('Do not merge, deploy, publish'));
// Adversarial negative fixtures: every mutation must FAIL a substantive safety check.
const mutations=[
 ['active merchant href',A.replace('href="/focus/"','href="https://zen12.com/?aff=fake"')],
 ['active commercial button',A.replace('<button type="button" disabled','<button type="button"')],
 ['lost near CTA disclosure',A.replaceAll('Final Vestige may earn a commission','Final Vestige is independent')],
 ['invented efficacy',A.replace('No affiliate relationship or earning link has been verified','guaranteed cure for anxiety')],
 ['remote script',A.replace('</main>','<script src="https://tracker.example/pixel.js"></script></main>')],
 ['autoplay',A.replace('</main>','<video autoplay src="/sample.mp4"></video></main>')],
 ['hidden external embed',A.replace('</main>','<iframe src="https://unapproved.example"></iframe></main>')],
 ['duplicated signup form',A.replace('</main>','<form action="/subscribe"><input name="email"></form></main>')],
 ['live affiliate iframe',A.replace('</main>','<iframe src="https://zen12.com"></iframe></main>')],
 ['fake paid button',A.replace('<button type="button" disabled','<button onclick="buyNow()" type="button"')],
];
for (const [label,mutant] of mutations){t('unsafe mutation detected: '+label,!safeGuide(mutant));}
t('gate tamper would be detected',!matrix.gates.map((g,i)=>i?g:{...g,status:'PASS'}).every(g=>g.status==='HOLD'));
t('claim tamper would be detected',!matrix.claims.map(c=>c.id==='C19'?{...c,status:'SUPPORTED'}:c).filter(c=>['C19','C20','C21','C23','C25'].includes(c.id)).every(c=>c.status==='NOT_ADOPTED'));
console.log('PASS '+pass+'/'+pass+' offline source assertions; 12/12 adverse fixtures rejected. NO browser, media, merchant or CMS tests.');
