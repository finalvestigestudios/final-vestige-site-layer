/* R481 native Node regression suite: run with node mind/r481/qa.test.cjs from repository root. No dependency. */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const d = __dirname;
const read = n => fs.readFileSync(path.join(d,n),'utf8');
const files = {
  article: read('THE_FACE_THAT_LOOKED_NORMAL_UNTIL_IT_TURNED_AROUND.md'),
  a: read('ZEN12_BUYER_GUIDE_A_TEXT.html'),
  b: read('ZEN12_BUYER_GUIDE_B_STORYBOARD.html'),
  hub: read('MIND_HUB_GUTENBERG_SOURCE_ONLY.html'),
  matrix: JSON.parse(read('SOURCE_CLAIM_PERMISSION_AND_RELEASE_MATRIX.json')),
  docket: read('OFFER_FUNNEL_CREATOR_AB_AND_NET_REVENUE_DOCKET.md'),
  vtt: read('OPTIONAL_42S_CAPTIONS.vtt'),
  svg: read('OPTIONAL_42S_POSTER.svg'),
};
let count = 0;
function check(name, fn) {fn();count++;process.stdout.write('PASS '+name+'\n');}
function safeBuyer(html) {
  if(!/\bdisabled\b[^>]*aria-describedby="buy-hold"/.test(html))return false;
  if(!/Affiliate disclosure:/.test(html))return false;
  if(/href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive)\./i.test(html))return false;
  if(/<script\b|<form\b|<iframe\b|<video[^>]+autoplay|on(click|load)\s*=/i.test(html))return false;
  if(/https?:\/\/(?:[\w-]+\.)?(?:refersion|clickbank)\.[^\s"']+\?/.test(html))return false;
  return true;
}
check('article substantive length',()=>assert.ok(files.article.trim().split(/\s+/).length>=2100));
check('Thompson primary source',()=>assert.ok(files.article.includes('10.1068/p090483')));
check('Wong non-face counterevidence',()=>assert.ok(files.article.includes('10.1068/p6659')));
check('observer rotation study',()=>assert.ok(files.article.includes('10.1068/p5508')));
check('neuroimaging cited with limits',()=>assert.ok(files.article.includes('10.1177/0956797613501521')));
check('existing Puységur archive',()=>assert.ok(files.article.includes('puysegurs-animal-magnetism-files/')));
check('free existing fieldbook',()=>assert.ok(files.article.includes('https://finalvestige.com/focus/')));
check('full-text access limit',()=>assert.ok(files.article.includes('access-restricted')));
check('article not a clinical product claim',()=>assert.ok(files.article.includes('not a controlled evaluation')));
check('variant A safe',()=>assert.ok(safeBuyer(files.a)));
check('variant B safe',()=>assert.ok(safeBuyer(files.b)));
check('B includes unique optional film',()=>assert.ok(files.b.toLowerCase().includes('optional 42-second original short')));
check('A does not contain film',()=>assert.ok(!files.a.includes('<section class="panel film"')));
check('B has full 6-cue transcript',()=>assert.equal((files.b.match(/seconds:<\/strong>/g)||[]).length,6));
check('A/B buyer copy byte-identical once optional section removed',()=>{
  let b=files.b.replace(/<section class="panel film"[\s\S]*?<section class="panel" aria-labelledby="question">/, '<section class="panel" aria-labelledby="question">').replaceAll('Variant B','Variant A').replaceAll('Draft B','Draft A').replaceAll('draft B','draft A');
  assert.equal(b,files.a);
});
for(const [label,x] of [['A',files.a],['B',files.b],['hub',files.hub]]) {
  check(label+' HTML doctype lang main',()=>assert.ok(x.startsWith('<!doctype html>') && x.includes('<html lang="en">') && x.includes('<main id="main">')));
  check(label+' viewport / noindex',()=>assert.ok(x.includes('name="viewport"') && x.includes('noindex,nofollow')));
  check(label+' no scripts/form/iframe',()=>assert.ok(!/<script\b|<form\b|<iframe\b/i.test(x)));
  check(label+' reduced motion CSS',()=>assert.ok(x.includes('prefers-reduced-motion')));
}
check('A button native disabled',()=>assert.match(files.a,/<button type="button" disabled/));
check('B button native disabled',()=>assert.match(files.b,/<button type="button" disabled/));
check('A disclosure before disabled CTA',()=>assert.ok(files.a.indexOf('Affiliate disclosure:')<files.a.indexOf('<button type="button" disabled')));
check('B disclosure before disabled CTA',()=>assert.ok(files.b.indexOf('Affiliate disclosure:')<files.b.indexOf('<button type="button" disabled')));
check('no merchant direct exits in A',()=>assert.ok(!/href="https:\/\/(zen12|inspire3)\.com/i.test(files.a)));
check('no merchant direct exits in B',()=>assert.ok(!/href="https:\/\/(zen12|inspire3)\.com/i.test(files.b)));
check('matrix claims count',()=>assert.ok(files.matrix.claim_decisions.length>=25));
check('matrix gate count',()=>assert.ok(files.matrix.release_gates.length>=25));
check('all release gates unapproved',()=>assert.ok(files.matrix.release_gates.every(g=>g.status==='HARD_HOLD_UNCLEARED')));
check('matrix activation false',()=>assert.equal(files.matrix.approval_to_activate,false));
check('no paid SKU invented',()=>assert.match(files.docket,/no replacement paid Mind offer/i));
check('prior ownership protected',()=>assert.ok(files.docket.includes('PR #49')&&files.docket.includes('PR #172')));
check('no revenue invented',()=>assert.ok(files.docket.includes('NOT COMPUTABLE')));
check('creator IDs remain null',()=>assert.ok(files.docket.includes('asset_id=null')));
check('visitor PII guard',()=>assert.ok(files.docket.includes('Do not store')));
check('VTT six cues',()=>assert.equal((files.vtt.match(/--> /g)||[]).length,6));
check('VTT starts 00',()=>assert.ok(files.vtt.includes('00:00:00.000 -->')));
check('VTT ends 42 seconds',()=>assert.ok(files.vtt.includes('--> 00:00:42.000')));
check('poster original vector',()=>assert.ok(files.svg.includes('<svg')&&files.svg.includes('FORMAT IS NOT PROOF')));
let mutants=[
files.a.replace(' disabled aria-describedby',' aria-describedby'),
files.a.replace('Affiliate disclosure:','No disclosure:'),
files.a.replace('Merchant link unavailable — approval required','Buy now').replace('<button type="button" disabled','<button type="button" onclick="location.href=\'https://zen12.com/\'" disabled'),
files.a.replace('<main id="main">','<form action="https://zen12.com/"><main id="main">'),
files.a.replace('noindex,nofollow','index,follow').replace('</body>','<script src="https://analytics.example/pixel.js"></script></body>'),
files.b.replace('https://finalvestige.com/focus/','https://zen12.com/secret/')
];
for (let i=0;i<mutants.length;i++)check('unsafe mutation '+(i+1)+' blocked',()=>assert.equal(safeBuyer(mutants[i]),false));
process.stdout.write('TOTAL '+count+' checks PASS; static source checks do NOT replace browser, WCAG, WordPress, merchant or actual A/B testing.\n');
