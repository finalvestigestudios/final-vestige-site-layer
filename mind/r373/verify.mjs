import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const root=new URL('.',import.meta.url);
const read=p=>readFileSync(new URL(p,root),'utf8');
const a=read('ZEN12_A_TEXT_GUIDE.html'),b=read('ZEN12_B_FILM_TREATMENT.html'),hub=read('MIND_ARCHIVE_WP_REVIEW_ONLY.html');
const article=read('THE_STRANGER_BEHIND_THE_DOOR.md'),vtt=read('ORIGINAL_42S_CAPTIONS.vtt'),spec=read('CONVERSION_FIRST_ACCEPTANCE.md'),matrix=JSON.parse(read('CLAIM_SOURCE_RIGHTS_MATRIX.json'));
let checks=0;function ok(c,label){assert.ok(c,label);checks++;}
function activeMerchant(s){return /<a\b[^>]*href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12\.com|affiliates\.inspire3\.com|hypnosislive\.com|brainwaveshots\.com)(?:\/|["'])/i.test(s);}
function nativeDisabled(s){return /<button\b[^>]*class=["']merchant["'][^>]*\sdisabled(?=[\s>])/.test(s);}
function safe(s){return !/<(?:script|form|iframe|object|embed)\b/i.test(s) && !/<meta[^>]+http-equiv\s*=\s*["']?refresh/i.test(s) && !/\s(?:onload|onclick|onsubmit|onerror)\s*=/i.test(s) && !activeMerchant(s) && /<meta name="robots" content="noindex,nofollow">/.test(s);}
function landing(s){
return safe(s)&&nativeDisabled(s)&&s.includes('Affiliate disclosure:')&&s.indexOf('Affiliate disclosure:')<s.indexOf('<button class="merchant"')&&s.indexOf('<button class="merchant"')-s.indexOf('Affiliate disclosure:')<1150 && s.includes('aria-describedby="merchantstatus"')&&s.includes('id="merchantstatus"') && s.includes('https://finalvestige.com/focus/') && !/<(?:video|audio)\b[^>]*\bautoplay\b/i.test(s);
}
for(const [name,h] of [['A',a],['B',b],['hub',hub]]) {
 ok(safe(h),name+' safe default');
 ok(h.includes('<a ')&&h.includes('class="skip"'),name+' skip to content');
 ok(h.includes('prefers-reduced-motion'),name+' reduced-motion');
 ok(h.includes('viewport'),name+' responsive viewport');
 ok(!/\s(?:src|href)=["']\/mind\//i.test(h),name+' no unapproved live mind link');
}
for(const [name,h] of [['A',a],['B',b]]){
 ok(landing(h),name+' disabled adjacent disclosure');
 ok((h.match(/<button class="merchant"/g)||[]).length===1,name+' one merchant control');
 ok(h.includes('This is a personal observation exercise'),name+' safe demonstration');
 ok(h.includes('not a validated attention test'),name+' no clinical test');
 ok(h.includes('No product use'),name+' no invented experience');
 ok(h.includes('seller')||h.includes('Seller'),name+' seller scope');
}
const film=/<aside class="film" data-test-film="true"[\s\S]*?<\/aside>/;
ok(film.test(b),'original optional film aside');
ok(b.replace(film,'')===a,'byte-identical A/B except film aside');
ok(!film.test(a),'A has no film');
ok(b.includes('<svg')&&b.includes('role="img"')&&b.includes('<details>'),'B original poster and accessible transcript');
ok(b.includes('not pretend a playable video exists'),'no fake playback');
ok((vtt.match(/ --> /g)||[]).length===6,'six cues');
ok(vtt.includes('00:00:35.000 --> 00:00:42.000'),'42 seconds exactly');
ok(vtt.startsWith('WEBVTT'),'valid VTT prefix');
ok(article.split(/\s+/).length>=2000,'deep original article');
for(const s of ['10.3758/BF03208840','10.1111/j.1467-9280.1997.tb00427.x','Puységur','2023','NOT PUBLISHED'])ok(article.includes(s),'original science/historical '+s);
ok(matrix.sources.length>=15,'source registry');
ok(matrix.claims.length>=30,'claims substantial');
const ids=new Set(matrix.sources.map(s=>s.id));
for(const c of matrix.claims)ok(c.source_ids.every(id=>ids.has(id)),'claim source refs '+c.id);
ok(Object.keys(matrix.release.gates).length>=32,'>=32 gates');
ok(Object.values(matrix.release.gates).every(v=>v===false),'all commercial gates fail closed');
ok(matrix.release.status==='HARD_HOLD','release hard hold');
ok(matrix.account_evidence?.result?.includes('not publisher approval'),'account email not inferred');
ok(matrix.alternative_owned_mind_sku.status==='unverified','no fake owned SKU');
for(const s of ['utm_medium','organic_social','topic_cluster_pilot_2026_11','NOT COMPUTABLE','asset_id','affiliate_outbound','verified','refund','fee'])ok(spec.includes(s),'cohort/owner contract '+s);
ok(hub.includes('not a saved WordPress CMS draft'),'no invented CMS write');
ok(hub.includes('Puységur'),'history bridge');
ok(hub.includes('finalvestige.com/focus/'),'reuse Focus');
ok(!activeMerchant(a)&&!activeMerchant(b),'no active affiliate href');
const mutants=[
[a.replace('type="button" disabled','type="button" aria-disabled="true"'),'native-disabled to aria'],
[a.replace('Affiliate disclosure:','Commercial relationship:'),'disclosure removed'],
[a.replace('<button class="merchant"','<script>alert("bad")</script><button class="merchant"'),'script'],
[a.replace('https://finalvestige.com/focus/','https://zen12.com/'),'unauthorized earning route'],
[a.replace('content="noindex,nofollow"','content="index,follow"'),'indexable preview'],
[a.replace('</main>','<form action="/subscribe"></form></main>'),'duplicate form'],
[a.replace('<button class="merchant" type="button" disabled','<button class="merchant" type="button"'),'enabled button'],
[a.replace('Affiliate disclosure:',''),'missing clear disclosure'],
[a.replace('type="button" disabled aria-describedby','type="button" aria-disabled="true" aria-describedby'),'aria false-positive'],
[a.replace('</body>','<iframe src="https://example.com"></iframe></body>'),'external embed'],
[a.replace('aria-describedby="merchantstatus"','aria-describedby="unknown"'),'broken a11y description'],
[a.replace('<button class="merchant"','<a href="https://zen12.com/">BUY</a><button class="merchant"'),'merchant href']
];
let rejected=0;
for(const [m,label] of mutants){ok(!landing(m),'unsafe mutant rejected: '+label);rejected++;}
console.log('PASS checks='+checks+' negative_mutations='+rejected+' claims='+matrix.claims.length+' sources='+matrix.sources.length+' closed_gates='+Object.keys(matrix.release.gates).length+' article_words='+article.trim().split(/\s+/).length);
