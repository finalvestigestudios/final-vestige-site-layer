'use strict';
// Run after checkout: node mind/r362/verify_r362.cjs
// Static no-network and synthetic checks only. Does not replace real-browser, WP, affiliate or financial QA.
const fs=require('node:fs'), path=require('node:path'), assert=require('node:assert/strict');
const dir=__dirname;
const read=n=>fs.readFileSync(path.join(dir,n),'utf8');
const a=read('ZEN12_A_EVIDENCE_GUIDE.html'),b=read('ZEN12_B_OPTIONAL_42S.html');
const hub=read('MIND_ARCHIVE_WP_SOURCE_ONLY.html'),vtt=read('ORIGINAL_42S_CAPTIONS.vtt');
const article=read('THE_WORD_THAT_CHANGED_THE_CRASH.md');
const plan=read('CONVERSION_ACCEPTANCE.md'),matrix=JSON.parse(read('CLAIM_SOURCE_RELEASE_MATRIX.json'));
let pass=0;
const ok=(condition,message)=>{assert.ok(condition,message);pass++};
const noMerchantHref=s=>!/<a\b[^>]*\bhref=["']https?:\/\/(?:www\.)?(?:inspire3\.com|zen12\.com|affiliates\.inspire3\.com|hypnosislive\.com|brainwaveshots\.com)/i.test(s);
const safeHtml=s=> !/<script\b|<iframe\b|<form\b|\bonclick\s*=|\bonload\s*=|javascript:|data:text\/html|<meta\s+http-equiv=["']refresh/i.test(s);
const safeCommerce=s=>noMerchantHref(s)&&/\bdisabled\b/.test(s)&&/If you buy through a link on this page, Final Vestige may earn a commission/.test(s)&&s.indexOf('Affiliate disclosure')<s.indexOf('<button type="button" disabled');
const articleCore=s=>s.match(/<article>([\s\S]*?)<\/article>/)?.[1];
const stripFilm=s=>s.replace(/<aside class="film"[\s\S]*?<\/aside>/,'');
for(const s of [a,b,hub]){
ok(/<html lang="en">/.test(s),'lang');
ok(/name="viewport"/.test(s),'viewport');
ok(/name="robots" content="noindex,nofollow"/.test(s),'noindex');
ok(/:focus-visible/.test(s),'visible keyboard focus');
ok(/prefers-reduced-motion/.test(s),'reduced-motion fallback');
ok(safeHtml(s),'no active script/form/iframe or auto-redirect');
ok(noMerchantHref(s),'no merchant-site hyperlink');
}
for(const s of [a,b]){
ok(safeCommerce(s),'adjacent disclosure and disabled commerce');
ok(/https:\/\/finalvestige\.com\/focus\//.test(s),'existing Focus route');
ok(!/<video\b/.test(s),'no video network load');
ok(!/<(?:video|audio)\b[^>]*\bautoplay\b|<source\b|<input\b/i.test(s),'no autoplay or new signup');
ok(/not a verified final checkout total/i.test(s),'price caveat');
ok(/not.*a.*clinically|not a scientifically|not scientifically|not a fair blinded/i.test(s),'claim boundary');
}
ok(articleCore(a)===stripFilm(articleCore(b)),'one-variable textual parity');
ok(/class="film"/.test(b),'B film only');
ok(!/class="film"/.test(a),'A no film');
ok(/<svg\b/.test(b)&&/<title id="posterTitle">/.test(b),'B original labeled SVG');
ok(/<details><summary>/.test(b),'B no-JS accessible transcript');
ok(!/autoplay|<video\b/i.test(b),'B no autoplay or unhosted video masquerading playable');
ok(/^WEBVTT/.test(vtt),'VTT header');
const timings=[...vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d{3}) --> (\d\d):(\d\d):(\d\d)\.(\d{3})/g)].map(m=>({from:(+m[1])*3600+(+m[2])*60+(+m[3])+(+m[4])/1000,to:(+m[5])*3600+(+m[6])*60+(+m[7])+(+m[8])/1000}));
ok(timings.length===6,'six timed cues');
ok(timings[0].from===0&&timings.at(-1).to===42,'exact 42 seconds');
ok(timings.every((t,i)=>t.to>t.from&&(i===0||t.from===timings[i-1].to)),'continuous ordered cues');
ok(article.split(/\s+/).length>1700,'substantive original source article');
for(const x of ['S1','S2','S3','S4','S5','S6','S7','S8'])ok(article.includes('['+x+']'),'article source trail '+x);
for(const x of ['THE_WORD_THAT_CHANGED_THE_CRASH.md','Zen12','NOT COMPUTABLE','Praxxis','Grok','refund','qualified_human_session','affiliate_click'])ok(plan.includes(x),'acceptance '+x);
ok(matrix.claims.length>=30,'minimum 30 explicit claim judgments');
ok(matrix.releases.length>=30,'release gates itemized');
ok(matrix.releases.every(g=>g.state==='CLOSED_UNVERIFIED'),'fail-closed release matrix');
ok(matrix.claims.some(c=>c.id==='zen12_1h_in_12m'&&c.status==='UNSUBSTANTIATED_OMIT'),'seller equivalence rejected');
ok(matrix.claims.some(c=>c.id==='fv_partner_approval'&&c.status==='UNVERIFIED_HOLD'),'no affiliate activation');
ok(matrix.financial_metric.value===null&&matrix.financial_metric.status==='NOT_COMPUTABLE','financial truthfulness');
ok(matrix.public_links_withheld===true,'links fail-closed');
ok(hub.includes('Four editorial streams')&&hub.includes('DO NOT PUBLISH'),'hub source-only');
ok(hub.includes('https://finalvestige.com/focus/'),'hub retains existing Fieldbook');
// Adversarial mutations must fail the relevant predicates; source files remain unchanged.
const attacks=[
[a.replace('<button type="button" disabled','<button type="button"'),safeCommerce],
[a.replace('If you buy through a link on this page, Final Vestige may earn a commission','Some links are affiliate links'),safeCommerce],
[a.replace('Merchant link pending verification','<a href="https://zen12.com/">Buy Zen12 now</a> Merchant link pending verification'),safeCommerce],
[b.replace('<details><summary>','<div>'),s=>(/<details><summary>/.test(s))],
[a+'<script>alert(1)</script>',safeHtml],
[b+'<iframe src="https://merchant.example/embed"></iframe>',safeHtml],
[hub+'<form action="/collect"><input name="email"></form>',safeHtml],
[a+'<meta http-equiv="refresh" content="0;url=https://zen12.com/">',safeHtml],
];
for(const [unsafe,predicate] of attacks)ok(!predicate(unsafe),'adversarial mutation rejected');
console.log('PASS '+pass+' static/source/safety assertions including '+attacks.length+' mutation rejection fixtures. NOT a browser/WP/merchant integration test.');
