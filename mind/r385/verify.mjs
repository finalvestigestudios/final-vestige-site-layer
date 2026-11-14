/**
 * Mind R385 offline source validator. Node 22+; no dependencies, network or writes.
 * Usage from repository root: node mind/r385/verify.mjs
 * Static checks do NOT replace real browser, hosted CI, WP, video, Jetpack or commerce QA.
 */
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname,join} from 'node:path';
const base=dirname(fileURLToPath(import.meta.url));
const names=[
'THE_FACE_THAT_LOOKED_NORMAL_UNTIL_YOU_TURNED_IT_OVER.md',
'ZEN12_A_TEXT_GUIDE.html',
'ZEN12_B_OPTIONAL_FILM_STORYBOARD.html',
'MIND_HUB_WORDPRESS_REVIEW_ONLY.html',
'CLAIM_PROOF_RIGHTS_RELEASE_MATRIX.json',
'ZEN12_FILM_42S_CAPTIONS.vtt',
'ZEN12_FILM_ORIGINAL_POSTER.svg',
'CONVERSION_ACCEPTANCE_CREATOR_HANDOFF.md'
];
const files=Object.fromEntries(names.map(n=>[n,readFileSync(join(base,n),'utf8')]));
const a=files['ZEN12_A_TEXT_GUIDE.html'];
const b=files['ZEN12_B_OPTIONAL_FILM_STORYBOARD.html'];
const h=files['MIND_HUB_WORDPRESS_REVIEW_ONLY.html'];
const ar=files['THE_FACE_THAT_LOOKED_NORMAL_UNTIL_YOU_TURNED_IT_OVER.md'];
const vtt=files['ZEN12_FILM_42S_CAPTIONS.vtt'];
const svg=files['ZEN12_FILM_ORIGINAL_POSTER.svg'];
const memo=files['CONVERSION_ACCEPTANCE_CREATOR_HANDOFF.md'];
const matrix=JSON.parse(files['CLAIM_PROOF_RIGHTS_RELEASE_MATRIX.json']);
let passed=0, failed=0;
function check(name,pred){if(!pred){console.error('FAIL',name);failed++}else{passed++}}
const forbidRe=/<script\b|<iframe\b|<form\b|<video\b|<audio\b|<meta\b[^>]*http-equiv\s*=\s*["']?refresh|(?:onload|onclick|onerror|onmouseover)\s*=|javascript:|<(?:video|audio|source)\b[^>]*\bautoplay\b|googletagmanager|google-analytics|dataLayer|<img\b[^>]+src\s*=\s*["']https?:/i;
const sellerLinkRe=/<a\b[^>]*href\s*=\s*["']https?:\/\/(?:[a-z0-9-]+\.)*(?:inspire3\.com|zen12\.com|hypnosislive\.com|brainwaveshots\.com|payhip\.com|clickbank\.com)\b/i;
function allStaticGuard(s){return !forbidRe.test(s)&&!sellerLinkRe.test(s)}
function disabledCTA(s){return /<button\b[^>]*\sdisabled(?:\s|>|=)/i.test(s) && /Purchasing unavailable/.test(s)}
function nearDisclosure(s){
 let button=s.indexOf('<button'),disc=s.indexOf('If you purchase through a future approved link');
 return button>0&&disc>0&&button>disc&&button-disc<900;
}
function panelCopy(s){
 const start=s.indexOf('<section aria-labelledby="story">'),end=s.indexOf('<section><h2>Source ledger');
 if(start<0||end<start)return null;
 let core=s.slice(start,end);
 // B adds only the optional storyboard, no altered buying copy.
 core=core.replace(/<details class="film"[\s\S]*?<\/details>/,'');
 return core.trim();
}
for(const [name,s] of Object.entries({A:a,B:b,Hub:h})){
  check(name+' HTML document',/^<!doctype html>/i.test(s));
  check(name+' accessible lang',/<html lang="en">/.test(s));
  check(name+' responsive viewport',/<meta name="viewport"/.test(s));
  check(name+' no indexing',/content="noindex,nofollow"/.test(s));
  check(name+' static/no unsafe markup',allStaticGuard(s));
  check(name+' no inline event handlers',!/\bon[a-z]+\s*=/i.test(s));
  check(name+' established free resource',s.includes('https://finalvestige.com/focus/'));
}
for(const [name,s] of Object.entries({A:a,B:b})){
  check(name+' native disabled',disabledCTA(s));
  check(name+' proximate commission disclosure',nearDisclosure(s));
  check(name+' no fabricated first person',!/\b(I tried Zen12|we tested Zen12|our results showed)\b/i.test(s));
  check(name+' no numeric price',!/\$\s*\d/.test(s));
  check(name+' full seller caveat',s.includes('not')&&s.includes('independently'));
  check(name+' seller descriptions',s.includes('48 MP3')&&s.includes('12 levels'));
  check(name+' 2023 independent research',s.includes('37205669'));
  check(name+' user-controlled alternative',s.includes('twelve-minute'));
  check(name+' no duplication',!/<form\b|newsletter signup|subscribe here/i.test(s));
}
check('buyer copy A/B parity',panelCopy(a)===panelCopy(b));
check('optional storyboard only B',!a.includes('class="film"')&&b.includes('class="film"'));
check('B contains poster transcript',b.includes('<svg')&&b.includes('Timed narration'));
check('B explicitly unplayable',b.includes('non-playable storyboard'));
check('B 42s',b.includes('35–42s'));
check('B accessibility summary',b.includes('<summary>'));
check('archive links only live resources',!/<a\b[^>]*href=["'](?:\/mind\/|https:\/\/zen12\.com)/i.test(h));
check('archive four streams', ['Perception &amp; Attention','History of Suggestion','Practice &amp; Reflection','Tools Under Review'].every(x=>h.includes(x)));
check('archive disabled CTA',disabledCTA(h));
check('archive proximate disclosure',nearDisclosure(h));
check('article primary study',ar.includes('Peter Thompson')&&ar.includes('1980'));
check('article scientific correction',ar.includes('2010')&&ar.includes('2014'));
check('article ethical bridge',ar.includes("Puységur"));
check('article free trial',ar.includes('twelve-minute'));
check('article source trail',ar.includes('pubmed.ncbi.nlm.nih.gov/20942363')&&ar.includes('doi.org/10.1068/p7755'));
check('caption file format',vtt.startsWith('WEBVTT'));
check('caption six cues',Array.from(vtt.matchAll(/\d\d:\d\d:\d\d\.\d{3} --> \d\d:\d\d:\d\d\.\d{3}/g)).length===6);
check('caption 42 seconds',vtt.includes('00:00:42.000'));
check('poster original and accessible',svg.includes('role="img"')&&svg.includes('<title')&&svg.includes('<desc'));
check('poster self-contained',!/<script|<image|<foreignObject|href=/i.test(svg));
check('matrix >= 25 decisions',matrix.claims.length>=25);
check('matrix >= 10 direct sources',Object.keys(matrix.sources).length>=10);
check('matrix all hold gates',matrix.release_gates.length>=30&&matrix.release_gates.every(g=>g.status==='HOLD'));
check('matrix no issued URL',matrix.usable_affiliate_url===null);
check('matrix no paid SKU invented',matrix.owned_paid_mind_sku===null);
check('matrix no order invented',matrix.verified_paid_orders===null);
check('matrix rejects false efficacy',['Z06','Z07','Z08','B02'].every(id=>matrix.claims.find(c=>c.id===id)?.editorial_action.toLowerCase().includes('exclude')||matrix.claims.find(c=>c.id===id)?.editorial_action.toLowerCase().includes('never')));
check('memo first-party cohort and sales',''&&false || /7.day and 30.day|7\/30.day/i.test(memo));
check('memo distinguishes click and sale',memo.includes('affiliate_outbound')&&memo.includes('merchant_confirmed_purchase'));
check('memo source/owner boundaries',memo.includes('Praxxis')&&memo.includes('Claude')&&memo.includes('Founder'));
check('memo active no-go',memo.includes('No outbound merchant link'));
check('memo source paths',memo.includes('https://zen12.com/')&&memo.includes('https://finalvestige.com/focus/'));

const unsafe=[
 ['merchant link',s=>s.replace('https://finalvestige.com/focus/','https://zen12.com/') ,allStaticGuard],
 ['missing native disabled',s=>s.replace(/<button class="disabled" type="button" disabled/,'<button class="disabled" type="button"'),disabledCTA],
 ['deceptive aria disabled',s=>s.replace(/\bdisabled aria-label=/,'aria-disabled="true" aria-label='),disabledCTA],
 ['no disclosure',s=>s.replace('If you purchase through a future approved link','If you are interested'),nearDisclosure],
 ['script injection',s=>s.replace('</body>','<script>bad()</script></body>'),allStaticGuard],
 ['iframe injection',s=>s.replace('</body>','<iframe src="https://example.com"></iframe></body>'),allStaticGuard],
 ['form injection',s=>s.replace('</body>','<form><input name="email"></form></body>'),allStaticGuard],
 ['autoplay injection',s=>s.replace('</body>','<audio autoplay></audio></body>'),allStaticGuard],
 ['inline handler injection',s=>s.replace('</body>','<button onclick="bad()">x</button></body>'),allStaticGuard],
 ['price claim',s=>s.replace('</body>','<p>$87.99 guaranteed price</p></body>'),s=>!/\$\s*\d/.test(s)]
];
for(const [name,mutate,guard] of unsafe){check('reject mutation '+name,guard(mutate(a))===false)}
console.log('Mind R385 static checks '+passed+' PASS, '+failed+' FAIL; negative mutations '+unsafe.length);
if(failed)process.exitCode=1;