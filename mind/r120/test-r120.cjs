'use strict';
/* Run natively from repo root:
   node mind/r120/test-r120.cjs
   Pure audit(files) export also permits V8 external source verification without network/PII.
   These are structural tests, NOT live browser WCAG, legal review, merchant acceptance, or revenue proof. */
const paths = Object.freeze({
  article:'mind/r120/the-beat-between-two-notes.md',
  guide:'mind/r120/zen12-one-offer-merchant-decision.md',
  ledger:'mind/r120/claims-offer-release-gates.json',
  panel:'mind/r120/unpublished-zen12-decision-panel.html',
  existingText:'mind/r114/zen12-text-A.html',
  existingVideo:'mind/r114/zen12-film-B.html',
  existingMath:'mind/r114/revenue-math.cjs'
});
function audit(files) {
  const A=files[paths.article],G=files[paths.guide],J=JSON.parse(files[paths.ledger]),H=files[paths.panel],T=files[paths.existingText],V=files[paths.existingVideo],M=files[paths.existingMath];
  const checks=[]; const check=(name,pass)=>checks.push({name,pass:!!pass});
  const citations=['37205669','30073406','17488185','33582570','32739799','29939051'];
  check('article is independently useful >=2000 words',A.trim().split(/\s+/).length>=2000);
  check('article not marked published',/UNPUBLISHED/.test(A));
  check('article distinguishes perception, EEG and outcome',/three kinds of evidence/i.test(A));
  check('article contains noncommercial exercise',/free, deliberately ordinary comparison/i.test(A));
  check('article refuses vendor efficacy attribution',/not test a downloadable twelve-minute audio product/i.test(A));
  for (const id of citations) check('article source PMID '+id,A.includes('pubmed.ncbi.nlm.nih.gov/'+id+'/'));
  check('article notes conflicting behavioral and EEG syntheses',/twenty-two studies/i.test(A)&&/fourteen studies/i.test(A));
  check('article does not contain earning affiliate link',!/href=["'][^"']*(affiliat|ref=|hop=|clickbank)/i.test(A));
  check('guide is substantive >=1200 words',G.trim().split(/\s+/).length>=1200);
  check('guide price divergence unambiguous',G.includes('87.99')&&G.includes('$37')&&/neither should be presented/i.test(G));
  check('guide says exact checkout not verified',/checkout/i.test(G)&&/not independently established/i.test(G));
  check('guide focuses one verified candidate, not activation',G.includes('Zen12 Premium')&&G.includes('Gate CLOSED'));
  check('guide does not claim authenticated Payhip inventory',/authenticated seller-led audit/.test(G));
  check('guide offers 3 creator routes',G.includes('Change blindness')&&G.includes('Mesmerism/Puységur')&&G.includes('brainwave audio'));
  check('guide refuses fake asset IDs',/asset IDs.*UNVERIFIED/.test(G));
  check('guide explicitly separates merchant sale and outbound',G.includes('affiliate_outbound_click')&&G.includes('verified_affiliate_commission'));
  check('guide guards R114 and flagship',G.includes('mind/r114/zen12-text-A.html')&&G.includes('PR #49')&&G.includes('PR #172'));
  check('ledger 15 sources',J.sources.length===15);
  check('ledger 16 claim decisions',J.claims.length===16);
  check('ledger 15 release gates',J.gates.length===15);
  check('all gates remain closed',J.gates.every(x=>x.status==='CLOSED'));
  check('ledger separates product effects from research',J.claims.some(x=>x.id==='C04'&&/PROHIBIT/.test(x.decision)));
  check('ledger denies universal promotional price',J.claims.some(x=>x.id==='C09'&&x.decision==='PROHIBIT'));
  check('ledger product link authorization closed',J.gates.find(x=>x.id==='G03')?.status==='CLOSED');
  check('ledger privacy supplier buyer data risk sourced',J.sources.some(x=>x.url==='https://inspire3.com/privacy/'));
  check('ledger affiliate commissions not clicks',J.conversion_contract.rejected_paid_proxies.includes('affiliate outbound click'));
  check('ledger 7/30 cohorts',JSON.stringify(J.conversion_contract.cohort_days)==='[7,30]');
  check('ledger real Grok media IDs null',J.creator_routes.every(x=>x.actual_asset_id===null));
  check('ledger excludes sensitive identifiers',J.conversion_contract.no_pii.includes('email')&&J.conversion_contract.no_pii.includes('order_id'));
  check('panel viewport mobile baseline',/name="viewport"/i.test(H)&&/@media\(max-width:720px\)/.test(H));
  check('panel no scripts, external players or duplicate signup',!/<script\b|<iframe\b|<form\b/i.test(H));
  check('panel no autoplay',!/<(?:video|audio)\b[^>]*\sautoplay\b/i.test(H));
  check('panel declares noindex',/noindex,nofollow/.test(H));
  check('panel native details disclosure',/<details>/.test(H)&&/<summary>/.test(H));
  check('panel clear prospective commission disclosure',/affiliate disclosure:/i.test(H)&&/may earn a commission at no additional cost/.test(H));
  check('panel disclosure adjacent to disabled purchase',H.indexOf('Prospective affiliate disclosure:')>0&&H.indexOf('Prospective affiliate disclosure:')<H.indexOf('Purchasing unavailable pending partner verification'));
  check('panel purchasing button disabled',/<button\b[^>]*disabled[^>]*>Purchasing unavailable pending partner verification<\/button>/.test(H));
  check('panel actual affiliate earning URL not present',!/(?:hop\.clickbank|awin1\.com|clickbank\.net|referral_code|aff_id=|affiliate_id=)/i.test(H));
  check('panel withholds clickable merchant purchase or offer href', !H.includes('href="https://zen12.com/') && !H.includes("href='https://zen12.com/"));
  check('panel first-party Focus link rather than new form',/href="https:\/\/finalvestige\.com\/focus\/"/.test(H));
  check('panel references seller privacy and terms',H.includes('https://inspire3.com/privacy/')&&H.includes('https://inspire3.com/terms/'));
  check('panel has skip link and visible focus',H.includes('class="skip"')&&H.includes(':focus-visible'));
  check('panel reduced-motion and forced-colors fallbacks',H.includes('prefers-reduced-motion')&&H.includes('forced-colors'));
  check('existing A and B retained',T.includes('UNPUBLISHED')&&V.includes('UNPUBLISHED'));
  check('existing A and B both no active direct earning link',![T,V].some(x=>/(?:hop\.clickbank|awin1\.com|affiliate_id=)/.test(x)));
  check('existing B is only optional storyboard and no autoplay',/forty|40-second|transcript|Transcript/i.test(V)&&!/<(?:video|audio)\b[^>]*\sautoplay\b/i.test(V));
  check('existing revenue math enforces verified attribution',M.includes("cohort.attribution!=='verified'")&&M.includes("source_proof!=='merchant_reconciled_and_firstparty_qualified'"));
  return {total:checks.length, passed:checks.filter(x=>x.pass).length, failed:checks.filter(x=>!x.pass).map(x=>x.name),checks};
}
if (typeof module !== 'undefined' && module.exports) module.exports={audit,paths};
if (typeof require !== 'undefined' && typeof module !== 'undefined' && require.main===module) {
  const fs=require('node:fs'); const all={};
  for(const p of Object.values(paths))all[p]=fs.readFileSync(p,'utf8');
  const result=audit(all);
  for(const t of result.checks)console.log((t.pass?'PASS':'FAIL')+'  '+t.name);
  console.log(result.passed+'/'+result.total+' passed');
  if(result.failed.length)process.exitCode=1;
}
