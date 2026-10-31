'use strict';
/* Source-only R20 auditor. Read-only, no network, no runtime tracking.
 * Run after checkout: node mind/clever-hans-r20/qa.cjs --mutation
 */
const pathPrefix='mind/clever-hans-r20/';
const required=['investigation.blocks.html','zen12-independent-guide.md','zen12-pilot-A.blocks.html','zen12-pilot-B.blocks.html','video-poster.svg','zen12-film-draft.vtt','mind-archive-draft.blocks.html','EVIDENCE_MATRIX.json','ATTRIBUTION_EXPERIMENT.md'];
function audit(files){
  const checks=[];
  const check=(name,pass)=>checks.push({name,pass:!!pass});
  for(const n of required)check('required/'+n,typeof files[n]==='string'&&files[n].length>100);
  const article=files['investigation.blocks.html']||'';
  const guide=files['zen12-independent-guide.md']||'';
  const a=files['zen12-pilot-A.blocks.html']||'';
  const b=files['zen12-pilot-B.blocks.html']||'';
  const hub=files['mind-archive-draft.blocks.html']||'';
  const svg=files['video-poster.svg']||'';
  const vtt=files['zen12-film-draft.vtt']||'';
  const experiment=files['ATTRIBUTION_EXPERIMENT.md']||'';
  let evidence={sources:{},claims:[]};try{evidence=JSON.parse(files['EVIDENCE_MATRIX.json']||'{}')}catch(_){}
  const html=[article,a,b,hub];
  html.forEach((h,i)=>{
    const n=['article','text-A','video-B','mind-hub'][i];
    check(n+'/gutenberg-html-wrapper',h.trim().startsWith('<!-- wp:html -->')&&h.trim().endsWith('<!-- /wp:html -->'));
    check(n+'/single-h1',(h.match(/<h1\b/gi)||[]).length===1);
    check(n+'/aria-h1',/<h1\s+id="[^"]+"[^>]*>/.test(h)&&/aria-labelledby="[^"]+"/.test(h));
    check(n+'/mobile-css',/@media\s*\(max-width\s*:/.test(h));
    check(n+'/reduced-motion',h.includes('prefers-reduced-motion'));
    check(n+'/keyboard-focus',h.includes(':focus-visible'));
    check(n+'/no-script',!/<script\b/i.test(h));
    check(n+'/no-active-merchant-anchor',!/<a\b[^>]*href=["'][^"']*(?:zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com)/i.test(h));
    check(n+'/no-email-form',!/<form\b/i.test(h)&&!/<input\b[^>]*type=["']email/i.test(h));
    check(n+'/no-third-party-pixel',!/(?:googletagmanager\.com|google-analytics\.com|connect\.facebook\.net|pixel\.facebook\.com|doubleclick\.net)/i.test(h));
  });
  check('article/primary-numbers',article.includes('29 / 31')&&article.includes('3 / 31'));
  check('article/experimental-controls',article.includes('no person present could know')&&article.includes('two different'));
  check('article/counterevidence-dogs',article.includes('2012')&&article.includes('dogs')&&article.includes('no measurable improvement'));
  check('article/puys-limits',article.includes("can't")||article.includes('cannot retroactively'));
  check('article/puysegur-link',article.includes('https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'));
  check('article/focus-link',article.includes('https://finalvestige.com/focus/'));
  check('article/no-affiliate-recommendation',!/If you purchase through/.test(article));
  check('guide/official-product-exact-page',guide.includes('https://zen12.com/about')&&guide.includes('https://zen12.com/getstarted'));
  check('guide/not-firsthand',guide.includes('not been independently purchased'));
  check('guide/unsupported-equivalence',guide.includes('seller\'s efficacy claim')&&guide.includes('not an established measurement'));
  check('guide/free-baseline',guide.includes('A free twelve-minute baseline'));
  check('guide/disclosure',guide.includes('Final Vestige may earn a commission'));
  check('guide/FTC',guide.includes('ftc.gov'));
  check('offer/A-marker',a.includes('<!-- FV_VIDEO_SLOT -->'));
  const match=b.match(/<aside class="film-slot"[\s\S]*?<\/aside>/);
  check('offer/B-video-slot',!!match&&match[0].includes('Full accessible draft transcript'));
  check('offer/A-B-core-identical',!!match&&b.replace(match[0],'<!-- FV_VIDEO_SLOT -->')===a);
  check('offer/two-disabled-CTA-A',(a.match(/<button\b[^>]*disabled\b/gi)||[]).length===2);
  check('offer/two-disabled-CTA-B',(b.match(/<button\b[^>]*disabled\b/gi)||[]).length===2);
  check('offer/two-near-disclosures-A',(a.match(/class="disclosure"/g)||[]).length===2&&a.includes('may earn a commission at no additional cost to you'));
  check('offer/two-near-disclosures-B',(b.match(/class="disclosure"/g)||[]).length===2&&b.includes('may earn a commission at no additional cost to you'));
  check('offer/no-video-player-A',!/<video\b/i.test(a));
  check('offer/B-video-hidden',/<video\s+hidden\s+controls\s+playsinline\s+preload="none"/.test(b));
  check('offer/B-no-video-source',!/<source\b/i.test(b)&&!/<video[^>]*\ssrc\s*=/i.test(b));
  check('offer/no-autoplay',!/<video[^>]*\bautoplay\b/i.test(a)&&!/<video[^>]*\bautoplay\b/i.test(b));
  check('offer/references-seller-and-independent',a.includes('Seller')&&a.includes('Liebherr')&&a.includes('Ingendoh'));
  check('offer/free-focus',a.includes('https://finalvestige.com/focus/'));
  check('offer/no-false-live-test',/no affiliate relationship/i.test(a)&&b.includes('not yet available for playback'));
  check('hub/all-four-streams',['Perception &amp; Attention','History of Suggestion','Practice &amp; Reflection','Tools Under Review'].every(x=>hub.includes(x)));
  check('hub/no-broken-future-links',!/<a[^>]*href=["']\/mind\//i.test(hub));
  check('hub/puys-focus-editorial',hub.includes('https://finalvestige.com/focus/')&&hub.includes('https://finalvestige.com/editorial-standards/')&&hub.includes('puysegurs-animal-magnetism-files'));
  check('poster/original-descriptive-svg',svg.includes('xmlns="http://www.w3.org/2000/svg"')&&svg.includes('<title')&&svg.includes('<desc')&&svg.includes('29/31')&&svg.includes('3/31'));
  check('poster/no-network-content',!/<(?:image|script|foreignObject)\b/i.test(svg)&&!/https?:\/\//.test(svg.replace('http://www.w3.org/2000/svg','')));
  check('vtt/header',vtt.startsWith('WEBVTT'));
  check('vtt/timing',(vtt.match(/--> /g)||[]).length===8&&vtt.includes('00:00:42.000'));
  check('vtt/not-synced-claim',vtt.includes('DRAFT')&&vtt.includes('Do not claim synchronization'));
  check('vtt/verbal-commercial-disclosure',vtt.includes('may earn a commission'));
  check('experiment/anonymous-aggregate-only',experiment.includes('Persist aggregated counters only')&&experiment.includes('no affiliate purchase link'));
  check('experiment/off-by-default',experiment.includes('default is **OFF**'));
  check('experiment/no-false-unique-users',experiment.includes('do not claim unique visitors'));
  check('experiment/explicit-A-B',experiment.includes('EXACT same substantive markup'));
  check('experiment/needed-approval',experiment.includes('Written, account-specific Inspire3 affiliate acceptance verified'));
  check('evidence/source-count',Object.keys(evidence.sources||{}).length===17);
  check('evidence/claim-count',(evidence.claims||[]).length===60);
  check('evidence/unique-ids',new Set((evidence.claims||[]).map(c=>c.id)).size===60);
  check('evidence/valid-source-links',Object.values(evidence.sources||{}).every(s=>/^https:\/\//.test(s.url||'')));
  check('evidence/valid-refs',(evidence.claims||[]).every(c=>Array.isArray(c.source_ids)&&c.source_ids.length>0&&c.source_ids.every(id=>!!evidence.sources[id])));
  check('evidence/partner-approval-false',evidence.merchant_account_approval_verified===false);
  check('evidence/earning-link-null',evidence.earning_link===null);
  check('evidence/tracking-off',evidence.purchase_tracking_enabled===false);
  check('evidence/video-unhosted',evidence.commercial_video_hosted===false);
  check('evidence/experiment-off',evidence.registered_conversion_experiment===false);
  check('evidence/no-price',evidence.pricing_quoted===false);
  check('evidence/has-FTC',evidence.sources?.FTC_ENDORSE?.url?.includes('ftc.gov')&&evidence.sources?.FTC_HEALTH?.url?.includes('ftc.gov'));
  check('evidence/has-exact-offer',evidence.sources?.ZEN12_CHECKOUT?.url==='https://zen12.com/getstarted');
  check('evidence/seller-disposition',(evidence.claims||[]).some(c=>c.classification==='unsubstantiated_seller_efficacy'));
  const failed=checks.filter(x=>!x.pass);
  return {total:checks.length,passed:checks.length-failed.length,failed:failed.length,failures:failed.map(x=>x.name),checks};
}
function mutationChecks(files){
 const mutations={
  remove_disclosure:f=>f['zen12-pilot-A.blocks.html']=f['zen12-pilot-A.blocks.html'].replace(/If you purchase through a future approved link/, 'If approved'),
  enable_checkout:f=>f['zen12-pilot-A.blocks.html']=f['zen12-pilot-A.blocks.html'].replace('<button type="button" disabled','<button type="button"'),
  merchant_anchor:f=>f['zen12-pilot-A.blocks.html']+='\n<a href="https://zen12.com/getstarted">Buy</a>',
  enable_video:f=>f['zen12-pilot-B.blocks.html']=f['zen12-pilot-B.blocks.html'].replace('<video hidden','<video'),
  video_src:f=>f['zen12-pilot-B.blocks.html']=f['zen12-pilot-B.blocks.html'].replace('<video hidden','<video src="https://merchant.example/video.mp4" hidden'),
  autoplay:f=>f['zen12-pilot-B.blocks.html']=f['zen12-pilot-B.blocks.html'].replace('<video hidden','<video autoplay hidden'),
  tracking_script:f=>f['zen12-pilot-A.blocks.html']+='\n<script>track(1)</script>',
  signup_form:f=>f['zen12-pilot-A.blocks.html']+='\n<form><input type="email"></form>',
  lost_historic_number:f=>f['investigation.blocks.html']=f['investigation.blocks.html'].replace('29 / 31','29 / 32'),
  wrong_source_ref:f=>{const x=JSON.parse(f['EVIDENCE_MATRIX.json']);x.claims[0].source_ids=['DOES_NOT_EXIST'];f['EVIDENCE_MATRIX.json']=JSON.stringify(x)},
  fake_approval:f=>{const x=JSON.parse(f['EVIDENCE_MATRIX.json']);x.merchant_account_approval_verified=true;f['EVIDENCE_MATRIX.json']=JSON.stringify(x)},
  fake_earning_link:f=>{const x=JSON.parse(f['EVIDENCE_MATRIX.json']);x.earning_link='https://merchant.example/ref=fake';f['EVIDENCE_MATRIX.json']=JSON.stringify(x)},
  tracking_enabled:f=>{const x=JSON.parse(f['EVIDENCE_MATRIX.json']);x.purchase_tracking_enabled=true;f['EVIDENCE_MATRIX.json']=JSON.stringify(x)},
  omit_vtt_disclosure:f=>f['zen12-film-draft.vtt']=f['zen12-film-draft.vtt'].replace('may earn a commission','may get paid'),
  poster_remote_image:f=>f['video-poster.svg']=f['video-poster.svg'].replace('</svg>','<image href="https://third-party.test/a.png"/></svg>'),
  remove_hub_stream:f=>f['mind-archive-draft.blocks.html']=f['mind-archive-draft.blocks.html'].replace('Tools Under Review','Alternative Tools'),
  fake_unique_visitor_analytics:f=>f['ATTRIBUTION_EXPERIMENT.md']=f['ATTRIBUTION_EXPERIMENT.md'].replace('do not claim unique visitors','claim unique visitors'),
  no_footnote:f=>f['investigation.blocks.html']=f['investigation.blocks.html'].replaceAll('https://finalvestige.com/focus/','https://example.test/focus/')
 };
 return Object.entries(mutations).map(([name,mutate])=>{const changed={...files};mutate(changed);const result=audit(changed);return {mutation:name,caught:result.failed>0,failures:result.failures.slice(0,3)}});
}
module.exports={audit,mutationChecks,required,pathPrefix};
if(require.main===module){
 const fs=require('node:fs'), path=require('node:path');
 const files=Object.fromEntries(required.map(n=>[n,fs.readFileSync(path.join(__dirname,n),'utf8')]));
 const result=audit(files); console.log(JSON.stringify({total:result.total,passed:result.passed,failed:result.failed,failures:result.failures},null,2));
 if(process.argv.includes('--mutation')){const m=mutationChecks(files);console.log(JSON.stringify(m,null,2));if(m.some(x=>!x.caught))process.exitCode=1;}
 if(result.failed)process.exitCode=1;
}
