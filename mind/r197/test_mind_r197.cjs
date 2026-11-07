/* Final Vestige Mind R197: SOURCE-LEVEL ONLY regression checks.
 * Node: node mind/r197/test_mind_r197.cjs from repo root.
 * Unit harness: require('./mind/r197/test_mind_r197.cjs').run({article,hub,claims,plan,r196_article,r196_ledger,A,B})
 * This does NOT replace actual browser, consent, checkout, subscriber, or payout tests.
 */
'use strict';
const fs=typeof require!=='undefined'?require('fs'):null;
const path=typeof require!=='undefined'?require('path'):null;
const P={
 article:'mind/r197/the-syllable-you-heard-with-your-eyes-MCGURK-INVESTIGATION-UNPUBLISHED.md',
 hub:'mind/r197/mind-four-stream-MCGURK-WORDPRESS-DRAFT-UNPUBLISHED.html',
 claims:'mind/r197/MCGURK-ZEN12-COMMERCE-CLAIMS-SOURCE-GATES.json',
 plan:'mind/r197/ONE-OFFER-MCGURK-ZEN12-AB-VERIFIED-PAID-ACCEPTANCE.md',
 r196_article:'mind/r196/the-second-target-that-vanished-ATTENTIONAL-BLINK-UNPUBLISHED.md',
 r196_ledger:'mind/r196/ATTENTIONAL-BLINK-SOURCES-PRODUCT-PERMISSIONS-REVENUE-GATES.json',
 A:'mind/r188/zen12-variant-A-independent-text-UNPUBLISHED.html',
 B:'mind/r188/zen12-variant-B-optional-42s-storyboard-UNPUBLISHED.html'
};
function run(d){
 let count=0,fail=[];const check=(ok,message)=>{count++;if(!ok)fail.push(message)};
 for(const k of Object.keys(P))check(typeof d[k]==='string'&&d[k].length>100,'missing '+k);
 const a=d.article||'',h=d.hub||'',p=d.plan||'',r=d.r196_article||'',v=d.r196_ledger||'',A=d.A||'',B=d.B||'';
 let j={sources:[],claims:[],release_gates:[]};
 try{j=JSON.parse(d.claims)}catch(e){check(false,'invalid JSON')}
 let jr={sources:[],claims:[]};try{jr=JSON.parse(v)}catch(e){check(false,'invalid inherited JSON')}
 check(a.length>13000,'article depth below baseline');
 check(a.includes('ORIGINAL INVESTIGATION')&&a.includes('UNPUBLISHED'),'article labelled draft');
 check(/McGurk.*1976|1976.*McGurk/s.test(a),'original study described');
 check(a.includes('ba')&&a.includes('ga')&&a.includes('da'),'three phonemes described');
 check(a.includes('https://doi.org/10.1038/264746a0'),'primary original link');
 check(a.includes('https://pubmed.ncbi.nlm.nih.gov/30418995/'),'Brown study cited');
 check(a.includes('https://doi.org/10.3389/fnins.2019.01029'),'twin study cited');
 check(a.includes('https://pmc.ncbi.nlm.nih.gov/articles/PMC5977076/'),'language study cited');
 check(a.includes('324')&&a.includes('5.5%'),'twin limitations present');
 check(/NOT.*working McGurk|not a working audiovisual|not a working audiovisual test/i.test(a),'avoid false interactive demo');
 check(/not.*Zen12|not test.*Zen12/i.test(a),'science not product proof');
 check(a.includes('https://finalvestige.com/focus/'),'single Focus CTA in article');
 check(!/\b(?:affiliate.*purchase link).*https?:\/\/.*(?:awin|cread\.php)/i.test(a),'no earning link in investigation');
 check(/NO affiliate|no affiliate/i.test(a),'editorial firewall in article');
 check(!/\bwe (?:guarantee|promise) (?:clinical|medical|wealth|health) (?:benefits|results|effects)/i.test(a),'no medical or wealth guarantees');
 check(/<!doctype html>/i.test(h)&&/<html lang="en">/i.test(h),'semantic HTML');
 check(h.includes('noindex,nofollow'),'unpublished meta noindex');
 check(h.includes('strict-origin-when-cross-origin'),'referrer policy meta');
 check(!/<script\b|<form\b|<iframe\b|<video\b/i.test(h),'no scripts, forms, remote video');
 check(!/autoplay|window\.location|addEventListener\(/i.test(h),'no autoplay or scripted navigation');
 check(h.includes('href="#main"')&&h.includes('id="main"'),'working skip link');
 check((h.match(/<nav\b/g)||[]).length===1,'one labelled nav');
 check((h.match(/<h1\b/g)||[]).length===1,'one h1');
 check((h.match(/<section\b/g)||[]).length>=5,'four streams plus method');
 for(const id of ['perception','suggestion','practice','tools'])check(h.includes('id="'+id+'"'),'archive stream '+id);
 const allids=[...h.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);check(new Set(allids).size===allids.length,'unique HTML IDs');
 const hrefs=[...h.matchAll(/href="#([^"]+)"/g)].map(m=>m[1]);check(hrefs.every(id=>allids.includes(id)),'all fragment links resolve');
 check(/\bdisabled(?:\s|>)/.test(h)&&/button type="button" disabled/.test(h),'native disabled merchant button');
 check(!/href="https?:\/\/(?:www\.)?(?:awin1|clickbank|affiliates\.inspire3)\./.test(h),'no earning network URL');
 check(h.includes('non-affiliate link')||h.includes('non-affiliate'),'seller link labelled informational');
 check(h.includes('https://zen12.com/hnp'),'exact seller public page');
 check(h.includes('may earn a commission at no additional cost to you'),'clear adjacent disclosure');
 check(h.indexOf('may earn a commission')<h.indexOf('<button type="button" disabled'),'disclosure above merchant button');
 check(h.includes('id="merchant-hold"')&&h.includes('aria-describedby="merchant-hold"'),'button condition explained via ARIA reference');
 check(h.includes('prefers-reduced-motion')&&h.includes('forced-colors:active'),'motion and forced color CSS');
 check(h.includes('focus-visible')&&h.includes('@media(max-width:700px)'),'keyboard and responsive styling');
 check(h.includes('audio')&&h.includes('filmed')&&h.includes('Possible report'),'conceptual demo labels');
 check(h.includes('not a working')||h.includes('NOT a working'),'no phantom McGurk demonstration');
 check(h.includes('https://finalvestige.com/2026/11/02/change-blindness/'),'existing published change link');
 check(h.includes('https://finalvestige.com/2026/11/02/mesmerism/'),'existing published Mesmerism link');
 check(h.includes('https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'),'Puységur historical archive link');
 check(h.includes('https://finalvestige.com/focus/'),'one existing Focus path');
 check(!/\/mind\/mcgurk-effect-hearing-lips\//.test(h),'unpublished slug not publicly linked');
 check(j.affiliate_earning_url===null&&j.authoritative_affiliate_approval===null,'no invented publisher approval/link');
 check(j.owned_payhip_mind_sku===null&&j.actual_paid_orders===null,'no invented SKU or paid orders');
 check(j.net_revenue_per_1000_qualified_humans==='NOT_COMPUTABLE','revenue not zero');
 check(Array.isArray(j.sources)&&j.sources.length>=20,'deep source register');
 check(Array.isArray(j.claims)&&j.claims.length>=28,'claim coverage');
 check(Array.isArray(j.release_gates)&&j.release_gates.length>=20,'release gates');
 const ids=j.sources.map(x=>x.id);check(new Set(ids).size===ids.length,'unique source IDs');
 check(j.sources.every(x=>/^https:\/\//.test(x.url)),'all source links full https');
 check(j.claims.every(x=>x.source_ids?.length&&x.source_ids.every(s=>ids.includes(s))),'all claim-to-source references resolvable');
 check(j.release_gates.every(x=>x.status==='OPEN'),'no unverified gate closed');
 const claimById=Object.fromEntries(j.claims.map(x=>[x.id,x]));
 for(const k of ['zen_equiv','zen_health','hyp_focus'])check(claimById[k]?.decision.includes('UNSUBSTANTIATED'),'seller efficacy claim withheld '+k);
 for(const k of ['publisher','paidsku','focus_landing','jetpack_confirm'])check(!!claimById[k],'conversion proof claim '+k);
 check(p.includes('qualified_human_session')&&p.includes('merchant_confirmed_paid_order'),'separate person vs purchase funnel');
 check(p.includes('received_affiliate_commission')&&p.includes('affiliate_click'),'affiliate outbound separate from payout');
 check(p.includes('NOT COMPUTABLE')&&p.includes('1000 × realized_net_revenue'),'proper net KPI');
 check(p.includes('7 and 30 days')||p.includes('7 and 30'),'7/30 cohorts');
 check(p.includes('one and only one existing Focus')||p.includes('single existing'),'no duplicated nurture');
 check(p.includes('A/B hypothesis')||p.includes('A/B'),'A/B experiment preregistered');
 check(p.includes('360/390/768/1440'),'responsive test cases');
 check(p.includes('Grok owns')&&p.includes('Claude owns'),'owner segregation');
 check(p.includes('No genuine A/B traffic')||p.includes('no genuine A/B traffic'),'no traffic falsely claimed');
 check(r.includes('17 experienced meditators')&&r.includes('23 meditation-naïve controls'),'Slagter group precision');
 check(r.includes('10–12 hours')&&r.includes('not randomly assigned'),'Slagter intensity and nonrandom design');
 check(jr.sources?.some(x=>x.id==='grassi2021'),'two-replication primary source added');
 check(jr.sources?.some(x=>x.id==='chun1995'&&/7 experiments/.test(x.note)),'Chun 7 experiments corrected');
 check(jr.sources?.some(x=>x.id==='slagter2007'&&/nonrandom/.test(x.note)),'Slagter ledger corrected');
 for(const [n,v] of [['A',A],['B',B]]){check(/<button[^>]*\sdisabled(?:\s|>)/i.test(v),n+' native disabled');check(v.includes('may earn a commission'),n+' disclosure');check(!/<script\b/i.test(v),n+' no script')}
 check(B.includes('42-second')||B.includes('42 seconds')||B.includes('0:42'),'B optional 42-sec storyboard');
 check(!/<video\b[^>]*autoplay/i.test(B),'B no forced autoplay');
 return {pass:fail.length===0,assertions:count,failures:fail};
}
module.exports={run,paths:P};
if(typeof require==='function'&&require.main===module){const d={};for(const [k,p] of Object.entries(P))d[k]=fs.readFileSync(path.resolve(process.cwd(),p),'utf8');const result=run(d);console.log(JSON.stringify(result,null,2));if(!result.pass)process.exitCode=1}