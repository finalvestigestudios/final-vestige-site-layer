/* Final Vestige Mind R446: source-only safety/semantic test; no web requests or external libraries.
   Run: node mind/r446/QA_GATE.cjs  (from repository root)
   It NEVER mutates source. It does NOT replace real-browser accessibility, merchant, or CMS QA. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const dir=__dirname;
const read=n=>fs.readFileSync(path.join(dir,n),'utf8');
const a=read('ZEN12_A_TEXT_ONLY.html'),b=read('ZEN12_B_OPTIONAL_FILM_CONCEPT.html');
const hub=read('MIND_HUB_WORDPRESS_SOURCE_ONLY.html');
const poster=read('ZEN12_42S_POSTER.svg'),vtt=read('ZEN12_42S_CAPTIONS.vtt');
const article=read('THE_QUESTION_THAT_PUT_GLASS_IN_THE_ROAD.md');
const spec=read('CONVERSION_CREATOR_AND_REVENUE_ACCEPTANCE.md');
const matrix=JSON.parse(read('CLAIM_SOURCE_PERMISSION_MATRIX.json'));
let passed=0;
function check(label,fn){try{fn();passed++;process.stdout.write('PASS '+label+'\n')}catch(e){process.stderr.write('FAIL '+label+' '+e.message+'\n');process.exitCode=1}}
function safeHtml(t){
  assert.match(t,/<html lang="en">/i);
  assert.match(t,/<meta name="viewport"/i);
  assert.match(t,/<meta name="robots" content="noindex,nofollow"/i);
  assert.match(t,/prefers-reduced-motion/);
  assert.doesNotMatch(t,/<script\b|<iframe\b|<form\b|<input\b|<audio\b|<video\b/i);
  assert.doesNotMatch(t,/\bon(click|load|submit|error|mouseover)\s*=|javascript:|data:text\/html|http-equiv\s*=\s*["']refresh/i);
  assert.doesNotMatch(t,/https?:\/\/(?:zen12|inspire3|affiliates\.inspire3|brainwaveshots|hypnosislive)\.com[^"\s]*["']/i);
  assert.doesNotMatch(t,/<a\b[^>]+(?:utm_|asset_id=|affiliate|ref=)[^>]*>/i);
  assert.doesNotMatch(t,/pixel\.gif|google-analytics|gtag\(|fbq\(|hotjar|segment\.io/i);
  assert.doesNotMatch(t,/\b(price|discount|coupon)\s*[:=]\s*\$\d+/i);
}
function buyerSafety(t){
  safeHtml(t);
  assert.match(t,/<button type="button" disabled aria-describedby="commission">/);
  assert.match(t,/<p id="commission">If you purchase through a future earning link, Final Vestige may earn a commission at no additional cost to you\./);
  assert(t.indexOf('id="commission"')<t.indexOf('<button type="button" disabled'));
  assert(t.indexOf('<button type="button" disabled')-t.indexOf('id="commission"')<500);
  assert.match(t,/We have not used or independently tested Zen12/);
  assert.match(t,/not independently verified|not been resolved/i);
  assert.match(t,/Firstbook|Fieldbook/);
  assert.match(t,/seller.*describe/i);
  assert.match(t,/There is no need to decide under a countdown/);
}
for(const [name,t] of [['A',a],['B',b]])check('full '+name+' buyer safety',()=>buyerSafety(t));
check('substantive A/B buyer copy identical after stripping opt-in film',()=>{
  const stripped=b.replace(/<section class="film panel"[\s\S]*?<\/section>/,'');
  assert.equal(stripped,a);
});
check('film concept adds original poster + full transcript / no playback',()=>{
  assert.match(b,/<img src="\.\/ZEN12_42S_POSTER\.svg"/);
  assert.match(b,/0–7 s\./);assert.match(b,/35–42 s\./);
  assert.match(b,/not encoded, embedded, hosted, streamed or autoplayed/i);
  assert.doesNotMatch(a,/ZEN12_42S_POSTER/);
});
check('original poster is self-contained and inert',()=>{
  assert.match(poster,/<svg\b/);assert.match(poster,/<title\b/);assert.match(poster,/<desc\b/);
  assert.doesNotMatch(poster,/<script|<foreignObject|<image\s|\son\w+\s*=|https?:\/\//i);
});
check('captions have 6 successive cues covering 42 seconds',()=>{
  assert.match(vtt,/^WEBVTT/);
  const cues=[...vtt.matchAll(/(\d\d:\d\d:\d\d\.\d\d\d) --> (\d\d:\d\d:\d\d\.\d\d\d)/g)];
  assert.equal(cues.length,6);
  const time=s=>Number(s.slice(3,5))*60+Number(s.slice(6,8));
  assert.equal(time(cues[0][1]),0);assert.equal(time(cues[5][2]),42);
  for(let i=1;i<cues.length;i++)assert.equal(cues[i-1][2],cues[i][1]);
});
check('hub is an inert no-JS 4-stream preview with only published destinations',()=>{
  safeHtml(hub);assert.match(hub,/Four paths into the archive/);
  for(const term of ['Perception &amp; Attention','History of Suggestion','Practice &amp; Reflection','Tools Under Review'])assert(hub.includes(term));
  assert.match(hub,/No live WordPress page/);assert.match(hub,/no form|no new signup/i);
  assert.match(hub,/https:\/\/finalvestige\.com\/focus\//);
  assert.match(hub,/https:\/\/finalvestige\.com\/free-resources\/puysegurs-animal-magnetism-files\//);
});
check('article 2000+ words and scientific sources / historic boundaries',()=>{
  assert(article.split(/\s+/).length>2000);
  for(const item of ['1974','1978','2023','S1','S2','S3','S4','S5','S6','S7','S8','Puységur','153','16 case'])assert(article.includes(item),item);
  assert(article.includes('not evidence that Zen12 improves memory'));
  assert.match(article,/no merchant link or earning link is active/i);
});
check('claim matrix covers all 28 with source evidence and 28 closed gates',()=>{
  assert.equal(matrix.claims.length,28);assert.equal(matrix.release_gates.length,28);
  assert(matrix.release_gates.every(g=>g.state==='HOLD'));
  assert.equal(matrix.commercial_link,'NONE');
  assert(matrix.claims.every(c=>c.id&&c.claim&&c.kind&&c.status&&Array.isArray(c.source_urls)&&c.limit));
  assert(matrix.claims.filter(c=>c.source_urls.length===0).every(c=>/not authenticated/.test(c.status)));
  for(const id of ['affiliate-named','affiliate-link','commission','owned-paid','disclosure','health'])assert(matrix.claims.some(c=>c.id===id));
});
check('conversion spec separates clicks, leads and settlements',()=>{
  for(const marker of ['qualified_campaign_landing','affiliate_click','merchant_order_paid','affiliate_commission_settled','refund_or_fee_adjustment','NOT COMPUTABLE','TASK-008','HOLD'])assert(spec.includes(marker),marker);
  assert.match(spec,/no unique user's personal history/);
});
const mutants=[
['A active merchant href',a.replace('<button type="button" disabled','<a href="https://zen12.com/secret/"'),buyerSafety],
['A removed native disabled',a.replace('type="button" disabled','type="button"'),buyerSafety],
['A absent disclosure',a.replace('If you purchase through a future earning link, Final Vestige may earn a commission at no additional cost to you.',''),buyerSafety],
['A injected JS',a.replace('</main>','<script>alert(1)</script></main>'),buyerSafety],
['A extra email form',a.replace('</main>','<form><input type="email"></form></main>'),buyerSafety],
['A affiliate tracking UTM',a.replace('</main>','<a href="/?utm_campaign=secret">Buy</a></main>'),buyerSafety],
['B unsafe inline handler',b.replace('</main>','<img onerror="alert(1)"></main>'),buyerSafety],
['B tracking pixel',b.replace('</main>','<img src="pixel.gif"></main>'),buyerSafety],
['B missing prospective commission section',b.replace('<p id="commission">','<p>'),buyerSafety],
['B fake immediate price',b.replace('</main>','<p>price: $37</p></main>'),buyerSafety],
['Hub injected signup',hub.replace('</main>','<form><input type="email"></form></main>'),safeHtml],
['Hub affiliate href',hub.replace('</main>','<a href="https://zen12.com/secret/">buy</a></main>'),safeHtml]
];
for(const [label,changed,validator]of mutants)check('reject synthetic '+label,()=>{
  let rejected=false;try{validator(changed)}catch{rejected=true}
  assert(rejected,'unsafe synthetic edit was not rejected');
});
process.stdout.write('SUMMARY '+passed+'/'+(12+10)+' checks; exit='+process.exitCode+'\n');
if(process.exitCode)process.exit(1);
