'use strict';
/* R17 source-only contract QA; run: node mind/invisible-gorilla-r17/qa.cjs --mutation
   Does NOT prove WordPress, WCAG compliance, film hosting, Playwright, or live CI. */
function audit(bundle) {
  const H=bundle.html||'', G=bundle.guide||'', M=bundle.matrix||{}, P=bundle.pilot||'', W=bundle.warmup||'';
  const results=[];
  function check(name,condition){results.push({name,pass:!!condition});}
  const cleanText=H.replace(/<style>[\s\S]*?<\/style>/g,' ').replace(/<[^>]*>/g,' ').replace(/&(?:amp|lt|gt|nbsp|mdash|rsquo);/g,' ');
  const words=t=>String(t).trim().split(/\s+/).filter(Boolean).length;
  check('article full investigation >1700 words',words(cleanText)>1700);
  check('independent guide >1600 words',words(G)>1600);
  check('visible original report title',H.includes('Everyone Saw the Gorilla.'));
  check('semantic main article',/<article\s+class="fv-mind-gorilla"\s+aria-labelledby="fvg-title"/.test(H));
  check('primary study 1999 link',H.includes('https://doi.org/10.1068/p281059'));
  check('follow-up 2010 link',H.includes('https://doi.org/10.1068/i0386'));
  check('radiologists study 2013 link',H.includes('https://doi.org/10.1177/0956797613479386'));
  check('1975 prior study',H.includes('https://doi.org/10.1016/0010-0285(75)90019-5'));
  check('2010 statistical nuance',/not statistically significant/i.test(H));
  check('2013 expert size caveat',/24 radiologists/.test(H)&&/83 percent/.test(H));
  check('original diagram nonvalidated note',/not a controlled psychological experiment/.test(H));
  check('no borrowed gorilla test video',!/<(iframe|video|audio)\b/i.test(H));
  check('first-party Puységur published route',H.includes('https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'));
  check('single Focus published route',H.includes('https://finalvestige.com/focus/'));
  check('source section exists',H.includes('id="fvg-sources"'));
  check('no unpublished mind URL represented as live',!/href="https:\/\/finalvestige\.com\/mind\//i.test(H));
  check('article section navigation accessible',/nav class="fvg-nav" aria-label=/.test(H));
  check('figure text accessible',H.includes('aria-label="Two abstract arrangements'));
  check('two distinct schematic frames', (H.match(/class="fvg-frame"/g)||[]).length===2 && H.includes('.fvg-frame:nth-child(2) .fvg-dot:nth-child(4)'));
  check('no inline script',!/<script\b/i.test(H));
  check('no forms/newsletter duplication',!/<form\b/i.test(H));
  check('no third-party embed',!/<iframe\b/i.test(H));
  check('no autoplay media',!/<(?:video|audio)[^>]*autoplay/i.test(H));
  check('no forced redirect',!/<meta[^>]*refresh|window\.location|location\.href/i.test(H));
  check('no tracking beacon',!/google-analytics|gtag\(|facebook\.com\/tr|dataLayer|localStorage|sessionStorage/i.test(H));
  check('no arbitrary remote script loading',!/<script[^>]+src=/i.test(H));
  check('no checkout action link in article',!/<a[^>]+href="https:\/\/zen12\.com\/getstarted"[^>]*>(?:Buy|Purchase|Start|Get|Review the offer)/i.test(H));
  check('merchant CTA disabled',/<button class="fvg-disabled"[^>]*disabled\s+aria-disabled="true"/.test(H));
  check('no active offer link within commerce panel', /<section class="fvg-commerce"[\s\S]*?<\/section>/.test(H) && !/<a\b/i.test((H.match(/<section class="fvg-commerce"[\s\S]*?<\/section>/)||[])[0]||''));
  check('commission relationship disclosed nearby',/Potential affiliate relationship:[\s\S]{0,270}Final Vestige may earn a commission/i.test(H));
  check('CTA visibly shows approval unavailable',/Merchant link unavailable/.test(H));
  check('readers can choose free option',/free.*Focus Fieldbook|Focus Fieldbook.*free/is.test(H));
  check('seller claims not presented as proven',/have not found product-specific independent evidence/.test(H));
  check('original exercise not a clinical assessment',/not a validated inattentional-blindness test/.test(H));
  check('responsive two-column collapses',/@media\(max-width:700px\)/.test(H));
  check('reduced motion covered',/prefers-reduced-motion:reduce/.test(H));
  check('forced colors covered',/forced-colors:active/.test(H));
  check('visible keyboard focus',/:focus-visible/.test(H));
  check('no external webfont or third-party dependencies',!/@import|fonts\.googleapis|<link\b/i.test(H));
  check('exact Zen12 brand and formats',/12 levels|twelve levels/i.test(G)&&/four listening styles|four formats|four listening styles/i.test(G));
  check('exact Zen12 offer URL reviewed',G.includes('https://zen12.com/getstarted'));
  check('official Inspire3 catalog reviewed',G.includes('https://inspire3.com/'));
  check('no unsupported hour equivalence stated as evidence',/not.*show equal effects/.test(G));
  check('buyer guide mentions no firsthand product use',/not purchased or personally used Zen12/.test(G));
  check('free timer alternative present',/A phone timer and a quiet room cost nothing/.test(G));
  check('checkout terms warned dynamic',/Do not copy a price, discount, countdown/i.test(G));
  check('guided + noise + music + nature formats described',/guided meditation/.test(G)&&/white noise/.test(G)&&/nature sounds/.test(G)&&/relaxation music/.test(G));
  check('source registry >= 12',Array.isArray(M.sources)&&M.sources.length>=12);
  check('claim registry >= 40',Array.isArray(M.claims)&&M.claims.length>=40);
  check('IDs unique',new Set((M.claims||[]).map(c=>c.id)).size===(M.claims||[]).length);
  check('all source IDs resolve',(M.claims||[]).every(c=>Array.isArray(c.source_ids)&&c.source_ids.every(id=>(M.sources||[]).some(s=>s.id===id))));
  check('source records contain HTTPS URLs',(M.sources||[]).every(s=>/^https:\/\//.test(s.url)));
  check('claim dispositions every record',(M.claims||[]).every(c=>c.editorial_handling&&c.status&&c.claim));
  check('claims explicitly suppress 12min=1h', (M.claims||[]).some(c=>/equals one hour/.test(c.claim)&&c.status==='UNSUPPORTED_SUPPRESS'));
  check('inattentional blindness cure claim suppressed', (M.claims||[]).some(c=>/help viewers notice invisible gorillas/.test(c.claim)&&c.status==='UNSUPPORTED_SUPPRESS'));
  check('no account approval',(M.affiliate||{}).account_approval_verified===false);
  check('no authorized earning link',(M.affiliate||{}).authorized_earning_url===null);
  check('no tracking',(M.affiliate||{}).tracking_enabled===false);
  check('no A/B experiment active',(M.affiliate||{}).conversion_test_live===false);
  check('no product eligibility verified',(M.affiliate||{}).sku_eligibility_verified===false);
  check('no creative rights verified',(M.affiliate||{}).approved_creatives_verified===false);
  check('no email promotion authorization',(M.affiliate||{}).newsletter_promotion_rights_verified===false);
  check('film variant has optional native controls spec',/video controls preload="none" playsinline/.test(P));
  check('film media placeholders not falsely hosted',P.includes('[VERIFIED_SITE_MP4_URL]'));
  check('B no-JS transcript explicitly required',P.includes('full transcript')&&P.includes('without JavaScript'));
  check('comparison identical guide wording',P.includes('exactly the same core visible text'));
  check('instrumentation privacy explicitly disabled',/tracking.*OFF|Current privacy module stays \*\*OFF\*\*/.test(P));
  check('no purchase from click inference',/Never call a click a purchase/.test(P));
  check('PR #49 ownership untouched in plan',P.includes('PR #49'));
  check('Mind hub #172 ownership untouched in plan',P.includes('PR #172'));
  check('Dispatch #174 coordination-only in plan',P.includes('Issue #174'));
  check('existing Jetpack funnel kept',P.includes('single')&&P.includes('Jetpack'));
  check('FTC close disclosure wording',/If you purchase through this link, Final Vestige may earn a commission/.test(P));
  const warmText=W.replace(/<style>[\s\S]*?<\/style>/g,' ').replace(/<[^>]*>/g,' ');
  check('standalone text-only Zen12 warmup >1000 words',words(warmText)>1000);
  check('warmup has first-party accessible heading',/aria-labelledby="fvm-z17-title"/.test(W));
  check('warmup no newsletter form',!/<form\b/i.test(W));
  check('warmup no tracking scripts',!/<script\b|<iframe\b|localStorage|gtag\(/i.test(W));
  check('warmup no broken video player',!/<video\b/i.test(W));
  check('warmup optional transcript concept',/film would explain/.test(W)&&/No finished hosted film/.test(W));
  check('warmup seller exact SKU sources',W.includes('https://zen12.com/about')&&W.includes('https://zen12.com/getstarted'));
  check('warmup research 2010 primary',W.includes('https://doi.org/10.1068/i0386'));
  check('warmup near-CTA affiliate disclosure',/Affiliate disclosure:[\s\S]{0,300}Final Vestige may earn a commission/.test(W));
  check('warmup disabled purchase button',/<button class="z17-disabled"[^>]*disabled aria-disabled="true"/.test(W));
  check('warmup no active merchant link in offer panel', /<section class="z17-cta"[\s\S]*?<\/section>/.test(W)&&!/<a\b/i.test((W.match(/<section class="z17-cta"[\s\S]*?<\/section>/)||[])[0]||''));
  check('warmup practical no-cost alternative',W.includes('https://finalvestige.com/focus/')&&/free timer|free practice|before you spend/i.test(W));
  check('warmup explicitly seller-claim only',/seller claim, not our conclusion/.test(W));
  check('warmup no false conversion results',!/increased conversions by|proven to convert|conversion rate rose/i.test(W));
  check('warmup responsive and motion safe',/@media\(max-width:650px\)/.test(W)&&/prefers-reduced-motion:reduce/.test(W));
  check('warmup keyboard focus',/:focus-visible/.test(W));
  const ratio=(a,b)=>{const ch=(s)=>{let rgb=s.match(/[a-f0-9]{2}/gi).map(v=>parseInt(v,16)/255);let lin=rgb.map(x=>x<=.04045?x/12.92:Math.pow((x+.055)/1.055,2.4));return lin[0]*.2126+lin[1]*.7152+lin[2]*.0722};let q=[ch(a),ch(b)].sort((x,y)=>y-x);return(q[0]+.05)/(q[1]+.05)};
  const contrast=[['body_on_bg','d8d2c7','090a0a',4.5],['ink_on_bg','f4efe6','090a0a',4.5],['muted_on_bg','aaa49a','090a0a',4.5],['gold_on_bg','c7a66c','090a0a',4.5],['panel_disclose','f4efe6','242016',4.5],['disabled_button','f4efe6','393730',4.5],['link_on_bg','ead1a8','090a0a',4.5]];
  contrast.forEach(([name,fg,bg,min])=>check('contrast '+name,ratio(fg,bg)>=min));
  return {results,passed:results.filter(t=>t.pass).length,total:results.length,failures:results.filter(t=>!t.pass).map(t=>t.name)};
}
function mutations(bundle){
 const deep=x=>JSON.parse(JSON.stringify(x)),tests=[
 ['removed commission disclosure',b=>{b.html=b.html.replace(/Final Vestige may earn a commission/g,'No compensation');}],
 ['activated CTA',b=>{b.html=b.html.replace('disabled aria-disabled="true"','aria-disabled="false"');}],
 ['merchant checkout in commercial box',b=>{b.html=b.html.replace('<button class="fvg-disabled"','<a href="https://zen12.com/getstarted">Buy Now</a><button class="fvg-disabled"');}],
 ['injected form',b=>{b.html+='<form><input></form>';}],
 ['injected script',b=>{b.html+='<script>alert(1)<\/script>';}],
 ['injected iframe',b=>{b.html+='<iframe src="https://example.org"></iframe>';}],
 ['deleted original research',b=>{b.html=b.html.replaceAll('https://doi.org/10.1068/i0386','https://no-research.invalid');}],
 ['broken Focus route',b=>{b.html=b.html.replaceAll('https://finalvestige.com/focus/','https://not-real.invalid/');}],
 ['missing reduced-motion',b=>{b.html=b.html.replace('prefers-reduced-motion:reduce','prefers-motion:reduce');}],
 ['duplicate source claim ID',b=>{b.matrix.claims[0].id=b.matrix.claims[1].id;}],
 ['fake approved affiliate',b=>{b.matrix.affiliate.account_approval_verified=true;}],
 ['activated tracking',b=>{b.matrix.affiliate.tracking_enabled=true;}],
 ['fabricated earning link',b=>{b.matrix.affiliate.authorized_earning_url='https://example.org/?aff=123';}],
 ['removed video controls',b=>{b.pilot=b.pilot.replace('video controls preload="none"','video autoplay preload="auto"');}],
 ['absent original film placeholder',b=>{b.pilot=b.pilot.replace('[VERIFIED_SITE_MP4_URL]','https://not-reviewed.example/video.mp4');}],
 ['removed review research context',b=>{b.guide=b.guide.replace('https://inspire3.com/','https://unknown.example/');}],
 ['removed free alternative',b=>{b.guide=b.guide.replace('A phone timer and a quiet room cost nothing.','Pay for all meditation sessions.');}],
 ['removed video source constraints',b=>{b.pilot=b.pilot.replace('exactly the same core visible text','different copy to influence readers');}],
 ['removed warmup disclosure',b=>{b.warmup=b.warmup.replace('Final Vestige may earn a commission','No commission disclosure');}],
 ['activated warmup purchase button',b=>{b.warmup=b.warmup.replace('disabled aria-disabled="true"','aria-disabled="false"');}],
 ['injected warmup form',b=>{b.warmup+='<form><input></form>';}],
 ['inserted warmup commercial outbound link',b=>{b.warmup=b.warmup.replace('<button class="z17-disabled"','<a href="https://zen12.com/getstarted">Buy now</a><button class="z17-disabled"');}]
 ];return tests.map(([name,apply])=>{const b=deep(bundle);apply(b);const res=audit(b);return {name,caught:res.total>res.passed,failures:res.failures}})}
module.exports={audit,mutations};
if(typeof require!=='undefined' && require.main===module){
 const fs=require('fs'),path=require('path'),dir=__dirname;
 const bundle={html:fs.readFileSync(path.join(dir,'INVESTIGATION_WP_DRAFT.html'),'utf8'),guide:fs.readFileSync(path.join(dir,'ZEN12_EXACT_OFFER_GUIDE.md'),'utf8'),matrix:JSON.parse(fs.readFileSync(path.join(dir,'EVIDENCE_MATRIX.json'),'utf8')),pilot:fs.readFileSync(path.join(dir,'ZEN12_FILM_PILOT_AND_PRIVACY_SPEC.md'),'utf8'),warmup:fs.readFileSync(path.join(dir,'ZEN12_WARMUP_PILOT_A_WP_DRAFT.html'),'utf8')};
 const base=audit(bundle),m=process.argv.includes('--mutation')?mutations(bundle):[];
 console.log(JSON.stringify({summary:{passed:base.passed,total:base.total,failed:base.failures,mutationsCaught:m.filter(x=>x.caught).length,mutationsTotal:m.length},mutations:m},null,2));
 process.exitCode=(base.passed===base.total && m.every(x=>x.caught))?0:1;
}
