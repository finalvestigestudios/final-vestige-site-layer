/* FV Mind R198 — reproducible source-level QA, no production writes.
 * Native execution from repo root:
 *   node mind/r198/test_mind_r198.cjs
 * Programmatic: require('./mind/r198/test_mind_r198.cjs').run({article,hub,claims,plan,A,B})
 * Results are SOURCE-LEVEL checks, not browser/merchant/Jetpack or live conversion proofs.
 */
'use strict';
const PATHS={
 article:'mind/r198/the-beat-between-two-ears-BINAURAL-EVIDENCE-INVESTIGATION-UNPUBLISHED.md',
 hub:'mind/r198/mind-four-stream-binaural-WORDPRESS-DRAFT-UNPUBLISHED.html',
 claims:'mind/r198/BINAURAL-ZEN12-SOURCE-CLAIM-COMMERCE-GATES.json',
 plan:'mind/r198/ONE-AUTHORIZED-OFFER-PRIVACY-SAFE-NET-REVENUE-TEST.md',
 A:'mind/r188/zen12-variant-A-independent-text-UNPUBLISHED.html',
 B:'mind/r188/zen12-variant-B-optional-42s-storyboard-UNPUBLISHED.html'
};
function run(d){
 const failures=[];let checks=0;
 function check(v,msg){checks++;if(!v)failures.push(msg)}
 for(const k of Object.keys(PATHS)) check(typeof d[k]==='string' && d[k].length>300,'missing '+k);
 const a=d.article||'', h=d.hub||'',p=d.plan||'',A=d.A||'',B=d.B||'';
 let j={};try{j=JSON.parse(d.claims)}catch(e){check(false,'JSON decode')}
 check(a.trim().split(/\s+/).length>=2000,'substantive article');
 check(a.includes('ORIGINAL INVESTIGATION')&&a.includes('UNPUBLISHED'),'editorial release label');
 for(const s of ['The sound that isn\'t in either ear','mechanism','2019','2023','2024','Puységur','fourteen published','five','eight','one had mixed results','NO affiliate links'])check(a.toLowerCase().includes(s.toLowerCase()),'article scope '+s);
 for(const url of ['https://pubmed.ncbi.nlm.nih.gov/37205669/','https://pubmed.ncbi.nlm.nih.gov/30073406/','https://pubmed.ncbi.nlm.nih.gov/35842538/','https://pubmed.ncbi.nlm.nih.gov/38458383/']) check(a.includes(url),'research source '+url);
 check(a.includes('https://finalvestige.com/focus/'),'existing Focus route');
 check(a.includes('https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'),'historical source bridge');
 check(!/we (personally|used|purchased|tested) Zen12/i.test(a),'no invented experience');
 check(!/https:\/\/(?:www\.)?(?:awin1\.com|clickbank\.com|affiliates\.inspire3\.com)\//i.test(a),'investigation has no earning links');
 check(!/guaranteed (cure|focus|treatment|wealth|health)/i.test(a),'no guaranteed benefit');
 check(/<!doctype html>/i.test(h)&&/<html lang="en">/.test(h),'HTML document semantics');
 check(h.includes('noindex,nofollow'),'unpublished noindex');
 check(h.includes('strict-origin-when-cross-origin'),'privacy referrer policy');
 check(/<main id="main"/.test(h)&&/href="#main"/.test(h),'working skip target');
 check((h.match(/<h1\b/g)||[]).length===1,'one H1');
 for(const id of ['perception','suggestion','practice','tools'])check(h.includes('id="'+id+'"'),'4 stream '+id);
 const ids=[...h.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);
 check(ids.length===new Set(ids).size,'unique ids');
 const frags=[...h.matchAll(/href="#([^"]+)"/g)].map(m=>m[1]);check(frags.every(x=>ids.includes(x)),'fragment IDs exist');
 check(!/<script\b|<form\b|<iframe\b|<video\b|<input\b/i.test(h),'no script/form/iframe/autoplay asset');
 check(/<button[^>]*\sdisabled(?:\s|>)/i.test(h),'native disabled button');
 check(/aria-disabled="true"/.test(h)&&/aria-describedby="merchant-hold"/.test(h),'ARIA native state and reason');
 check(h.indexOf('may earn a commission')>=0 && h.indexOf('may earn a commission')<h.indexOf('<button type="button"'),'adjacent prospective disclosure');
 check(!/href="https?:\/\/(?:www\.)?(?:awin1|clickbank|affiliates\.inspire3)\./i.test(h),'no affiliate URL');
 check(h.includes('https://zen12.com/hnp')&&h.includes('non-affiliate'),'exact seller page informational');
 check(h.includes('https://finalvestige.com/focus/'),'one existing Focus path');
 check(h.includes('https://finalvestige.com/2026/11/02/mesmerism/'),'published Mesmerism canonical');
 check(h.includes('https://finalvestige.com/2026/11/02/change-blindness/'),'published Change Blindness canonical');
 check(h.includes('https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'),'Puységur link');
 check(!/href="https:\/\/finalvestige\.com\/mind\/the-beat/.test(h),'unpublished article no public link');
 check(h.includes('prefers-reduced-motion')&&h.includes('forced-colors:active')&&h.includes('focus-visible'),'CSS accommodation');
 check(h.includes('max-width:780px')&&h.includes('max-width:400px'),'mobile CSS breakpoints present');
 check(j.affiliate_earning_url===null&&j.authoritative_affiliate_approval===null,'no invented affiliate approval');
 check(j.owned_payhip_mind_sku===null&&j.actual_paid_orders===null,'no invented purchase or SKU');
 check(j.confirmed_jetpack_leads===null,'no invented subscriber confirmations');
 check(j.net_revenue_per_1000_qualified_humans==='NOT_COMPUTABLE','not zero KPI');
 check(Array.isArray(j.sources)&&j.sources.length>=18,'source register size');
 check(Array.isArray(j.claims)&&j.claims.length>=25,'claim matrix size');
 check(Array.isArray(j.release_gates)&&j.release_gates.length>=20,'release gate size');
 const sids=j.sources.map(s=>s.id);check(sids.length===new Set(sids).size,'unique sources');
 check(j.sources.every(s=>/^https:\/\//.test(s.url)),'full source links');
 check(j.claims.every(c=>c.source_ids?.length && c.source_ids.every(s=>sids.includes(s))),'every claim has valid source');
 check(j.release_gates.every(g=>g.status==='OPEN'),'all gates remain open');
 const cs=Object.fromEntries(j.claims.map(c=>[c.id,c]));
 for(const id of ['zen_equiv','zen_health','brainwave_shots','hypnosis_live'])check(/UNSUBSTANTIATED/.test(cs[id]?.decision||''),'unsubstantiated branded claims '+id);
 for(const id of ['publisher','affiliate_url','owned_sku','paid_orders','focus_lead'])check(Boolean(cs[id]),'conversion integrity claim '+id);
 check(p.includes('qualified_human_session')&&p.includes('merchant_confirmed_paid_order')&&p.includes('received_affiliate_commission'),'separate revenue events');
 check(p.includes('affiliate_click')&&p.includes('confirmed_jetpack_lead'),'clicks not lead or sales');
 check(p.includes('1000 × realized_net_revenue / qualified_human_sessions'),'net per 1000 formula');
 check(p.includes('NOT COMPUTABLE')&&!p.includes('CONVERSION ACHIEVED'),'non-fictional performance');
 check(p.includes('360 / 390 / 768 / 1440 / 1920'),'responsive test plan');
 check(p.includes('7 and 30 days'),'cohort report timing');
 check(p.includes('Grok owns')&&p.includes('Claude owns')&&p.includes('Dispatch #174 owns'),'owner segmentation');
 check(p.includes('A/B')&&p.includes('42-second')&&p.includes('UNRENDERED')===false,'hypothesis and storyboard concept');
 check(p.includes('No genuine A/B traffic')||p.includes('No film has been rendered'),'no fake video metrics');
 for(const [label,s] of [['A',A],['B',B]]){
  check(/<button[^>]*\sdisabled(?:\s|>)/i.test(s),label+' natively disabled');
  check(s.includes('may earn a commission'),label+' disclosure');
  check(!/<script\b/i.test(s),label+' no scripts');
  check(!/<video\b[^>]*autoplay/i.test(s),label+' no forced autoplay');
 }
 check(B.includes('42-second')&&B.includes('transcript'),'42sec B storyboard/transcript');
 return {pass:failures.length===0,assertions:checks,failures};
}
function negativeMutations(d){
 const examples=[
 ['remove_disclosure',x=>({...x,hub:x.hub.replace('may earn a commission','may receive something')})],
 ['activate_purchasing',x=>({...x,hub:x.hub.replace(/(<button[^>]*?)\sdisabled\s/, '$1 ')})],
 ['inject_form',x=>({...x,hub:x.hub.replace('</main>','<form method="post"></form></main>')})],
 ['inject_script',x=>({...x,hub:x.hub.replace('</body>','<script src="https://example.com/track.js"></script></body>')})],
 ['insert_earning_link',x=>({...x,hub:x.hub.replace('https://zen12.com/hnp','https://awin1.com/cread.php?x=1')})],
 ['delete_source',x=>({...x,article:x.article.replace('https://pubmed.ncbi.nlm.nih.gov/37205669/','https://none.invalid/')})],
 ['invent_affiliate',x=>({...x,claims:x.claims.replace('"affiliate_earning_url": null','"affiliate_earning_url": "https://example.com/earning"')})],
 ['fabricate_paid',x=>({...x,claims:x.claims.replace('"actual_paid_orders": null','"actual_paid_orders": 12')})],
 ['gate_open',x=>({...x,claims:x.claims.replace('"status": "OPEN"','"status": "CLOSED"')})],
 ['remove_Focus',x=>({...x,hub:x.hub.replace('https://finalvestige.com/focus/','https://example.org/other-optin')})],
 ['delete_quiet',x=>({...x,hub:x.hub.replace('prefers-reduced-motion','prefers-animated-motion')})],
 ['strip_noindex',x=>({...x,hub:x.hub.replace('noindex,nofollow','index,follow')})],
 ['alter_H1',x=>({...x,hub:x.hub.replace('<h1>','<h2>')})],
 ['fake_subscriber',x=>({...x,claims:x.claims.replace('"confirmed_jetpack_leads": null','"confirmed_jetpack_leads": 200')})],
 ['remove_privacy',x=>({...x,hub:x.hub.replace('strict-origin-when-cross-origin','unsafe-url')})]
 ];
 const failures=[];for(const [name,mutate] of examples){if(run(mutate(d)).pass)failures.push(name)}
 return {total:examples.length,detected:examples.length-failures.length,missed:failures};
}
module.exports={run,negativeMutations,paths:PATHS};
if(typeof require==='function'&&require.main===module){
 const fs=require('fs'),path=require('path'),d={};for(const [k,p] of Object.entries(PATHS)){d[k]=fs.readFileSync(path.resolve(process.cwd(),p),'utf8')}
 const result=run(d),negative=negativeMutations(d);
 console.log(JSON.stringify({result,negative},null,2));
 if(!result.pass||negative.missed.length)process.exitCode=1;
}
