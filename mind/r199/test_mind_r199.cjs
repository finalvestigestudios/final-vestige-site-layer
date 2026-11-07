'use strict';
/**
 * Final Vestige Mind R199 reproducible source-level QA.
 * Native usage from repo root:
 *   node mind/r199/test_mind_r199.cjs
 * No HTTP calls, no CMS writes, no merchant activation.
 * These checks do NOT replace real-browser/mobile/Lighthouse/merchant QA.
 */
const paths={
 article:'mind/r199/the-thought-that-left-the-room-MIND-WANDERING-INVESTIGATION-UNPUBLISHED.md',
 hub:'mind/r199/mind-archive-FOUR-STREAM-UNPUBLISHED.html',
 a:'mind/r199/zen12-offer-guide-A-TEXT-UNPUBLISHED.html',
 b:'mind/r199/zen12-offer-guide-B-OPTIONAL-FILM-UNPUBLISHED.html',
 matrix:'mind/r199/MIND-WANDERING-ZEN12-SOURCE-CLAIM-MERCHANT-GATES.json',
 plan:'mind/r199/OFFER-FIRST-CREATOR-FIT-AB-PAID-REVENUE-ACCEPTANCE.md',
 r197:'mind/r197/the-syllable-you-heard-with-your-eyes-MCGURK-INVESTIGATION-UNPUBLISHED.md',
 r197ledger:'mind/r197/MCGURK-ZEN12-COMMERCE-CLAIMS-SOURCE-GATES.json',
 r198:'mind/r198/the-beat-between-two-ears-BINAURAL-EVIDENCE-INVESTIGATION-UNPUBLISHED.md',
 r198ledger:'mind/r198/BINAURAL-ZEN12-SOURCE-CLAIM-COMMERCE-GATES.json'
};
function validate(d){
 const result=[];const check=(ok,name)=>result.push({ok:!!ok,name});
 let j;try{j=JSON.parse(d.matrix)}catch(e){return {ok:false,passes:0,failures:[{name:'parse matrix',error:String(e)}],checks:[]}};
 const links=new Set(j.sources.map(s=>s.id));
 const plain=h=>h.replace(/<[^>]+>/g,' ');
 const filmRemoved=d.b.replace(/<section class="film panel"[\s\S]*?<\/section>/,'');
 const flat=s=>s.replace(/\s+/g,'');
 const htmls=[d.hub,d.a,d.b];
 check(d.article.split(/\s+/).length>1900,'original long-form investigation');
 check(d.article.includes('Killingsworth')&&d.article.includes('MacLean')&&d.article.includes('Mrazek'),'three named primary studies');
 check(d.article.includes('30 people')&&d.article.includes('five hours daily for three months'),'primary-study exposure precision');
 check(d.article.includes('not a blinded randomized trial'),'free exercise has proper limitations');
 check(d.article.includes('no active affiliate recommendation')||d.article.includes('no active affiliate recommendation'.toUpperCase())||d.article.includes('**There is no active affiliate recommendation'),'independent article contains no endorsement');
 check(!/https:\/\/www\.awin1\.com|affiliate\.ref|\bmy experience with Zen12\b/i.test(d.article),'no fabricated affiliate experience or URL');
 check(d.article.includes('https://finalvestige.com/focus/'),'one established free Focus funnel');
 check(d.article.includes('https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'),'historical archive bridge');
 check(d.hub.includes('id="attention"')&&d.hub.includes('id="history"')&&d.hub.includes('id="practice"')&&d.hub.includes('id="tools"'),'four-stream archive');
 check(d.hub.includes('noindex,nofollow')&&d.a.includes('noindex,nofollow')&&d.b.includes('noindex,nofollow'),'all prototypes excluded from indexing');
 check(htmls.every(h=>!/<script\b|<form\b|<iframe\b|<video\b|<audio\b/i.test(h)),'no scripts, new forms, embeds or media players');
 check(htmls.every(h=>!/\bonclick\s*=|\bonload\s*=|javascript:/i.test(h)),'no event handlers or javascript URLs');
 check(htmls.every(h=>!/<a[^>]*href=["'][^"']*(?:zen12\.com|affiliates\.inspire3\.com|awin1\.com)/i.test(h)),'no commercial outbound link');
 check(htmls.every(h=>!/<link[^>]*rel=["']stylesheet|@import|@font-face/i.test(h)),'no external fonts/styles');
 check(htmls.every(h=>/max-width:750px/.test(h)&&/max-width:390px/.test(h)),'source responsive breakpoints');
 check(htmls.every(h=>/prefers-reduced-motion:reduce/.test(h)),'reduced motion');
 check(htmls.every(h=>/focus-visible/.test(h)),'keyboard focus visible');
 check(htmls.every(h=>/class="hold"[^>]*\bdisabled\b/.test(h)||/type="button" class="hold" disabled/.test(h)),'native disabled controls');
 check(htmls.every(h=>h.includes('aria-disabled="true"')),'aria-disabled supplemental semantics');
 check(htmls.every(h=>h.includes('may earn a commission')),'disclosure on each commercial preview');
 check(htmls.every(h=>h.indexOf('may earn a commission')<h.lastIndexOf('</button>')),'disclosure ahead of CTA');
 check(htmls.every(h=>h.includes('https://finalvestige.com/focus/')),'single Focus path only');
 check(htmls.every(h=>!/(guaranteed cure|proven to rewire|guaranteed sales|sale confirmed)/i.test(plain(h))),'no prohibited seller-style outcome guarantees');
 check(d.a.includes('$87.99')&&d.a.includes('not a verified final checkout charge'),'seller price identified as unverified checkout');
 check(d.a.includes('one-year money-back guarantee')&&d.a.includes('refund execution'),'seller returns vs actual refund distinguished');
 check(d.a.includes('12 levels')&&d.a.includes('48 MP3'),'actual SKU features');
 check(d.a.includes('twelve minutes of audio')&&d.a.includes('not independently established'),'claim differentiation');
 check(flat(d.a)===flat(filmRemoved),'A/B equivalent outside optional film');
 check(d.b.includes('id="optional-film"')&&d.b.includes('<details>')&&d.b.includes('<summary'),'B optional/no-JS storyboard');
 check(d.b.includes('42-second')&&d.b.includes('00–07 s:')&&d.b.includes('34–42 s:'),'42s transcript timed');
 check(d.b.includes('role="img"')&&d.b.includes('<title id="poster-title"')&&d.b.includes('<desc id="poster-desc"'),'original poster accessible name/description');
 check(d.b.includes('aria-labelledby="poster-title poster-desc"'),'SVG references label and desc');
 check(d.b.includes('WebVTT'),'caption implementation gate specified');
 check(j.affiliate_earning_url===null&&j.authoritative_affiliate_approval===null,'no invented commercial approval');
 check(j.owned_payhip_mind_sku===null&&j.actual_paid_orders===null,'owned SKU and paid orders unknown');
 check(j.confirmed_jetpack_leads===null&&j.qualified_human_sessions===null,'no fabricated subscriber or human data');
 check(j.net_revenue_per_1000_qualified_humans==='NOT_COMPUTABLE','missing denominator not reported zero');
 check(j.sources.length>=19 && j.claims.length>=30 && j.gates.length>=25,'rich evidence and release gates');
 check(j.gates.every(g=>g.passed===false&&g.evidence===null),'no falsely closed commercial gates');
 check(j.claims.every(c=>c.source_ids.every(id=>links.has(id))),'all claim source references resolve');
 check(j.sources.every(s=>/^https:\/\//.test(s.url)),'source links complete');
 check(j.claims.some(c=>c.id==='zen12_equiv'&&c.decision==='EXCLUDE_UNSUBSTANTIATED'),'vendor equivalence claim excluded');
 check(j.claims.some(c=>c.id==='zen12_health'&&c.decision==='EXCLUDE_UNSUBSTANTIATED'),'product health guarantees excluded');
 check(j.claims.some(c=>c.id==='focus_view'&&c.decision==='REJECT_INFERENCE'),'PDF reveal not confirmed signup');
 check(j.claims.some(c=>c.id==='affiliate_outbound'&&c.decision==='REJECT_INFERENCE'),'click not sale');
 check(j.seller_premium_price_observed_usd===87.99 && j.verified_checkout===null,'seller figure not a verified checkout');
 check(d.plan.includes('asset_id')&&d.plan.includes('utm_campaign'),'creator attribution fields');
 check(d.plan.includes('merchant_confirmed_purchase')&&d.plan.includes('merchant_refund_or_reversal'),'independent paid and reversal events');
 check(d.plan.includes('7-day and 30-day')&&d.plan.includes('NOT COMPUTABLE'),'cohorts and missing data');
 check(d.plan.includes('Grok retains')&&d.plan.includes('Dispatch #174'),'owner boundaries');
 check(d.plan.includes('HARD HOLD')&&d.plan.includes('No WordPress'), 'release hold and protected live environment');
 check(d.r197.includes('in quiet listening conditions')&&d.r197.includes('no significant between-group difference in the noisy condition'),'R197 bilingual condition fixed');
 check(d.r197.includes('5.5%')&&d.r197.includes('not a heritability estimate'),'R197 twin inference fixed');
 check(d.r197ledger.includes('NOT heritability')&&d.r197ledger.includes('QUIET'),'R197 ledger aligned');
 check(d.r198.includes('only one evaluated binaural beats')&&d.r198.includes('I² approximately 77%'),'R198 scoped review and heterogeneity');
 check(d.r198ledger.includes('I²≈76.91%')&&d.r198ledger.includes('only ONE'),'R198 ledger aligned');
 check(!d.r198ledger.includes('UNKNOWN_AWAIT_P RAXXIS'),'reviewer typo fixed');
 return {ok:result.every(r=>r.ok),passes:result.filter(r=>r.ok).length,failures:result.filter(r=>!r.ok),checks:result};
}
function mutations(base){
 const cases=[
 ['native A disable', 'a',' disabled aria-disabled="true"',' aria-disabled="true"'],
 ['native B disable', 'b',' disabled aria-disabled="true"',' aria-disabled="true"'],
 ['affiliate link','a','<button type="button"','<a href="https://zen12.com/hnp"'],
 ['merchant approval','matrix','"authoritative_affiliate_approval": null','"authoritative_affiliate_approval": "APPROVED"'],
 ['invented order','matrix','"actual_paid_orders": null','"actual_paid_orders": 5'],
 ['fake lead','matrix','"confirmed_jetpack_leads": null','"confirmed_jetpack_leads": 42'],
 ['revenue zero','matrix','"net_revenue_per_1000_qualified_humans": "NOT_COMPUTABLE"','"net_revenue_per_1000_qualified_humans": 0'],
 ['unsubstantiated claims','matrix','"id": "zen12_equiv"','"id": "zen12_equiv_BAD"'],
 ['removed film','b','id="optional-film"','id="missing-film"'],
 ['missing caption','b','WebVTT','no captions'],
 ['missing poster desc','b','<desc id="poster-desc"','<desc id="other-desc"'],
 ['missing FTC','a','may earn a commission','could perhaps receive something'],
 ['cross-pitch article','article','**There is no active affiliate recommendation','**There is an active affiliate recommendation'],
 ['missing UTM','plan','utm_campaign','track_campaign'],
 ['bad source','matrix','"killingsworth2010"','"not_a_source"'],
 ['lift gate','matrix','"passed": false','"passed": true'],
 ['twin heritability','r197','not a heritability estimate','is a heritability estimate'],
 ['binaural overgeneral','r198','only one evaluated binaural beats','all 31 evaluated binaural beats'],
 ['invalid reviewer typo','r198ledger','UNKNOWN_AWAIT_PRAXXIS','UNKNOWN_AWAIT_P RAXXIS'],
 ['add script','hub','</head>','<script src="https://tracker.example.com/x.js"></script></head>'],
 ['remove Focus','hub','https://finalvestige.com/focus/','https://example.com/new-mailing-list/'],
 ['break CTA disclosure','b','may earn a commission','this link pays us 99 percent']
 ];
 let detected=0,notDetected=[];for(const [label,key,from,to] of cases){
   if(!base[key].includes(from)){notDetected.push(label+':missing mutation target');continue}
   const mutated={...base,[key]:base[key].replace(from,to)};
   if(!validate(mutated).ok)detected++;else notDetected.push(label+':escaped');
 }
 return {count:cases.length,detected,notDetected};
}
module.exports={paths,validate,mutations};
if(typeof require!=='undefined' && require.main===module){
 const fs=require('fs'),path=require('path');const d={};
 for(const [k,v] of Object.entries(paths))d[k]=fs.readFileSync(path.resolve(process.cwd(),v),'utf8');
 const r=validate(d),m=mutations(d);
 console.log('R199 assertions '+r.passes+'/'+r.checks.length,'mutations '+m.detected+'/'+m.count);
 if(r.failures.length)console.log('FAILS',r.failures);
 if(m.notDetected.length)console.log('MISSED MUTANTS',m.notDetected);
 if(!r.ok||m.detected!==m.count)process.exitCode=1;
}
