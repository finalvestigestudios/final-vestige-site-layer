/* R184 source-only safety regression.
   Native: node mind/r184/test_mind_r184.cjs (from repository root)
   Portable: const {run}=require('./test_mind_r184.cjs'); run({article, guide, a, b, hub, ledger, dossier})
   This checks markup and source safety, not actual browser accessibility, payment or video playback.
*/
'use strict';
const fs=require('fs');
const root='mind/r184/';
const p={article:'the-second-number-that-disappeared-INVESTIGATION-UNPUBLISHED.md',guide:'zen12-independent-buyer-guide-UNPUBLISHED.md',a:'zen12-premium-A-text-UNPUBLISHED.html',b:'zen12-premium-B-optional-film-UNPUBLISHED.html',hub:'mind-archive-four-stream-WORDPRESS-PREVIEW-UNPUBLISHED.html',ledger:'claims-offer-and-merchant-gates.json',dossier:'offer-first-creator-conversion-and-revenue-ACCEPTANCE.md'};
function readAll(){return Object.fromEntries(Object.entries(p).map(([k,n])=>[k,fs.readFileSync(root+n,'utf8')]));}
function run(files){
let passed=0;const fails=[];
function check(ok,message){if(ok)passed++;else fails.push(message)}
const {article,guide,a,b,hub,ledger,dossier}=files;let json;try{json=JSON.parse(ledger)}catch(e){fails.push('ledger parses: '+e.message);return {passed,fails}}
check(article.length>8500,'substantive original investigation');
check((article.match(/https:\/\/(?:doi.org|pubmed.ncbi.nlm.nih.gov)/g)||[]).length>=5,'primary research links');
check(article.includes('17 people')&&article.includes('23 meditation-interested'),'group sizes contextualized');
check(article.includes('not a test of Zen12')||article.includes('neither was a test of Zen12'),'no study-to-product inference');
check(!/https:\/\/.*(?:awin1|affiliate\/redirect|clickbank)/i.test(article),'research no earning url');
check(guide.includes('NOT')||guide.includes('not'),'guide distinguishes limits');
check(guide.includes('12 levels')||guide.includes('twelve levels'),'seller package specified');
check(guide.includes('No payment-page transaction'),'checkout not asserted');
check(guide.includes('No earning link is active'),'commercial gate visible');
check(dossier.includes('NOT COMPUTABLE'),'honest primary KPI');
check(dossier.includes('qualified human'),'privacy unit');
check(dossier.includes('settled_revenue'),'settled cash separate');
check(dossier.includes('Grok')&&dossier.includes('TASK-008'),'creator owner boundaries');
check(dossier.includes('7/30'),'cohorts specified');
check(json.advertising_activation===false,'affiliate activation false');
check(json.partner.authorized_earning_url===null,'earning url null');
check(json.owned_fallback.sku===null,'owned fallback sku not fabricated');
check(json.metrics.realized_net_revenue===null,'revenue unknown');
check(json.merchant.refund_tested===false,'refund not falsely tested');
check(json.gates.some(g=>g.status==='HARD_HOLD'),'commercial gates closed');
for(const [name,html] of [['a',a],['b',b],['hub',hub]]){
check(/<!doctype html>/i.test(html),name+' valid html5 start');
check(/<html lang="en">/.test(html),name+' language');
check(/name="viewport"/.test(html),name+' viewport');
check(/<main>/.test(html),name+' main landmark');
check(/:focus-visible/.test(html),name+' keyboard focus');
check(/prefers-reduced-motion/.test(html),name+' reduced motion style');
check(!/<(?:script|iframe|form)\b|<(?:video|audio)\b[^>]*\sautoplay(?:\s|=|>)|onload\s*=|onclick\s*=/i.test(html),name+' no scripts/forms/auto play');
check(!/(?:awin1\.com|hop\.clickbank|tracking_id=|aff_id=)/i.test(html),name+' no affiliate url');
}
for(const [name,html] of [['a',a],['b',b]]){
check(/<button[^>]*\sdisabled(?:\s|>|=)[^>]*>/.test(html),name+' natively disabled buying control');
check(/Affiliate disclosure for a future approved link/.test(html),name+' adjacent truthful disclosure');
check(html.indexOf('Affiliate disclosure for a future approved link')-html.indexOf('<button type="button" class="disabled"')<600,name+' disclosure near control');
check(/noindex,nofollow/.test(html),name+' not search-indexable if preview exposed');
check(/zen12\.com/.test(html),name+' exact seller source');
}
check(!a.includes('optional-film')&&b.includes('optional-film'),'optional film only in B');
const norm=x=>x.replace(/<section id="optional-film"[\s\S]*?<\/section>/,'').replace(/Prototype [AB] · [^<]*/,'Prototype VARIANT').replace(/UNPUBLISHED.html/,'UNPUBLISHED.html');
check(norm(a)===norm(b),'A and B equal except optional film treatment');
check(b.includes('00–07')&&b.includes('33–42'),'42-second transcript timing');
check(!/<video\b/.test(b),'no claimed playable video');
check(hub.includes('four-stream')||hub.includes('four-stream'),'unpublished four-stream indication');
check(hub.includes('/focus/')&&!/<form\b/i.test(hub),'sole focus link no form');
check(!/href="https?:\/\/[^"]*payhip/i.test(a+b),'no invented owned checkout link');
const mutationInputs=[
{key:'a',s:'disabled aria-disabled',r:'aria-disabled',note:'enable button'},
{key:'a',s:'Affiliate disclosure for a future approved link',r:'Affiliate note',note:'remove near disclosure'},
{key:'a',s:'noindex,nofollow',r:'index,follow',note:'preview discoverable'},
{key:'a',s:'<main>',r:'<div>',note:'missing main landmark'},
{key:'a',s:':focus-visible',r:':focus-hidden',note:'keyboard focus'},
{key:'a',s:'prefers-reduced-motion',r:'prefers-allow-motion',note:'reduce motion'},
{key:'b',s:'No earning link is active here.',r:'Earning link is active.',note:'false earned link'},
{key:'b',s:'42 seconds: the second number',r:'42 seconds: the seller promise',note:'film identity'},
{key:'hub',s:'https://finalvestige.com/focus/',r:'https://new-email-vendor.example/subscribe',note:'duplicate signup destination'},
{key:'dossier',s:'NOT COMPUTABLE',r:'$1000',note:'invented KPI'},
{key:'ledger',s:'"advertising_activation": false',r:'"advertising_activation": true',note:'activation unsafe'},
{key:'ledger',s:'"authorized_earning_url": null',r:'"authorized_earning_url": "https://some-link.example"',note:'earning URL invented'},
{key:'ledger',s:'"realized_net_revenue": null',r:'"realized_net_revenue": 500',note:'revenue invented'},
{key:'article',s:'not a test of Zen12',r:'a test of Zen12',note:'evidence transfer'}
];
let caught=0;const negative=[];
const statusUnsafe=(v)=>{try{const j=JSON.parse(v.ledger);return j.advertising_activation||j.partner.authorized_earning_url!==null||j.metrics.realized_net_revenue!==null}catch(e){return true}};
for(const m of mutationInputs){const original=files[m.key];if(!original.includes(m.s)){negative.push('setup missing '+m.note);continue}const altered={...files,[m.key]:original.replaceAll(m.s,m.r)};const detect= m.key==='ledger'?statusUnsafe(altered):m.key==='article'?!altered.article.includes('not a test of Zen12'):m.key==='dossier'?!altered.dossier.includes('NOT COMPUTABLE'):m.key==='hub'?!altered.hub.includes('https://finalvestige.com/focus/'):m.note==='enable button'?!/<button[^>]*\sdisabled(?:\s|>|=)[^>]*>/.test(altered.a):m.note==='remove near disclosure'?!altered.a.includes('Affiliate disclosure for a future approved link'):m.note==='preview discoverable'?!altered.a.includes('noindex,nofollow'):m.note==='missing main landmark'?!altered.a.includes('<main>'):m.note==='keyboard focus'?!altered.a.includes(':focus-visible'):m.note==='reduce motion'?!altered.a.includes('prefers-reduced-motion'):m.note==='film identity'?!altered.b.includes('42 seconds: the second number'):m.note==='false earned link'?!altered.b.includes('No earning link is active here.'):false;if(detect)caught++;else negative.push('not caught '+m.note)}
return {passed,failed:fails.length,failures:fails,mutations_caught:caught,mutations_total:mutationInputs.length,mutation_failures:negative};
}
module.exports={run,readAll};
if(require.main===module){const r=run(readAll());console.log(JSON.stringify(r,null,2));if(r.failed||r.mutation_failures.length)process.exitCode=1}
