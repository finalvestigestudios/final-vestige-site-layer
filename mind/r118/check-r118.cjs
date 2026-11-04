'use strict';
/**
 * R118 reproducible offline / no network / no customer-data test.
 * Native: node mind/r118/check-r118.cjs  (from repository root)
 * Alternative: require('./check-r118.cjs')(files) with source strings.
 * Tests are intentionally source/contract checks; NOT browser WCAG, CI or purchases.
 */
const paths = Object.freeze({
  article:'mind/r118/the-paragraph-you-read-without-seeing.md',
  plan:'mind/r118/one-offer-commerce-acceptance.md',
  evidence:'mind/r118/claims-and-conversion-gates.json',
  panel:'mind/r118/zen12-conditional-decision.fragment.html',
  existingA:'mind/r114/zen12-text-A.html',
  existingB:'mind/r114/zen12-film-B.html',
  captions:'mind/r114/film-40s.vtt',
  priorKpi:'mind/r114/revenue-math.cjs'
});
function checkAll(files){
  const a=files[paths.article],p=files[paths.plan],j=JSON.parse(files[paths.evidence]),h=files[paths.panel],
    A=files[paths.existingA],B=files[paths.existingB],vtt=files[paths.captions],kpi=files[paths.priorKpi];
  const cases=[];
  function check(label,fn){try{if(!fn())throw Error('assertion false');cases.push({label,pass:true})}catch(e){cases.push({label,pass:false,error:String(e.message||e)})}}
  check('original article has meaningful length',()=>a.trim().split(/\s+/).length>=1800);
  check('article is unpublished editorial only',()=>a.includes('UNPUBLISHED EDITORIAL DRAFT')&&a.includes('no product recommendation or purchase offer'));
  check('article contains original free reflection',()=>a.includes('free field observation')&&a.includes('not a validated psychological instrument'));
  check('article cites original experience sampling',()=>a.includes('10.1126/science.1192439'));
  check('article cites independent review',()=>a.includes('annurev-psych-010814-015331'));
  check('article cites RCT with limitation',()=>a.includes('23538911/')&&a.includes('They did not simply purchase'));
  check('article marks merchant benefits unproven',()=>a.includes('did not establish Zen12-specific effects')&&a.includes('hour of advanced meditation'));
  check('article links existing Focus only as optional',()=>a.includes('https://finalvestige.com/focus/')&&a.includes('no need to subscribe'));
  check('plan chooses one actual merchant product',()=>p.includes('https://zen12.com/hnp')&&p.includes('Zen12 Premium'));
  check('plan explicitly rejects invented paid FV product',()=>p.includes('No Payhip seller-dashboard connector')&&p.includes('NOT VERIFIED'));
  check('plan buyer privacy requires permission',()=>p.includes('aggregate-only data arrangement')&&p.includes('buyer PII'));
  check('plan has seven and thirty-day cohorts',()=>p.includes('7-day')&&p.includes('30-day'));
  check('plan has creator-to-article three topics',()=>['Change blindness','Attentional blink','Mesmer & Puységur'].every(x=>p.includes(x)));
  check('plan distinguishes outbound from sales',()=>p.includes('merchant_confirmed_affiliate_sale')&&p.includes('affiliate_outbound'));
  check('evidence has official/FTC/independent sources',()=>j.sources.length>=12&&j.sources.some(x=>x.url.includes('ftc.gov'))&&j.sources.some(x=>x.url.includes('pubmed.ncbi.nlm.nih.gov')));
  check('at least fifteen explicit claim decisions',()=>j.claims.length>=15);
  check('seller efficacy withheld',()=>j.claims.filter(x=>x.status.includes('WITHHOLD')).length>=2);
  check('merchant privacy risk documented',()=>j.claims.some(x=>x.text.includes('purchaser names/emails')));
  check('partner acceptance and earning URL still absent',()=>j.partner_acceptance_document===null&&j.affiliate_earning_url===null&&!j.offer_verified_for_paid_conversion);
  check('all gated decisions explicitly fail closed',()=>j.release_gates.length>=15&&j.release_gates.every(g=>g.passed===false));
  check('creator IDs are never fabricated',()=>j.creator_to_offer.length===3&&j.creator_to_offer.every(x=>x.asset_id===null));
  check('revenue values unknown, never synthetic actual',()=>j.confirmed_paid_orders===null&&j.settled_commissions===null&&j.net_revenue_per_1000===null);
  check('no duplicate tracking injected',()=>j.attribution.create_tracking_script===false&&j.attribution.personally_identifying_fields.length===0);
  check('panel has a discernible section heading',()=>h.includes('aria-labelledby="fv-mind-decision-title"')&&h.includes('<h2 id="fv-mind-decision-title">'));
  check('conditional purchase control disabled',()=>/\<button[^>]*disabled/.test(h));
  check('prospective commission disclosure adjacent',()=>h.includes('may earn a commission at no additional cost')&&h.indexOf('fv-mind-commercial-disclosure')<h.indexOf('<button'));
  check('no active merchant link in panel',()=>!/<a\b[^>]*href=["'][^"']*(zen12|inspire3|hypnosislive|brainwaveshots)/i.test(h));
  check('only internal free signup, no extra form',()=>h.includes('href="/focus/"')&&!/<form\b|<input\b/i.test(h));
  check('no external players/JS/tracking',()=>!/<script\b|<iframe\b|<video\b|<audio\b|autoplay\b|<img\b[^>]*pixel/i.test(h));
  check('keyboard and reduced-motion styles present',()=>h.includes(':focus-visible')&&h.includes('prefers-reduced-motion'));
  check('existing R114 A and B are still draft',()=>A.includes('noindex,nofollow')&&B.includes('noindex,nofollow'));
  check('existing R114 A and B no live purchase activation',()=>A.includes('disabled')&&B.includes('disabled'));
  check('optional film captions run through 40 sec',()=>vtt.includes('WEBVTT')&&vtt.includes('00:00:40.000'));
  check('reuse existing offline revenue logic not duplicate script',()=>kpi.includes('ALLOWED_EVENTS')&&kpi.includes('validateSafeEvent'));
  check('canonical R114 guide referenced, not superseded',()=>j.canonical_existing_guide==='mind/r114/zen12-canonical-decision-guide.md');
  return {total:cases.length,passed:cases.filter(x=>x.pass).length,failed:cases.filter(x=>!x.pass),cases};
}
module.exports=checkAll;
if(typeof require!=='undefined'&&require.main===module){
  const fs=require('node:fs');
  const files={};
  for(const path of Object.values(paths))files[path]=fs.readFileSync(path,'utf8');
  const result=checkAll(files);
  for(const check of result.cases)console.log((check.pass?'PASS ':'FAIL ')+check.label+(check.error?': '+check.error:''));
  console.log(result.passed+'/'+result.total+' passed; source-contract tests only');
  if(result.failed.length)process.exitCode=1;
}
