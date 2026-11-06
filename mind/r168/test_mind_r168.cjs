/* Final Vestige Mind R168 source-only compliance gate.
   Reproduce in Node: node mind/r168/test_mind_r168.cjs
   NO live website, checkout, browser, MP4, WordPress, UTM or partner validation implied.
*/
'use strict';
const fs=require('node:fs'),path=require('node:path');
const files={
article:'the-beat-between-your-ears-INVESTIGATION-UNPUBLISHED.md',
buyer:'zen12-premium-42s-evidence-buyer-PREVIEW-UNPUBLISHED.html',
hub:'mind-archive-evidence-integration-PREVIEW-UNPUBLISHED.html',
matrix:'merchant-provenance-claims-and-closed-gates.json',
plan:'offer-first-creator-fit-experiment-and-net-revenue.md'
};
const load=()=>Object.fromEntries(Object.entries(files).map(([key,file])=>[key,fs.readFileSync(path.join(__dirname,file),'utf8')]));
let assertions=0;
function check(ok,msg){assertions++;if(!ok)throw Error('R168 assertion '+assertions+' FAIL: '+msg)}
function has(text,regex,msg){check(regex.test(text),msg)}
function lacks(text,regex,msg){check(!regex.test(text),msg)}
function validate(d){
let m=JSON.parse(d.matrix);check(m.status==='DRAFT_ONLY_HARD_HOLD','release hold');
check(m.sources.length===16,'source count');check(m.claims.length===26,'claims count');check(m.gates.length===36,'gate count');
check(m.gates.every(g=>g.status==='CLOSED'),'all gates closed');
check(m.authorization.affiliate_url===null,'no invented URL');check(m.authorization.affiliate_approved===null,'no invented approval');
check(m.authorization.allowed_channels===null,'no accepted channels');check(m.authorization.commission_terms===null,'no imagined commissions');
check(m.payhip_fallback.eligible_owned_mind_sku===null,'no invented Payhip SKU');
check(m.measurement.verified_paid_orders===null,'no invented paid orders');
check(m.measurement.realized_net_revenue===null,'no invented revenue');
check(m.measurement.qualified_human_sessions===null,'no invented sessions');
check(m.measurement.revenue_per_1000_qualified_human_sessions===null,'no invented KPI');
check(m.draft_only.enabled_merchant_links===0,'no active merchant links');
check(m.draft_only.active_subscribe_forms===0,'no duplicate email capture');
check(m.draft_only.duplicate_tracking_scripts===0,'no duplicate analytics');
check(m.draft_only.commercial_publishing_approved===false,'no release');
const byId=Object.fromEntries(m.claims.map(x=>[x.id,x]));
for(const id of ['Z12-05','Z12-06','Z12-08','BWS-04'])check(byId[id].status==='EXCLUDE_UNSUBSTANTIATED','exclude unsupported '+id);
check(byId['AUD-02'].status==='SCIENCE_SUPPORTED_REVIEW','appropriate EEG review');
has(d.article,/200-hertz tone[\s\S]*210-hertz tone/,'original explanatory example');
has(d.article,/five reported results[\s\S]*eight reported contradictory[\s\S]*one produced mixed/,'precise EEG review');
has(d.article,/thirty-one studies|31 studies/,'auditory cognition review context');
has(d.article,/binaural[\s\S]*monaural/i,'different acoustic phenomena');
has(d.article,/does not automatically prove|cannot establish/,'limits on product transfer');
has(d.article,/Puységur/,'evidence history bridge');
has(d.article,/https:\/\/pubmed.ncbi.nlm.nih.gov\/37205669\//,'scientific source');
has(d.article,/https:\/\/pubmed.ncbi.nlm.nih.gov\/38458383\//,'cognition science');
has(d.article,/This investigation contains no product endorsement/,'editorial-commercial boundary');
has(d.buyer,/<html lang="en">/,'HTML language');
has(d.buyer,/<main id="main">/,'main landmark');
has(d.buyer,/Skip to content/,'skip link');
has(d.buyer,/aria-labelledby="waveTitle waveDesc"/,'graphic accessible labeling');
has(d.buyer,/<title id="waveTitle">/,'SVG titled');
has(d.buyer,/prefers-reduced-motion:reduce/,'reduced motion');
has(d.buyer,/@media\(max-width:390px\)/,'mobile layout');
has(d.buyer,/disabled aria-disabled="true"/,'physical disable');
has(d.buyer,/aria-describedby="affiliate-note"/,'disclosure proximity');
has(d.buyer,/If you purchase through an affiliate link, Final Vestige may earn a commission/,'FTC clear plain disclosure');
has(d.buyer,/No affiliate link is active/,'nonactivation explicit');
has(d.buyer,/https:\/\/finalvestige\.com\/focus\//,'existing free funnel');
has(d.buyer,/no video file|no video/i,'no video claims');
has(d.buyer,/42-second explanation|42-second|42 seconds/,'original short storyboarding');
has(d.buyer,/<details class="transcript">/,'no-JS accessible transcript disclosure');
lacks(d.buyer,/<(?:script|form|iframe|video|input)\b/i,'no thirdparty scripts, duplicate forms or fake video');
lacks(d.buyer,/(?:href|action)\s*=\s*["'](?:https?:\/\/)?(?:affiliates\.inspire3|www\.awin1|payhip\.com|checkout\.)/i,'no earning or checkout');
lacks(d.buyer,/<a[^>]+href=["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com)/i,'no merchant bypass');
lacks(d.buyer,/\sonclick\s*=|\sonload\s*=/i,'no inline browser event handlers');
has(d.hub,/<html lang="en">/,'hub language');
has(d.hub,/<main id="main"/,'hub main');
has(d.hub,/Skip to content/,'hub skip');
has(d.hub,/not a published \/mind\/ hub|not a live route/i,'hub draft status');
has(d.hub,/PR #172/,'canonical hub protection');
has(d.hub,/Perception &amp; Attention/,'stream one');
has(d.hub,/History of Suggestion/,'stream two');
has(d.hub,/Practice &amp; Reflection/,'stream three');
has(d.hub,/Tools Under Review/,'stream four');
has(d.hub,/https:\/\/finalvestige\.com\/focus\//,'hub existing free funnel');
has(d.hub,/prefers-reduced-motion:reduce/,'hub motion');
lacks(d.hub,/<(?:script|form|iframe|video|input)\b/i,'no hub tracking or added list');
lacks(d.hub,/<a[^>]+href=["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com)/i,'no hub commerce bypass');
has(d.plan,/Grok \+ Praxxis/,'separate creator owner');
has(d.plan,/NOT COMPUTABLE/,'no invented revenue');
has(d.plan,/affiliate_click/,'affiliate click distinct');
has(d.plan,/preload="none"/,'video performance spec');
has(d.plan,/30-day/,'cohorts');
has(d.plan,/7\/30-day/,'cohorts again');
has(d.plan,/qualified human sessions/,'denominator');
has(d.plan,/H0:/,'experiment null');
has(d.plan,/Founder separately approves/,'release policy');
lacks(d.plan,/paid (?:orders|commissions) (?:verified|confirmed)\s*:\s*[1-9]/i,'no claimed sales');
return assertions;
}
const original=load();let baseline=validate(original);let mutations=0;
const cases=[
['buyer',s=>s.replace('disabled aria-disabled="true"','aria-disabled="false"')],
['buyer',s=>s.replace('aria-describedby="affiliate-note"','')],
['buyer',s=>s.replace('If you purchase through an affiliate link, Final Vestige may earn a commission','Potential benefit')],
['buyer',s=>s.replace('No affiliate link is active','Affiliate link is active')],
['buyer',s=>s.replace('https://finalvestige.com/focus/','https://payhip.com/test')],
['buyer',s=>s+'<script src="https://tracking.test/x.js"></script>'],
['buyer',s=>s+'<form action="/signup"><input name="email"></form>'],
['buyer',s=>s+'<a href="https://zen12.com/">Seller bypass</a>'],
['buyer',s=>s+'<a href="https://affiliates.inspire3.com/abc">Earning URL</a>'],
['buyer',s=>s+'<video autoplay src="video.mp4"></video>'],
['buyer',s=>s.replace('prefers-reduced-motion:reduce','no-motion-rule')],
['buyer',s=>s.replace('<main id="main">','<div id="main">')],
['buyer',s=>s.replace('<title id="waveTitle">','<title>')],
['hub',s=>s+'<script>alert(1)</script>'],
['hub',s=>s+'<a href="https://brainwaveshots.com/focus-shot">Buy</a>'],
['hub',s=>s.replace('PR #172','PR changed')],
['hub',s=>s.replace('Practice &amp; Reflection','Practice')],
['hub',s=>s.replace('https://finalvestige.com/focus/','https://example.com/not-focus/')],
['article',s=>s.replace('eight reported contradictory','ten reported contradictory')],
['article',s=>s.replace('https://pubmed.ncbi.nlm.nih.gov/37205669/','https://example.invalid/')],
['matrix',s=>{let x=JSON.parse(s);x.authorization.affiliate_approved=true;return JSON.stringify(x)}],
['matrix',s=>{let x=JSON.parse(s);x.authorization.affiliate_url='https://affiliate.fake';return JSON.stringify(x)}],
['matrix',s=>{let x=JSON.parse(s);x.gates[0].status='OPEN';return JSON.stringify(x)}],
['matrix',s=>{let x=JSON.parse(s);x.measurement.verified_paid_orders=10;return JSON.stringify(x)}],
['matrix',s=>{let x=JSON.parse(s);x.measurement.realized_net_revenue=1000;return JSON.stringify(x)}],
['matrix',s=>{let x=JSON.parse(s);x.payhip_fallback.eligible_owned_mind_sku='fake';return JSON.stringify(x)}],
['matrix',s=>{let x=JSON.parse(s);x.claims.find(q=>q.id==='Z12-05').status='SCIENCE_SUPPORTED';return JSON.stringify(x)}],
['plan',s=>s.replace('NOT COMPUTABLE','zero')],
['plan',s=>s.replace('preload="none"','preload="auto"')],
['plan',s=>s.replace('H0:','HO:')]
];
for(const [file,mutate] of cases){const c={...original,[file]:mutate(original[file])};let rejected=false;try{validate(c)}catch(e){rejected=true}if(!rejected)throw Error('Mutation escaped: '+file+' '+mutations);mutations++}
console.log('R168 SOURCE ONLY PASS: '+baseline+' baseline assertions; '+mutations+'/'+cases.length+' intentional unsafe changes rejected. Native Node filesystem/browser, WordPress, video, partner eligibility, CI and merchant transaction tests NOT performed by source checks.');
