// Mind R426 — reproducible, source-only regression. Run: node mind/r426/verify.mjs
// This verifies repository text and release gates; it is NOT a browser, WordPress, video or merchant test.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root=path.dirname(fileURLToPath(import.meta.url));
const get=n=>fs.readFileSync(path.join(root,n),'utf8');
const files=['THE_WORD_THAT_WOULD_NOT_GET_OUT_OF_THE_WAY.md','ZEN12_A_TEXT_ONLY.html','ZEN12_B_OPTIONAL_FILM_CONCEPT.html','ZEN12_FILM_42S.vtt','MIND_HUB_SOURCE_ONLY.html','CLAIM_SOURCE_PERMISSION_MATRIX.json','CONVERSION_ACCEPTANCE_CREATOR_ROUTE.md'];
const file=Object.fromEntries(files.map(n=>[n,get(n)]));
let n=0;const check=(condition,description)=>{if(!condition)throw new Error('FAIL '+description);n++};
const a=file['ZEN12_A_TEXT_ONLY.html'],b=file['ZEN12_B_OPTIONAL_FILM_CONCEPT.html'],hub=file['MIND_HUB_SOURCE_ONLY.html'];
const article=file['THE_WORD_THAT_WOULD_NOT_GET_OUT_OF_THE_WAY.md'];
const d=file['CONVERSION_ACCEPTANCE_CREATOR_ROUTE.md'];
const matrix=JSON.parse(file['CLAIM_SOURCE_PERMISSION_MATRIX.json']);
const vtt=file['ZEN12_FILM_42S.vtt'];
const merchant=/https?:\/\/(?:www\.)?(?:inspire3\.com|zen12\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)/i;
function checkHtml(source,label){
 check(source.startsWith('<!DOCTYPE html>'),label+' HTML5');
 check(/<html lang="en">/.test(source),label+' lang');
 check(/name="viewport"/.test(source),label+' viewport');
 check(/noindex,nofollow/.test(source),label+' noindex draft');
 check(/href="#(?:question|content)"/.test(source),label+' keyboard skip');
 check(/:focus-visible/.test(source),label+' visible focus');
 check(/prefers-reduced-motion:reduce/.test(source),label+' reduced motion');
 check(!/<script\b/i.test(source),label+' no scripts');
 check(!/<iframe\b/i.test(source),label+' no embedded third party');
 check(!/<form\b/i.test(source),label+' no signup duplication');
 check(!/\bonclick\s*=|\bonload\s*=/i.test(source),label+' no inline events');
 check(!/<(?:video|audio)[^>]*\bautoplay\b/i.test(source),label+' no autoplay attribute');
 check(!/href\s*=\s*["'][^"']*(?:inspire3\.com|zen12\.com|hypnosislive\.com|brainwaveshots\.com)/i.test(source),label+' no merchant link activation');
 check(!/src\s*=\s*["']https?:/i.test(source),label+' no remote media');
 check(!/<input\b/i.test(source),label+' no hidden lead collection');
}
checkHtml(a,'A');checkHtml(b,'B');checkHtml(hub,'Hub');
for(const [label,html] of [['A',a],['B',b]]){
 check(/<button[^>]+disabled[^>]*>/.test(html),label+' truly disabled native purchase control');
 check(/If you eventually purchase through an approved Final Vestige earning link/.test(html),label+' clear near-CTA disclosure');
 check(html.indexOf('Affiliate disclosure:')<html.indexOf('<button type="button" disabled'),label+' disclosure precedes CTA');
 check(html.indexOf('id="commission-note"')<html.indexOf('<button type="button" disabled'),label+' CTA linked to disclosure');
 check(/href="https:\/\/finalvestige\.com\/focus\/"/.test(html),label+' existing free focus route');
 check(/href="https:\/\/doi\.org\/10\.1037\/h0054651"/.test(html),label+' primary source');
 check(!/<a[^>]+\brel=["']?sponsored/i.test(html),label+' not pretending sponsored merchant link');
}
const section=x=>x.slice(x.indexOf('<section class="wrap" aria-labelledby="question">'),x.indexOf('<footer class="wrap small">'));
check(section(a)===section(b),'A/B identical substantive buyer copy and disclosure');
check(b.includes('aria-labelledby="poster-title poster-desc"'),'B accessible original poster');
check(b.includes('42-second original film element'),'B concept marked');
check(b.includes('no encoded film'),'B playable status accurately withheld');
check(b.includes('transcript'),'B transcript provided');
check(vtt.startsWith('WEBVTT'),'VTT header');
const times=[...vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d{3}) --> (\d\d):(\d\d):(\d\d)\.(\d{3})/g)];
check(times.length===6,'six caption cues');
const toMs=(a,b,c,d)=>Number(a)*3600000+Number(b)*60000+Number(c)*1000+Number(d);
let last=0;for(const t of times){const start=toMs(...t.slice(1,5));const end=toMs(...t.slice(5,9));check(start===last,'VTT continuity '+start);check(end>start,'VTT positive cue');last=end}
check(last===42000,'VTT exact 42 seconds');
check(article.trim().split(/\s+/).length>=2000,'deep original investigation');
check(article.includes('https://doi.org/10.1037/h0054651'),'article primary original study');
check(article.includes('https://doi.org/10.1037/0033-2909.109.2.163'),'article integrative review');
check(article.includes('https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'),'historical bridge');
check(article.includes('not a diagnosis'),'article nonclinical caution');
check(d.includes('NOT COMPUTABLE'),'metric honesty');
check(d.includes('UNMATCHED'),'no invented creator IDs');
check(d.includes('qualified_landing'),'human session contract');
check(d.includes('merchant_settled_commission'),'paid evidence contract');
check(d.includes('HARD HOLD'),'commercial hold in dossier');
check(Object.keys(matrix.sources).length>=18,'18+ source ledger');
check(matrix.claims.length>=30,'30+ distinct claim decisions');
check(matrix.gates.length===28,'28 release gates exactly');
check(matrix.gates.every(g=>g.status==='HOLD'&&g.proof===null),'all release gates held');
check(matrix.affiliate_cta.enabled===false&&matrix.affiliate_cta.href===null,'earning URL withheld');
check(matrix.claims.some(c=>c.id==='R08'&&c.status==='seller_claim_excluded'),'seller equivalence excluded');
check(matrix.claims.some(c=>c.id==='R15'&&c.status==='merchant_discrepancy'),'Total Focus refund discrepancy');
check(matrix.claims.some(c=>c.id==='R19'&&c.status==='seller_terms_only'),'Brainwave return restrictions');
check(matrix.claims.some(c=>c.id==='R31'&&c.status==='rejected_unsubstantiated'),'unencoded video honest');
for(const claim of matrix.claims){check(claim.source_ids.every(s=>matrix.sources[s]&&matrix.sources[s].url),'references resolve '+claim.id)}
const dangerous=[
 ['merchant href',a.replace('</body>','<a href="https://zen12.com/">Buy</a></body>'),x=>/href\s*=\s*["'][^"']*zen12\.com/i.test(x)],
 ['embedded JS',a.replace('</body>','<script>alert(1)</script></body>'),x=>/<script\b/i.test(x)],
 ['duplicate optin',a.replace('</body>','<form method="POST"></form></body>'),x=>/<form\b/i.test(x)],
 ['autoplay video',b.replace('</body>','<video autoplay></video></body>'),x=>/<video\s+autoplay/i.test(x)],
 ['third-party embed',b.replace('</body>','<iframe src="https://example.com"></iframe></body>'),x=>/<iframe\b/i.test(x)],
 ['earning URL release',JSON.stringify({...matrix,affiliate_cta:{enabled:true,href:'https://example.com/?aff=fake'}}),x=>JSON.parse(x).affiliate_cta.enabled],
 ['released gate',JSON.stringify({...matrix,gates:matrix.gates.map((g,i)=>i===0?{...g,status:'PASS'}:g)}),x=>JSON.parse(x).gates.some(g=>g.status!=='HOLD')],
 ['missing disclosure',a.replace('Affiliate disclosure:','No disclosure:'),x=>!x.includes('Affiliate disclosure:')]
];
for(const [name,mutated,detect] of dangerous)check(detect(mutated),'unsafe mutation rejected '+name);
console.log('R426 SOURCE PREFLIGHT: PASS '+n+'/'+n+' assertions; 8/8 deliberately unsafe mutations rejected. Browser/CMS/video/merchant: NOT TESTED.');
