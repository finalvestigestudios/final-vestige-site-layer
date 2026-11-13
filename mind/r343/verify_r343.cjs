'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const read=n=>fs.readFileSync(path.join(__dirname,n),'utf8');
const A=read('zen12_A_text_review.html'),B=read('zen12_B_optional_video_review.html'),H=read('MIND_HUB_WP_REVIEW_ONLY.html');
const J=read('THE_COLOR_WORD_THAT_WOULD_NOT_OBEY.md'),V=read('zen12_42s.vtt'),M=JSON.parse(read('CLAIMS_SOURCE_RELEASE_GATES.json'));
let n=0; const check=(x,label)=>{assert.ok(x,label);n++};
for(const [label,v] of [['A',A],['B',B],['hub',H]]){
check(v.includes('lang="en"'),label+' language');check(v.includes('name="viewport"'),label+' mobile');check(v.includes('noindex,nofollow'),label+' not public');check(!/<script\b/i.test(v),label+' no script');check(!/<form\b/i.test(v),label+' no form');check(!/<iframe\b/i.test(v),label+' no iframe');check(!/<video\b/i.test(v),label+' no phantom video');check(!/<video[^>]*\bautoplay\b/i.test(v),label+' no autoplay attribute');
}
for(const [label,v] of [['A',A],['B',B]]){
check(/<button\s+type="button"\s+disabled\s+aria-disabled="true"/.test(v),label+' native disabled');check(v.includes('Prospective commission disclosure:'),label+' disclosure present');check(v.indexOf('Prospective commission disclosure:')<v.indexOf('Merchant link unavailable'),label+' near CTA');check(!/<a[^>]+href=["']https?:\/\/(zen12\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)/i.test(v),label+' no seller outbound');check(v.includes('https://finalvestige.com/focus/'),label+' existing funnel');check(v.includes('Premium'),label+' exact product');check(v.includes('Current checkout price'),label+' no price invention');}
const clean=v=>v.replace(/<section class="section" id="film">[\s\S]*?<\/section>/,'').replace(/Text-only|Optional film/g,'VARIANT');
check(clean(A)===clean(B),'text parity A/B excluding film');
check((B.match(/<li>\d\d.\d\d/g)||[]).length===6,'six scenes');
check((V.match(/-->/g)||[]).length===6,'six VTT cues');check(V.includes('00:00:42.000'),'42 second duration');
check(Object.values(M.release_gates).length===19,'nineteen gates');check(Object.values(M.release_gates).every(x=>x===false),'gates closed');check(M.affiliate_url===null,'no affiliate URL');check(M.revenue_data==='NOT_COMPUTABLE','no invented revenue');check(M.claims.length>=17,'evidence coverage');check(M.claims.filter(x=>x.decision==='DO_NOT_ADOPT').length>=4,'unsupported claims held');
check(J.split(/\s+/).length>1700,'longform');check(J.includes('https://pubmed.ncbi.nlm.nih.gov/16466414/'),'primary research');check(J.includes('Puységur'),'historical trail');
check(H.includes('Existing Seven Day Focus Fieldbook')||H.includes('existing Seven Day Focus Fieldbook'),'hub free funnel');
const bad=[A.replace(' disabled aria-disabled="true"',''),B.replace('Prospective commission disclosure:','Commission details elsewhere'),A.replace('noindex,nofollow','index,follow'),A.replace('</main>','<script src="https://tracker.invalid/tracker.js"></script></main>')];
check(!/<button\s+type="button"\s+disabled\s+aria-disabled="true"/.test(bad[0]),'mutation enables button detected');check(!bad[1].includes('Prospective commission disclosure:'),'mutation disclosure stripped detected');check(!bad[2].includes('noindex,nofollow'),'mutation indexing detected');check(/<script\b/.test(bad[3]),'mutation script detected');
console.log('PASS '+n+' checks: source assertions and 4 adversarial changes');
