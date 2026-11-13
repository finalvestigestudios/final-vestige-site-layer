'use strict';
/* R355 source-level validator. Run from repository root:
   node mind/r355/verify_r355.cjs
   No network, CMS, cookies, orders or personal information. */
const fs=require('node:fs');
const assert=require('node:assert/strict');
const root=__dirname+'/';
const read=f=>fs.readFileSync(root+f,'utf8');
const A=read('ZEN12_A_TEXT_REVIEW.html');
const B=read('ZEN12_B_OPTIONAL_42S_FILM_REVIEW.html');
const hub=read('MIND_HUB_WORDPRESS_REVIEW_ONLY.html');
const article=read('THE_FREQUENCY_THAT_WAS_NOT_A_VERDICT.md');
const accept=read('CONVERSION_ACCEPTANCE_OFFER_FIRST.md');
const vtt=read('ORIGINAL_42S_SCRIPT_CAPTIONS.vtt');
const matrix=JSON.parse(read('CLAIMS_SOURCES_PERMISSIONS_AND_RELEASE_GATES.json'));
let checks=0;const ok=(condition,msg)=>{assert.ok(condition,msg);checks++};
const stripFilm=s=>s.replace(/<aside class="video-proof"[\s\S]*?<\/aside>/,'');
const merchant=/<a\s+[^>]*href=["']https?:\/\/(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com|brainwaveshots\.com|hypnosislive\.com)/i;
const prohibited=/<(?:script|iframe|form|video|audio|source)\b|\bautoplay\s*=|<a\s+[^>]*href=["'](?:javascript:|data:)/i;
function validatePage(s,what){
 ok(/<!doctype html>/i.test(s),what+' doctype');
 ok(/<html lang="en">/.test(s),what+' language');
 ok(/<main id="main">/.test(s),what+' main landmark');
 ok(/href="#main"/.test(s),what+' skip link');
 ok(/<button\b[^>]*\sdisabled(?=\s|=|>)/.test(s),what+' disabled merchant button');
 ok(/may earn a commission at no additional cost to you/.test(s),what+' proximate disclosure');
 ok(s.indexOf('may earn a commission')<s.indexOf('<button type="button" disabled'),what+' disclosure DOM before CTA');
 ok(!merchant.test(s),what+' no active merchant outbound');
 ok(!prohibited.test(s),what+' no script/iframe/form/auto media');
 ok(!/\b(onclick|onerror|onload)\s*=|<meta[^>]+http-equiv=["']refresh/i.test(s),what+' no inline event/redirect');
 ok(/48 (?:downloadable )?MP3/.test(s)&&/four listening styles|four different listening styles|four styles per level/i.test(s),what+' accurate package distinctions');
 ok(/seller-page|seller effectiveness claim|seller descriptions/i.test(s),what+' no independent product-efficacy claim');
 ok(/not independently|not established|not a warranty/i.test(s),what+' evidence limits visible');
 ok(/https:\/\/finalvestige.com\/focus\//.test(s),what+' unchanged first party Focus');
 ok(/prefers-reduced-motion/.test(s),what+' reduced motion CSS');
 ok(/@media\(max-width:640px\)/.test(s),what+' mobile CSS breakpoint');
 ok(/focus-visible/.test(s),what+' keyboard focus');
}
validatePage(A,'A');validatePage(B,'B');
ok(stripFilm(B)===A,'A and B exact substantive HTML identity with film removed');
ok(/<aside class="video-proof"/.test(B),'B optional original vector poster');
ok(/<details>/.test(B)&&/<summary>/.test(B),'B native no-JS transcript');
ok(!/<aside class="video-proof"/.test(A),'A text only');
ok(/<svg viewBox="0 0 1280 720"/.test(B),'B original SVG poster');
ok(/^WEBVTT/.test(vtt),'captions VTT header');
let cues=[...vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d\d\d) --> (\d\d):(\d\d):(\d\d)\.(\d\d\d)/g)];
ok(cues.length===6,'six caption cues');
const sec=(h,m,s,ms)=>Number(h)*3600+Number(m)*60+Number(s)+Number(ms)/1000;
let next=0;for(const q of cues){let start=sec(q[1],q[2],q[3],q[4]),end=sec(q[5],q[6],q[7],q[8]);ok(start===next&&end-start===7,'caption contiguous 7 sec');next=end;}
ok(next===42,'film treatment exactly 42 seconds');
ok(article.split(/\s+/).length>=2000,'deep original product guide');
ok(/doi.org\/10.1371\/journal.pone.0286023/.test(article),'independent EEG review');
ok(/doi.org\/10.1038\/s41598-025-88517-z/.test(article),'2025 parameter experiment');
ok(/Puységur/.test(article),'history bridge');
ok(/NOT COMPUTABLE/.test(accept),'no invented net KPI');
ok(/asset_id/.test(accept),'creator linking specification');
ok(/affiliate_click/.test(accept),'affiliate click separate from paid sale');
ok(matrix.claims.length>=30,'30+ classified claims');
ok(Object.keys(matrix.sources).length>=15,'15+ source URLs');
ok(matrix.creator_topic_fit.length===3,'three creator pathways');
ok(matrix.release_gates.length>=25,'25+ gates');
ok(matrix.release_gates.every(x=>x.status==='HARD_HOLD'),'all release gates closed');
ok(matrix.creator_topic_fit.every(x=>x.asset_id===null&&x.platform_url===null),'no invented Grok media');
ok(matrix.claims.every(x=>x.source_key in matrix.sources),'every claim source key exists');
ok(!JSON.stringify(matrix).includes('sk-proj'),'no accidental API key');
ok(!/\b(?:customer_email|email_address|phone_number|payment_card)\b/.test(JSON.stringify(matrix.attribution.allowlist)),'no PII allowed for attribution');
ok(!/https?:\/\/[^\s"']+\/checkout\/buy\b/.test(A+B),'no checkout URL');
const guard=s=>/<button\b[^>]*\sdisabled(?=\s|=|>)/.test(s)&&/may earn a commission at no additional cost to you/.test(s)&&!merchant.test(s)&&!prohibited.test(s)&&!/<a\s+[^>]*href=["']javascript:/i.test(s)&&!/will cure|guaranteed focus|instant IQ boost/i.test(s);
const attacks=[
A.replace(' disabled aria-disabled',' aria-disabled'),
A.replace('may earn a commission at no additional cost to you','relationship undisclosed'),
A.replace('</main>','<a href="https://zen12.com/">BUY NOW</a></main>'),
A.replace('</main>','<script>alert(1)</script></main>'),
A.replace('</main>','<form action="https://zen12.com/"></form></main>'),
A.replace('</main>','<iframe src="https://zen12.com/"></iframe></main>'),
A.replace('</main>','<video autoplay="autoplay"></video></main>'),
A.replace('</main>','<p>guaranteed focus</p></main>')
];ok(guard(A)&&guard(B),'valid baselines pass gate');for(let i=0;i<attacks.length;i++)ok(!guard(attacks[i]),'adversarial mutation '+(i+1)+' rejected');
function netPerThousand(x){
 if(!x||x.settlement_verified!==true||x.qualified_sessions_verified!==true||!Number.isInteger(x.qualified_sessions)||x.qualified_sessions<=0)throw Error('missing authoritative settlement or qualified denominator');
 for(const k of ['settled_owned_usd','settled_affiliate_usd','fees_usd','refunds_usd','other_costs_usd'])if(typeof x[k]!=='number'||!Number.isFinite(x[k])||x[k]<0)throw Error('missing/invalid '+k);
 for(const k of ['email','ip','phone','card','fingerprint'])if(k in x)throw Error('PII '+k);
 return 1000*(x.settled_owned_usd+x.settled_affiliate_usd-x.fees_usd-x.refunds_usd-x.other_costs_usd)/x.qualified_sessions;
}
const valid={settlement_verified:true,qualified_sessions_verified:true,qualified_sessions:100,settled_owned_usd:100,settled_affiliate_usd:100,fees_usd:10,refunds_usd:20,other_costs_usd:0};
ok(netPerThousand(valid)===1700,'verified net calculation 1700');
ok(netPerThousand({...valid,refunds_usd:180})===0,'zero is real only when verified');
for(const bad of [{...valid,settlement_verified:false},{...valid,qualified_sessions_verified:false},{...valid,qualified_sessions:0},{...valid,fees_usd:null},{...valid,refunds_usd:-1},{...valid,email:'no'},{...valid,ip:'0.0.0.0'},{...valid,qualified_sessions:1.4}]){
 let rejected=false;try{netPerThousand(bad)}catch{rejected=true};ok(rejected,'unsafe settlement fixture rejected');
}
process.stdout.write('mind R355 source/commerce QA: '+checks+' checks PASS. Native Node is executed only if this script was actually run in Node; source-only V8 reuse is NOT hosted CI, browser or transaction verification.\n');
