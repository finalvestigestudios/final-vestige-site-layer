/* Final Vestige R18 source guardrails.
   Node: node mind/sperling-zen12-r18/qa.cjs --mutation
   Pure audit(files,matrix) also runnable on verified GitHub readbacks in isolated V8.
   Source checks are NOT WordPress runtime, browser AT, QA approval or efficacy validation. */
'use strict';
function audit(files,matrix){
 const checks=[],errors=[];
 function check(id,ok){ checks.push({id,ok:!!ok});if(!ok)errors.push(id); }
 const I=files['INVESTIGATION.html']||'';
 const A=files['PILOT_A.html']||'';
 const B=files['PILOT_B_STAGING.html']||'';
 const G=files['ZEN12_BUYER_GUIDE.md']||'';
 const P=files['EXPERIMENT_AND_RELEASE.md']||'';
 const R=files['README.md']||'';
 const Z=matrix||{};
 const html=[['I',I],['A',A],['B',B]];
 for(const [label,h] of html){
  check(label+' has single h1', (h.match(/<h1\b/g)||[]).length===1);
  check(label+' has disabled button', /<button\b[^>]*\bdisabled\b/i.test(h));
  check(label+' marks disabled accessibly', /aria-disabled="true"/.test(h));
  check(label+' has close plain commission language', /Final Vestige may earn a commission at no additional cost to you/.test(h));
  check(label+' no merchant anchors', !/<a\b[^>]*href=["']https?:\/\/(?:www\.)?(?:zen12|inspire3|affiliates\.inspire3)\.com/i.test(h));
  check(label+' no newsletter form', !/<form\b/i.test(h));
  check(label+' no email capture', !/<input\b[^>]*type=["']email/i.test(h));
  check(label+' no scripts or embeds', !/<(?:script|iframe)\b/i.test(h));
  check(label+' no autoplay', !/<video\b[^>]*\bautoplay\b/i.test(h));
  check(label+' no analytics pixel', !/(?:facebook\.com\/tr|googletagmanager|google-analytics|doubleclick|sendBeacon|localStorage\.setItem)/i.test(h));
  check(label+' no live signup injection', !/jetpack-subscriptions__form-elements|<form|type=["']email/i.test(h));
  check(label+' includes reliable focus route', h.includes('https://finalvestige.com/focus/'));
  check(label+' has responsive styles', h.includes('@media(max-width:'));
  check(label+' has keyboard focus provision', h.includes(':focus-visible'));
  check(label+' has reduced motion provision', h.includes('prefers-reduced-motion'));
  check(label+' has forced colors provision', h.includes('forced-colors'));
  check(label+' no unearned efficacy endorsement', !/we (?:guarantee|proved|tested|verified) (?:Zen12|this product)/i.test(h));
  check(label+' no false testimonial', !/(?:I personally used Zen12|our team achieved a Zen12|I got rich with Zen12)/i.test(h));
 }
 check('I original Sperling context', I.includes('George Sperling')&&I.includes('partial-report')&&I.includes('50-millisecond'));
 check('I original 10 sections', (I.match(/<section\b/g)||[]).length>=10);
 check('I untimed nonvalidated grid caveat', I.includes('not a replication or diagnostic test'));
 check('I cites Puységur live archive', I.includes('Puységur')&&I.includes('puysegurs-animal-magnetism-files'));
 check('I has scientific sources', I.includes('Sperling_PsychMonogr_1960.pdf')&&I.includes('pubmed.ncbi.nlm.nih.gov/37578065/'));
 check('I commercial panel separate', I.includes('Separate independent product evaluation'));
 check('A is text-only', !/<video\b/i.test(A));
 check('A retained film slot anchor', A.includes('<!--VIDEO_SLOT-->'));
 check('A original credible microstory', A.includes('1960 George Sperling'));
 check('A 4 product audio forms', ['Guided meditation','Relaxation music','White noise','Nature sounds'].every(x=>A.includes(x)));
 check('A buyer objections actual checkout timer', A.includes('countdown')&&A.includes('mobile phone'));
 check('A free twelve minutes', A.includes('Try twelve free minutes first'));
 check('A includes exact film visual transcript', A.includes('Read the complete film transcript'));
 check('B native controls + no-preload', /<video\b[^>]*\bcontrols\b[^>]*\bplaysinline\b[^>]*preload="none"/.test(B));
 check('B media hidden pending verification', /<video\b[^>]*\bhidden\b/.test(B)&&B.includes('data-media-approved="false"'));
 check('B only review-only relative media', B.includes('REVIEW_ONLY_zen12_40s_portrait.mp4'));
 check('B captions track', /<track\b[^>]*kind="captions"/.test(B)&&B.includes('.vtt'));
 check('B source returns original full copy', B.replace(/<!-- REVIEW ONLY: video B staging candidate, media UNHOSTED, unpublished, no CMS writes -->/,'<!-- REVIEW ONLY: text A, unpublished, no CMS writes or earning URLs -->').replace(/<figure class="fv-z18-film"[\s\S]*?<\/figure>/,'<!--VIDEO_SLOT-->')===A);
 check('B full matching text transcript', B.includes('Read the complete film transcript')&&B.includes('32–40:'));
 check('buyer guide exact actual offer', G.includes('https://zen12.com/about')&&G.includes('https://zen12.com/getstarted'));
 check('buyer guide checks checkout privacy', G.includes('mobile phone number')&&G.includes('countdown'));
 check('buyer guide refrains from price amounts', G.includes('No particular sale price'));
 check('buyer guide mindfulness study is not SKU proof', G.includes('Zen12\'s marketed recordings were not thereby evaluated'));
 check('buyer guide declared no firsthand use', G.includes('not purchased or listened to'));
 check('buyer guide preserves focus', G.includes('https://finalvestige.com/focus/'));
 check('plan fair A/B disclosure equality', P.includes('Exactly identical')&&P.includes('plain-language near-button'));
 check('plan privacy OFF', P.includes('No pixel')&&P.includes('No server log changes')&&P.includes('No collection enabled here')===false);
 check('plan preserves no-JS and site QA', P.includes('no JS')&&P.includes('Site QA #126'));
 check('plan requires real browser device widths', P.includes('360, 390, 768, 1440 and 1920'));
 check('plan requires accessibility review', P.includes('NVDA/VoiceOver'));
 check('plan no actual sales from click', P.includes('not actual purchases'));
 check('plan does not activate hosted media', P.includes('REVIEW_ONLY_'));
 check('plan confirms other agents protected', P.includes('Homepage flagship PR #49')&&P.includes('Dispatch #174'));
 check('plan maintains one Jetpack signup', P.includes('Jetpack signup'));
 check('source matrix at least 50 claims', Array.isArray(Z.claims)&&Z.claims.length>=50);
 check('source matrix at least 15 sources', Z.source_urls&&Object.keys(Z.source_urls).length>=15);
 check('matrix ids unique', new Set((Z.claims||[]).map(c=>c.id)).size===(Z.claims||[]).length);
 check('matrix links valid', (Z.claims||[]).every(c=>Array.isArray(c.source_ids)&&c.source_ids.every(id=>Object.hasOwn(Z.source_urls||{},id))));
 check('matrix no affiliate URL', Z.affiliate_earning_url===null);
 check('matrix partner not approved', Z.partner_approval_verified===false);
 check('matrix tracker OFF', Z.affiliate_tracking_enabled===false);
 check('matrix no actual product trial', Z.original_product_tested===false);
 check('matrix social rights unverified', Z.social_promotion_allowed===null);
 check('matrix email rights unverified', Z.email_promotion_allowed===null);
 check('matrix creative permissions unverified', Z.approved_creatives_verified===false);
 check('matrix contains excluded unsupported claim', (Z.claims||[]).some(c=>c.disposition==='unsupported_suppress'&&/hour/i.test(c.claim)));
 check('matrix exact FTC references', Z.source_urls?.FTC_ENDORSEMENT?.includes('ftcs-endorsement-guides')&&Z.source_urls?.FTC_HEALTH?.includes('health-products-compliance'));
 check('matrix separate seller science', (Z.claims||[]).some(c=>c.disposition==='seller_feature')&&(Z.claims||[]).some(c=>c.disposition==='independent_context'));
 check('readme release hold', R.includes('HOLD'));
 check('readme command', R.includes('qa.cjs --mutation'));
 return {passed:checks.length-errors.length,failed:errors.length,errors,checks};
}
if(typeof module!=='undefined')module.exports={audit};
if(typeof require==='function'&&typeof module!=='undefined'&&require.main===module){
 const fs=require('node:fs'),path=require('node:path');
 const names=['INVESTIGATION.html','ZEN12_BUYER_GUIDE.md','PILOT_A.html','PILOT_B_STAGING.html','EXPERIMENT_AND_RELEASE.md','README.md'];
 const files=Object.fromEntries(names.map(n=>[n,fs.readFileSync(path.join(__dirname,n),'utf8')]));
 const matrix=JSON.parse(fs.readFileSync(path.join(__dirname,'EVIDENCE_MATRIX.json'),'utf8'));
 const result=audit(files,matrix);
 console.log(JSON.stringify({source_checks:result.passed,failed:result.failed,errors:result.errors},null,2));
 if(result.failed)process.exitCode=1;
 if(process.argv.includes('--mutation')){
   const attacks=[
    ['remove CTA disclosure',o=>({...o,'PILOT_A.html':o['PILOT_A.html'].replace('Final Vestige may earn a commission at no additional cost to you','There may be something')})],
    ['activate button',o=>({...o,'PILOT_A.html':o['PILOT_A.html'].replace(' disabled aria-disabled="true"','')})],
    ['link direct checkout',o=>({...o,'PILOT_A.html':o['PILOT_A.html'].replace('</button>','</button><a href="https://zen12.com/getstarted">Buy now</a>')})],
    ['inject email form',o=>({...o,'PILOT_A.html':o['PILOT_A.html']+'<form><input type="email"></form>'})],
    ['inject tracker',o=>({...o,'PILOT_B_STAGING.html':o['PILOT_B_STAGING.html']+'<script src="https://www.googletagmanager.com/gtag/js"></script>'})],
    ['autoplay film',o=>({...o,'PILOT_B_STAGING.html':o['PILOT_B_STAGING.html'].replace('controls playsinline preload="none"','controls playsinline autoplay preload="none"')})],
    ['unhide placeholder film',o=>({...o,'PILOT_B_STAGING.html':o['PILOT_B_STAGING.html'].replace('<video hidden controls','<video controls')})],
    ['remove caption track',o=>({...o,'PILOT_B_STAGING.html':o['PILOT_B_STAGING.html'].replace(/<track\b[^>]*>/,'')})],
    ['remove free fieldbook link',o=>({...o,'PILOT_A.html':o['PILOT_A.html'].replaceAll('https://finalvestige.com/focus/','/not-existing')})],
    ['rewrite research caveat',o=>({...o,'INVESTIGATION.html':o['INVESTIGATION.html'].replace('not a replication or diagnostic test','a replication and diagnostic test')})],
   ];
   const m=attacks.map(([name,change])=>({name,caught:audit(change(files),matrix).failed>0}));
   console.log(JSON.stringify({adversarial:m,detected:m.filter(x=>x.caught).length,total:m.length},null,2));
   if(m.some(x=>!x.caught))process.exitCode=1;
 }
}