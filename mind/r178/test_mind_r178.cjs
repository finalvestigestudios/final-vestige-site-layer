/* R178 isolated regression; run: node mind/r178/test_mind_r178.cjs
 * Run from repository root. Source-level only: not CI, browser, merchant or video validation. */
'use strict';
function validate(files){
  const checks=[];
  function check(label,ok){checks.push({label,ok:!!ok});}
  const A=files.A||'',B=files.B||'',H=files.H||'',M=files.M||'',G=files.G||'',P=files.P||'',R=files.R||'';
  let data;try{data=JSON.parse(M);}catch(e){data=null;}
  for(const [name,html] of [['A',A],['B',B]]){
    check(name+' noindex',/<meta name="robots" content="noindex,nofollow"/i.test(html));
    check(name+' native disabled purchase',/<button\s+type="button" disabled\b/i.test(html));
    check(name+' no active merchant purchase href',!/<a\b[^>]*href=["']https?:\/\/(?:www\.)?(?:zen12|inspire3|hypnosislive|brainwaveshots)\./i.test(html));
    check(name+' adjacent commission disclosure',/<div class="disclosure">[\s\S]{0,700}commission[\s\S]{0,400}<\/div>\s*<button\s+type="button" disabled/i.test(html));
    check(name+' existing Focus link',/href="https:\/\/finalvestige.com\/focus\/"/.test(html));
    check(name+' no form',!/<form\b/i.test(html));
    check(name+' no script iframe or autoplay',!/<(?:script|iframe)\b/i.test(html)&&!/autoplay\s*(?:=|>)/i.test(html));
    check(name+' no tracking, checkout or referral functions',!/\b(?:dataLayer\.push|gtag\(|fbq\(|window\.location\s*=)\b/.test(html));
    check(name+' skip nav and main',/href="#main"/.test(html)&&/<main id="main">/.test(html));
    check(name+' seller claims qualified',html.includes('seller-described')&&html.includes('No purchase link'));
    check(name+' free alternative',/three-day routine-fit check/i.test(html));
  }
  check('variant A contains no proposed video section',!A.includes('aria-labelledby="video-title"'));
  check('variant B contains poster/transcript section',B.includes('aria-labelledby="video-title"')&&B.includes('complete proposed 42-second video transcript'));
  check('variant B no unrendered video tag',!/<video\b/i.test(B));
  check('variant B user-initiated playback only',!/<source\b/i.test(B));
  check('hub noindex',H.includes('noindex,nofollow'));
  check('hub four editorial streams', ['PERCEPTION &amp; ATTENTION','HISTORY OF SUGGESTION','PRACTICE &amp; REFLECTION','TOOLS UNDER REVIEW'].every(x=>H.includes(x)));
  check('hub no opt-in duplication',!/<form\b/i.test(H));
  check('hub existing Focus path',H.includes('https://finalvestige.com/focus/'));
  check('hub independent history',H.includes('puysegurs-animal-magnetism-files'));
  check('hub no commerce href',!/<a\b[^>]*href=["']https?:\/\/(?:www\.)?(?:zen12|inspire3)\./i.test(H));
  check('matrix parses',!!data);
  if(data){
    check('matrix still hard hold',data.state==='UNPUBLISHED_HARD_HOLD');
    check('no affiliate approval',data.commercial.inspire3_approved===null);
    check('no earning url',data.commercial.approved_tracking_url===null);
    check('no activation',data.commercial.affiliate_activated===false);
    check('no imaginary paid revenue',data.commercial.paid_commissions_received===null&&data.commercial.verified_net_revenue===null);
    check('no imaginary sessions',data.commercial.qualified_human_sessions===null);
    check('no invented owned Mind SKU',data.commercial.owned_payhip_mind_sku===null);
    check('video not produced',data.commercial.video_produced===false);
    check('A/B not executed',data.commercial.AB_experiment_executed===false);
    check('source citation matrix populated',data.sources?.length>=15&&data.claims?.length>=25);
    check('product-specific unsupported benefits rejected',data.claims?.some(c=>c.id==='P08'&&c.disposition.startsWith('REJECT')));
    check('partner gate closed',data.gates?.some(g=>g.id==='affiliate_partner_identity'&&g.state==='CLOSED'));
  }
  check('article original McGurk 1976',G.includes('23 December 1976')&&G.includes('doi.org/10.1038/264746a0'));
  check('article no direct merchant purchasing link',!/<a\b[^>]*href=["']https?:\/\/(?:zen12|inspire3)\./i.test(G));
  check('article uncertainty and individual variation',G.includes('variability')&&G.includes('does not'));
  check('article with standalone free exercise',G.includes('two-column listening log'));
  check('article separation of research and commercial',G.includes('contains no endorsement')&&G.includes('does not establish'));
  check('guide authentic review',P.includes('12 levels')||P.includes('twelve levels'));
  check('guide review citation is exact and mixed',P.includes('37205669')&&P.includes('eight contradictory'));
  check('guide no active earning link',P.includes('no active purchase/referral link')||P.includes('no active purchase'));
  check('plan prevents double refund deduction',R.includes('not already deducted')||R.includes('already deducted'));
  check('plan allows negative net',R.includes('do not clamp a negative value to zero'));
  check('plan concrete consent/source event',R.includes('affiliate_click')&&R.includes('merchant_confirmed_purchase'));
  check('plan preserves Grok boundaries',R.includes('TASK-008')&&R.includes('Mini Museum'));
  const failed=checks.filter(c=>!c.ok);
  return {passed:checks.length-failed.length,total:checks.length,failed:failed.map(c=>c.label)};
}
function mutationTests(original){
  const attempts=[];
  function attack(label,key,from,to){let x={...original};if(!x[key]?.includes(from))throw Error('Bad mutation anchor: '+label);x[key]=x[key].replace(from,to);let r=validate(x);attempts.push({label,rejected:r.failed.length>0});}
  attack('A enabled purchase','A','type="button" disabled','type="button"');
  attack('B enabled purchase','B','type="button" disabled','type="button"');
  attack('A merchant href injected','A','<main id="main">','<a href="https://zen12.com/buy">BUY</a><main id="main">');
  attack('B merchant href injected','B','<main id="main">','<a href="https://hypnosislive.com/checkout">BUY</a><main id="main">');
  attack('A disclosure removed','A','<div class="disclosure">','<div class="disclosure-removed">');
  attack('B disclosure removed','B','<div class="disclosure">','<div class="disclosure-removed">');
  attack('A new opt-in','A','<main id="main">','<form action="/subscribe"></form><main id="main">');
  attack('B new opt-in','B','<main id="main">','<form action="/subscribe"></form><main id="main">');
  attack('A external JS','A','<main id="main">','<script src="https://example.org/analytics.js"></script><main id="main">');
  attack('B iframe','B','<main id="main">','<iframe src="https://example.org"></iframe><main id="main">');
  attack('B fake video element','B','<main id="main">','<video autoplay src="no-permission.mp4"></video><main id="main">');
  attack('A forced video section','A','<main id="main">','<section aria-labelledby="video-title">BAD</section><main id="main">');
  attack('B removes transcript','B','complete proposed 42-second video transcript','transcript omitted');
  attack('Hub new form','H','<main id="main">','<form></form><main id="main">');
  attack('Hub noindex removed','H','noindex,nofollow','index,follow');
  attack('Article source changed','G','doi.org/10.1038/264746a0','example.org/unsupported');
  attack('Article removes demonstration','G','two-column listening log','two-column miracle');
  attack('Guide removes review evidence','P','37205669','unverified');
  attack('Revenue negative clamped','R','do not clamp a negative value to zero','clamp loss to zero');
  attack('Plan conflates click and purchase','R','affiliate_click','outbound_treated_as_sale');
  function changeJson(label,fn){const x={...original},o=JSON.parse(x.M);fn(o);x.M=JSON.stringify(o);attempts.push({label,rejected:validate(x).failed.length>0});}
  changeJson('fake affiliate approval',o=>o.commercial.inspire3_approved=true);
  changeJson('fake affiliate URL',o=>o.commercial.approved_tracking_url='https://aff.example/click');
  changeJson('fake commission amount',o=>o.commercial.paid_commissions_received=20);
  changeJson('affiliate activated',o=>o.commercial.affiliate_activated=true);
  changeJson('imagined visitor count',o=>o.commercial.qualified_human_sessions=1000);
  changeJson('fake video completion',o=>o.commercial.video_produced=true);
  changeJson('fake A/B trial',o=>o.commercial.AB_experiment_executed=true);
  changeJson('unclosed partner gate',o=>o.gates.find(g=>g.id==='affiliate_partner_identity').state='OPEN');
  changeJson('binaural marketing upgrade',o=>o.claims.find(c=>c.id==='P08').disposition='ALLOW');
  return {total:attempts.length,rejected:attempts.filter(a=>a.rejected).length,escaped:attempts.filter(a=>!a.rejected).map(a=>a.label)};
}
if(typeof module!=='undefined')module.exports={validate,mutationTests};
if(typeof require!=='undefined'&&require.main===module){
  const fs=require('node:fs'),path=require('node:path');
  const root=process.cwd();
  const paths={
    A:'mind/r178/zen12-premium-presell-variant-A-UNPUBLISHED.html',
    B:'mind/r178/zen12-premium-presell-variant-B-UNPUBLISHED.html',
    H:'mind/r178/mind-archive-four-stream-WORDPRESS-DRAFT-UNPUBLISHED.html',
    M:'mind/r178/merchant-claims-proof-and-closed-activation-gates.json',
    G:'mind/r178/hearing-with-your-eyes-mcgurk-evidence-INVESTIGATION-UNPUBLISHED.md',
    P:'mind/r178/zen12-exact-offer-evidence-buyer-guide-UNPUBLISHED.md',
    R:'mind/r178/offer-first-funnel-creator-fit-ab-and-revenue-ACCEPTANCE.md'
  };
  const files=Object.fromEntries(Object.entries(paths).map(([k,p])=>[k,fs.readFileSync(path.join(root,p),'utf8')]));
  const base=validate(files),mutations=mutationTests(files);
  console.log(JSON.stringify({baseline:base,mutations},null,2));
  if(base.failed.length||mutations.escaped.length)process.exitCode=1;
}