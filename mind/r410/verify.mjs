/**
 * R410 source-only commercial hold checks.
 * Run: node mind/r410/verify.mjs
 * This is STATIC QA only: no browser, WP, partner account or sale verification.
 */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const dir=path.dirname(fileURLToPath(import.meta.url));
const read=name=>fs.readFileSync(path.join(dir,name),'utf8');
const a=read('ZEN12_BUYER_A_TEXT.html');
const b=read('ZEN12_BUYER_B_OPTIONAL_FILM.html');
const hub=read('MIND_ARCHIVE_HUB_SOURCE_ONLY.html');
const vtt=read('ORIGINAL_42S_CAPTIONS.vtt');
const guide=read('THE_PURCHASE_IS_A_HYPOTHESIS.md');
const dossier=read('CONVERSION_ACCEPTANCE_AND_CREATOR_MAP.md');
const matrix=JSON.parse(read('SOURCE_CLAIM_AND_PERMISSION_MATRIX.json'));
let pass=0, failures=[];
const check=(condition,why)=>{if(condition)pass++;else failures.push(why)};
const buyer=s=>s.match(/<article id="buyer"[\s\S]*?<\/article>/)?.[0]??'';
const isDisabled=s=>/<button\b[^>]*\bdisabled(?:\s|=|>)/i.test(s);
const forbiddenCommerce=s=>/<a\b[^>]*href=["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|affiliates\.inspire3\.com|hypnosislive\.com|brainwaveshots\.com)/i.test(s);
const noFormsScripts=s=>!/<(?:script|form|iframe|video|audio)\b/i.test(s);
const disclosure=s=>/If you purchase through this link, Final Vestige may earn a commission at no additional cost to you\./.test(s);
const noFixed=s=>!/(?:\$\s?(?:87\.99|37(?:\.00)?|24\.44|17\.95|17\.99))/.test(s);
const articleA=buyer(a),articleB=buyer(b);
check(articleA.length>2500,'substantive A article absent');
check(articleA===articleB,'A/B substantive buyer article differs');
for(const [name,html] of [['A',a],['B',b],['Hub',hub]]){
check(/<!doctype html>/i.test(html),name+' missing document doctype');
check(/<html lang="en"/i.test(html),name+' missing language');
check(/name="viewport"/i.test(html),name+' missing viewport');
check(/name="robots" content="noindex,nofollow"/i.test(html),name+' missing draft noindex');
check(noFormsScripts(html),name+' adds form/script/media embed');
check(!forbiddenCommerce(html),name+' has merchant/earning link');
check(disclosure(html),name+' disclosure not adjacent / missing');
check(isDisabled(html),name+' merchant CTA not genuinely disabled');
check(/:focus-visible/.test(html),name+' focus-visible style missing');
check(/prefers-reduced-motion/.test(html),name+' reduced motion CSS missing');
check(/https:\/\/finalvestige\.com\/focus\//.test(html),name+' lacks single existing free route');
check(noFixed(html),name+' hardcodes unverified merchant price');
}
check(/id="buyer"/.test(a)&&/id="buyer"/.test(b),'article landmark absent');
check(!/autoplay\b/i.test(a+b+hub),'autoplay requested');
check(!/dataLayer|gtag\(|fbq\(|google-analytics|googletagmanager/i.test(a+b+hub),'tracking script reference');
check(/<svg\b[\s\S]*?<title/.test(b),'B lacks accessible original poster');
check(/role="img"/.test(b)&&/aria-labelledby="film-svg-title film-svg-desc"/.test(b),'B SVG lacks accessible naming');
check(/<details open>/.test(b)&&/id="film-transcript"/.test(b),'B lacks visible transcript');
check(/not yet encoded or embedded/.test(b),'B falsely implies playable video');
check(!/<svg\b/.test(a),'A unexpectedly includes storyboard');
check(!/<img\b/i.test(a+b+hub),'remote image requests present');
check(/Four|four-stream|four streams/i.test(guide+hub+read('README.md')),'hub stream metadata absent');
check(/#perception/.test(hub)&&/#history/.test(hub)&&/#practice/.test(hub)&&/#tools/.test(hub),'hub navigation incomplete');
check(/WEBVTT/.test(vtt),'VTT header absent');
const cueRx=/(\d\d):(\d\d):(\d\d)\.(\d{3}) --> (\d\d):(\d\d):(\d\d)\.(\d{3})/g;
const cues=[...vtt.matchAll(cueRx)].map(m=>({start:Number(m[1])*3600000+Number(m[2])*60000+Number(m[3])*1000+Number(m[4]),end:Number(m[5])*3600000+Number(m[6])*60000+Number(m[7])*1000+Number(m[8])}));
check(cues.length===6,'expected 6 subtitle cues');
check(cues.length>0&&cues[0].start===0,'captions do not start at zero');
check(cues.length>0&&cues.at(-1).end===42000,'captions do not end at 42 sec');
check(cues.every((c,i)=>c.end>c.start&&(i===0||c.start===cues[i-1].end)),'captions noncontiguous or inverted');
check(Object.keys(matrix.sources??{}).length>=14,'source list too small');
check(matrix.claims.length===24,'claim count drift');
check(matrix.release_gates.length===16,'release gate count drift');
check(matrix.claims.every(c=>c.source_ids?.every(k=>matrix.sources[k])),'unresolved claim source reference');
check(matrix.release_gates.every(g=>g.status==='HARD_HOLD'),'opened commercial release gate');
check(matrix.authorization.issued_earning_url===null,'unauthorized issued earning URL');
check(matrix.authorization.named_publisher_accepted===false,'fabricated partner approval');
check(matrix.authorization.owned_paid_mind_sku_authenticated===false,'fabricated owned paid SKU');
check(/NOT COMPUTABLE/.test(dossier),'revenue caution missing');
check(/affiliate_click/.test(dossier)&&/paid_order_confirmed/.test(dossier)&&/affiliate_commission_settled/.test(dossier),'conflated clicks/sales/commissions');
check(/asset_id/.test(dossier)&&/utm_campaign/.test(dossier),'asset-specific attribution omitted');
check(/not a new assignment/i.test(dossier),'creator role boundaries omitted');
// Mutation tests prove high-value gates reject known unsafe changes; these are static probes.
const mutations=[
['enabled button',a.replace(' disabled aria-disabled="true"',' aria-disabled="true"'),s=>isDisabled(s)],
['merchant link',a.replace('Merchant offer unavailable — approval required','<a href="https://zen12.com/pay">Buy</a>'),s=>!forbiddenCommerce(s)],
['missing disclosure',a.replace('If you purchase through this link, Final Vestige may earn a commission at no additional cost to you.',''),s=>disclosure(s)],
['script injection',a.replace('</main>','<script src="https://example.test/pixel.js"></script></main>'),s=>noFormsScripts(s)],
['forced video',b.replace('</main>','<video autoplay src="track.mp4"></video></main>'),s=>noFormsScripts(s)],
['dup signup',hub.replace('</main>','<form><input type="email"></form></main>'),s=>noFormsScripts(s)],
['unverified price',a.replace('Some people prefer','$87.99 Some people prefer'),s=>noFixed(s)],
['ungated affiliate',JSON.stringify({...matrix,release_gates:matrix.release_gates.map((g,i)=>i?g:{...g,status:'APPROVED'})}),s=>JSON.parse(s).release_gates.every(g=>g.status==='HARD_HOLD')]
];
for(const [name,mutant,property] of mutations)check(!property(mutant),'mutant escaped safety gate: '+name);
console.log(JSON.stringify({status:failures.length?'FAIL':'PASS',passed:pass,failed:failures.length,failures,media:'static storyboard only',commerce:'HARD HOLD',ci:'this script is local source QA, not actual merchant/browser testing'},null,2));
if(failures.length)process.exitCode=1;
