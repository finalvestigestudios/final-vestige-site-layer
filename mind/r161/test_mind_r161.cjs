'use strict';
// Execute from repository root: node mind/r161/test_mind_r161.cjs
// Pure source-contract test; NOT a browser, merchant, scientific replication or checkout test.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const here = __dirname;
const paths = Object.freeze({
  article: 'the-moment-you-noticed-your-mind-was-gone-investigation.md',
  html: 'zen12-premium-mind-wandering-presell-UNPUBLISHED.html',
  evidence: 'source-claim-permission-and-commerce-gates.json',
  plan: 'creator-offer-funnel-and-controlled-test-contract.md'
});
function load() {
  return Object.fromEntries(Object.entries(paths).map(([key,file]) => [key,fs.readFileSync(path.join(here,file),'utf8')]));
}
function verify(files) {
  const failures=[];
  function check(name, condition) {if(!condition) failures.push(name);}
  const article=files.article || '', html=files.html || '', plan=files.plan || '';
  let ledger;
  try { ledger=JSON.parse(files.evidence); } catch(e){return ['EVIDENCE_JSON_PARSE'];}
  const claims=ledger.claim_decisions||[],gates=ledger.release_gates||[],src=ledger.source_links||[];
  const checkClaim=(id,decision) => claims.some(x=>x.id===id && x.decision===decision);
  // Independent editorial: scientific references exist and no endorsement linked to research.
  check('ARTICLE_IS_UNPUBLISHED',/status:.*UNPUBLISHED/i.test(article));
  check('ARTICLE_ORIGINAL_THESIS',/wander/i.test(article) && /notic/i.test(article) && /return/i.test(article));
  check('ARTICLE_HASENKAMP_PRIMARY',article.includes('https://pubmed.ncbi.nlm.nih.gov/21782031/'));
  check('ARTICLE_RCT_PRIMARY',article.includes('https://pubmed.ncbi.nlm.nih.gov/23538911/'));
  check('ARTICLE_META_PRIMARY',article.includes('https://pubmed.ncbi.nlm.nih.gov/37578065/'));
  check('ARTICLE_STUDY_LIMIT',article.includes('fourteen') && article.includes('did not') && article.includes('Zen12'));
  check('ARTICLE_NO_BUY_BUTTON',!/<(?:a|button)[^>]*affiliate/i.test(article) && !/href=.*(?:awin1.com|clickbank.net)/i.test(article));
  // Accessible no-JS site-layer prototype: real free route, genuinely blocked commercial control.
  check('HTML_NO_INDEX',/<meta name="robots" content="noindex,nofollow,noarchive">/.test(html));
  check('HTML_HTML_LANG',/<html lang="en">/.test(html));
  check('HTML_VIEWPORT',/name="viewport"/.test(html));
  check('HTML_NO_SCRIPTS',!/<script[\s>]/i.test(html));
  check('HTML_NO_IFRAME',!/<iframe[\s>]/i.test(html));
  check('HTML_NO_TRACKING_PIXEL',!/<(?:img|iframe)[^>]+(?:facebook|google-analytics|gtag|analytics|pixel)/i.test(html));
  check('HTML_NO_ADDED_FORM',!/<form[\s>]/i.test(html));
  check('HTML_ACCESSIBLE_SKIP',/class="skip" href="#main"/.test(html) && /id="main"/.test(html));
  check('HTML_ACCESSIBLE_FOCUS',/:focus-visible\s*\{/.test(html));
  check('HTML_REDUCED_MOTION',/prefers-reduced-motion:reduce/.test(html));
  check('HTML_MOBILE',/@media\(max-width:420px\)/.test(html) && /@media\(max-width:760px\)/.test(html));
  check('HTML_FOCUS_ACTIVE',/href="https:\/\/finalvestige.com\/focus\/"/.test(html));
  const buttons=[...html.matchAll(/<button\b[^>]*>/gi)].map(m=>m[0]);
  const purchase=buttons.find(b=>b.includes('class="purchase"'))||'';
  check('HTML_NATIVE_DISABLED_PURCHASE',purchase.includes(' disabled') && purchase.includes('aria-disabled="true"') && !/onclick|href=|data-url=/i.test(purchase));
  check('HTML_NO_EARNING_URL',!/awin1\.com|clickbank\.net|hop\.clickbank|ref=[A-Za-z0-9]{4,}/i.test(html));
  const disclosure=html.indexOf('Affiliate disclosure:'),buttonIndex=html.indexOf('class="purchase"');
  check('HTML_DISCLOSURE_PROXIMATE',disclosure>0 && buttonIndex>disclosure && buttonIndex-disclosure<800);
  check('HTML_DISCLOSURE_PLAIN',html.includes('may earn a commission at no additional cost to you'));
  check('HTML_PRICE_CAVEAT',html.includes('$87.99') && html.includes('not been independently verified') && html.includes('Check the exact merchant checkout'));
  check('HTML_AUDIO_LIMIT',html.includes('did not study Zen12') && html.includes('not trials of this specific commercial recording'));
  check('HTML_VIDEO_IS_NOT_FAKED',html.includes('No MP4, VTT')===false && /video has not been produced|unproduced video|Video unproduced/i.test(html) && !/<video[\s>]/i.test(html));
  check('HTML_VIDEO_TRANSCRIPT',html.includes('00:00–00:08') && html.includes('00:29–00:40'));
  check('HTML_SOURCE_TRAIL',html.includes('https://pubmed.ncbi.nlm.nih.gov/21782031/'));
  check('HTML_NO_CMS_MUTATION',!/(wp-admin|wp-json\/wp\/v2\/pages)/i.test(html));
  // Machine-readable source/claims and hard permission/settlement gates.
  check('LEDGER_SOURCE_COUNTS',src.length>=13 && src.every(s=>/^https:\/\//.test(s.url)));
  check('LEDGER_CLAIM_COUNT',claims.length>=34);
  check('LEDGER_GATE_COUNT',gates.length>=30 && gates.every(x=>x.state==='CLOSED'));
  check('LEDGER_APPROVAL_NULL',ledger.merchant_account_approval===null && ledger.affiliate_earning_url===null && ledger.channel_permissions===null);
  check('LEDGER_PRICE_NOT_VERIFIED',ledger.priced_checkout_verified===false);
  check('LEDGER_REVENUE_UNKNOWN',ledger.net_revenue_per_1000_qualified_human_sessions===null && ledger.verified_sales===null);
  check('LEDGER_VIDEO_UNPRODUCED',ledger.video_rendered===false && ledger.experiment_run===false);
  check('LEDGER_UNSUBSTANTIATED_EQUAL_HOUR',checkClaim('C18','unsupported_product_claim'));
  check('LEDGER_PRIVACY',checkClaim('C27','false') && checkClaim('C34','not_verified'));
  check('LEDGER_APPROVAL_UNVERIFIED',checkClaim('C24','not_verified') && checkClaim('C25','not_verified'));
  check('LEDGER_OBSERVED_PRICE',checkClaim('C14','observed_seller_page_only'));
  // Conversion-first decision and creator/commerce boundaries.
  check('PLAN_CREATOR_MAP',plan.includes('Change Blindness') && plan.includes('Mind wandering') && plan.includes('Puységur'));
  check('PLAN_HARD_HOLD',plan.includes('Commercial HARD HOLD') || plan.includes('Commercial decision:** HARD HOLD'));
  check('PLAN_ASSET_IDS_NULL',plan.includes('asset_id=NULL'));
  check('PLAN_SETTLEMENT_MATH',plan.includes('settled attributable net revenue / qualified human sessions'));
  check('PLAN_7_30_DAY',plan.includes('7/30-day') || plan.includes('7d and 30d'));
  check('PLAN_NOT_CLICK_SALE',plan.includes('A click is NOT a purchase'));
  check('PLAN_NO_PRODUCTION',plan.includes('No new scripts, popups') && plan.includes('Mind hub PR #172'));
  check('PLAN_RESEARCH_AND_PRODUCT_SOURCE',plan.includes('https://zen12.com/?no-popup=1') && plan.includes('https://www.ftc.gov/'));
  return failures;
}
function run() {
  const files=load();
  const errs=verify(files);
  assert.deepEqual(errs,[], 'baseline failed: '+errs.join(', '));
  let detected=0;
  const cases=[
    ['affiliate authorization forged', f=>{f.evidence=f.evidence.replace('"merchant_account_approval": null','"merchant_account_approval": "approved"');}],
    ['live partner link forged', f=>{f.evidence=f.evidence.replace('"affiliate_earning_url": null','"affiliate_earning_url": "https://unknown.invalid"');}],
    ['checkout price claimed verified', f=>{f.evidence=f.evidence.replace('"priced_checkout_verified": false','"priced_checkout_verified": true');}],
    ['purchase control enabled', f=>{f.html=f.html.replace('class="purchase" disabled','class="purchase"');}],
    ['affiliate disclosure deleted', f=>{f.html=f.html.replace('Affiliate disclosure:','Partner notice:');}],
    ['disclosure moved too far', f=>{f.html=f.html.replace('class="purchase"','data-note="'+ 'x'.repeat(1000) +'" class="purchase"');}],
    ['paid price caveat deleted', f=>{f.html=f.html.replace('Check the exact merchant checkout','Ignore the merchant checkout');}],
    ['unapproved tracking introduced', f=>{f.html+='\n<script src="//example.invalid/tracker.js"></script>'; }],
    ['unapproved signup introduced', f=>{f.html+='<form method="post"></form>'; }],
    ['video falsely claims production', f=>{f.evidence=f.evidence.replace('"video_rendered": false','"video_rendered": true');}],
    ['video fake media player inserted', f=>{f.html+='<video autoplay><source src="bad.mp4"></video>'; }],
    ['research citation removed', f=>{f.article=f.article.replaceAll('https://pubmed.ncbi.nlm.nih.gov/21782031/','https://invalid.invalid');}],
    ['seller health claim promoted as evidence', f=>{f.evidence=f.evidence.replace('"id": "C18",\n      "claim": "Zen12 delivers benefits of an hour of meditation in 12 minutes",\n      "decision": "unsupported_product_claim"','"id": "C18",\n      "claim": "Zen12 delivers benefits of an hour of meditation in 12 minutes",\n      "decision": "research_supported"');}],
    ['missing creator IDs represented as known', f=>{f.plan=f.plan.replaceAll('asset_id=NULL','asset_id=FAKED');}],
    ['sales claimed from click', f=>{f.plan=f.plan.replace('A click is NOT a purchase','A click is a purchase');}],
    ['merchant earnings claimed verified', f=>{f.evidence=f.evidence.replace('"verified_sales": null','"verified_sales": 12');}],
    ['commercial gates opened', f=>{f.evidence=f.evidence.replace('"state": "CLOSED"','"state": "OPEN"');}],
    ['free fieldbook URL removed', f=>{f.html=f.html.replaceAll('href="https://finalvestige.com/focus/"','href="#broken"');}],
    ['scriptless protection removed', f=>{f.html+='<iframe src="https://unknown.invalid/"></iframe>'; }],
    ['no-index safety removed', f=>{f.html=f.html.replace('noindex,nofollow,noarchive','index,follow');}]
  ];
  for (const [label,mutate] of cases) {
    const copy={...files};
    mutate(copy);
    const violations=verify(copy);
    assert.ok(violations.length>0, 'adversarial mutation NOT detected: '+label);
    detected++;
  }
  return {source_checks:'PASS', baseline_assertions:48,mutations_detected:detected,mutations_total:cases.length,test_mode:'native Node source checks only; no real browser or merchant'};
}
if (require.main===module) console.log(JSON.stringify(run(),null,2));
module.exports={verify,run};
