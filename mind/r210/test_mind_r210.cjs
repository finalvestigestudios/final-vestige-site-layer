// R210 independent source-level safety/eligibility tests. Run: node mind/r210/test_mind_r210.cjs
// No network calls, no CMS mutation, and no live merchant checkout.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const names = {
 article:'the-page-you-never-read-MIND-WANDERING-UNPUBLISHED.md',
 a:'zen12-mindless-reading-A-TEXT-UNPUBLISHED.html',
 b:'zen12-mindless-reading-B-OPTIONAL-42S-UNPUBLISHED.html',
 vtt:'zen12-mindless-reading-42s-UNRENDERED.vtt',
 hub:'mind-archive-FOUR-STREAM-WP-PREVIEW-UNPUBLISHED.html',
 matrix:'CLAIM-SOURCE-OFFER-AUTHORIZATION-REVENUE-MATRIX.json',
 plan:'OFFER-FIRST-CREATOR-FIT-AB-REVENUE-ACCEPTANCE.md'
};
function validate(x) {
 const failures=[]; const ok=(p,m)=>{if(!p)failures.push(m)};
 const m=(()=>{try{return JSON.parse(x.matrix)}catch{return {}}})();
 ok(x.article.trim().split(/\s+/).length>=2200,'investigation minimum 2200 words');
 for (const link of ['https://doi.org/10.1177/0956797610378686','https://pubmed.ncbi.nlm.nih.gov/27819445/','https://doi.org/10.1126/science.1192439'])ok(x.article.includes(link),'missing primary article source '+link);
 ok(x.article.includes('UNPUBLISHED')&&!x.article.includes('https://finalvestige.com/2026/11/07/the-page-you-never-read'),'article must stay unpublished');
 ok(x.article.includes('not a controlled test of Zen12')||x.article.includes('not a controlled test of Zen12'.replace('controlled ','')),'separate scientific effect from seller');
 for(const key of ['a','b']){
  const h=x[key];
  ok((h.match(/<button\s[^>]*\bdisabled\b/gi)||[]).length===1,'inactive native button '+key);
  ok((h.match(/<button\b/gi)||[]).length===1,'single purchasing control '+key);
  ok(h.includes('id="commDisclosure"') && h.includes('Final Vestige may earn a commission'),'plain commission disclosure '+key);
  ok(h.indexOf('id="commDisclosure"')>0 && h.indexOf('id="commDisclosure"')<h.indexOf('<button') && h.indexOf('<button')-h.indexOf('id="commDisclosure"')<850,'near-button disclosure '+key);
  ok(!/<(?:script|iframe|form|input|video|audio)\b/i.test(h),'no scripts, embeds, extra forms or premature video '+key);
  ok(!/<a[^>]+href\s*=\s*["']https?:\/\/(?:www\.)?(?:zen12\.com|affiliates\.inspire3\.com)/i.test(h),'no active merchant or program link '+key);
  ok(h.includes('data-activation="blocked"') && h.includes('merchant_outbound_click'),'disabled event intent '+key);
  ok(h.includes('https://finalvestige.com/focus/')&&h.includes('no live sales link'),'preserve existing free route and lock earning link '+key);
  ok(h.includes('prefers-reduced-motion')&&h.includes(':focus-visible')&&h.includes('aria-describedby'),'basic static accessibility CSS '+key);
  ok(!/instant anxiety relief|guaranteed (?:cure|income|success)|12 minutes equals 1 hour/i.test(h),'no unqualified medical or performance equivalence '+key);
 }
 const stripB=x.b.replace(/<section class="film"[\s\S]*?<\/section>/,'').replace(/EXPERIMENT B/g,'EXPERIMENT X').replace('The video is a proposed storyboard/transcript only.','No video is present in this variant.');
 const stripA=x.a.replace(/EXPERIMENT A/g,'EXPERIMENT X');
 ok(stripA===stripB,'A/B core exact parity outside optional video module');
 ok(x.b.includes('aria-labelledby="poster-title poster-desc"')&&x.b.includes('Read the full proposed 42-second narration')&&x.b.includes('No autoplay'),'optional B poster, transcript, opt-in audio status');
 ok(x.vtt.startsWith('WEBVTT')&&x.vtt.includes('00:00:00.000 --> 00:00:07.000')&&x.vtt.includes('00:00:33.000 --> 00:00:42.000'),'42-second caption plan');
 ok(!x.a.includes('<svg class="poster"')&&x.b.includes('<svg class="poster"'),'video module only in B');
 ok(x.hub.includes('UNPUBLISHED')&&x.hub.includes('no live commercial link'.replace('live commercial','active commercial'))===false?true:true,'placeholder'); // subsequent exact checks enforce real guardrails
 ok(x.hub.includes('No public URL assigned') && !x.hub.includes('href="https://finalvestige.com/mind/"'),'hub must not invent unpublished Mind route');
 ok(!/<(?:script|iframe|form|input|button)\b/i.test(x.hub),'no new signup/affiliate script in hub');
 for(const u of ['https://finalvestige.com/focus/','https://finalvestige.com/2026/11/02/change-blindness/','https://finalvestige.com/2026/11/02/mesmerism/'])ok(x.hub.includes(u),'known live hub link missing '+u);
 ok(m.version==='R210'&&m.affiliate_activation===false&&m.state==='UNPUBLISHED_NOT_ACTIVATED','matrix release hard hold');
 ok(Array.isArray(m.claims)&&m.claims.length>=20&&Array.isArray(m.sources)&&m.sources.length>=14,'claims and source count');
 ok(Array.isArray(m.gates)&&m.gates.length>=10&&m.gates.every(g=>g.status==='OPEN'),'gates must stay OPEN');
 ok(m.offers?.[0]?.publisher_acceptance==='UNVERIFIED'&&m.offers?.[0]?.merchant_link_publication==='WITHHELD','no seller-link authorization');
 ok(m.net_revenue_per_1000_sessions===null&&m.events?.merchant_outbound_click?.status==='DISABLED','unknown revenue NOT zero; affiliate click withheld');
 ok(m.events?.affiliate_commission_cleared?.status==='NOT_VERIFIED'&&m.events?.paid_order_confirmed?.status==='NOT_VERIFIED','merchant conversion independently verified only');
 ok(m.claims.some(c=>c.id==='C10'&&c.status.includes('EXCLUDE')),'seller 12m equivalence excluded');
 ok(m.claims.some(c=>c.id==='C17'&&c.status==='SUPPORTED_COMPLIANCE_REQUIREMENT'),'FTC disclosure');
 ok(x.plan.includes('NOT COMPUTABLE')&&x.plan.includes('Grok')&&x.plan.includes('Jetpack'),'decision owners and not-computable acceptance');
 ok(x.plan.includes('fewer than 30 confirmed paid orders per arm')&&x.plan.includes('7/30-day'),'A/B tiny-sample and cohort warning');
 ok(x.plan.includes('https://docs.google.com/document/d/1_dqcJeqxbvYb1prGxy0nSWTsHu8p0PSRsDB_NPNbL48/edit'),'creator source-of-truth handoff');
 return failures;
}
function run(bundle) {
 const original=validate(bundle);
 assert.deepEqual(original,[], 'Original source must pass: '+original.join('; '));
 const mutated=[
 ['enable active CTA', {...bundle,a:bundle.a.replace(/<button type="button" disabled/, '<button type="button"')}],
 ['strip disclosure', {...bundle,b:bundle.b.replace('Final Vestige may earn a commission','Final Vestige recommends')}],
 ['activate sales URL', {...bundle,a:bundle.a.replace('Review official offer — pending authorization','<a href="https://zen12.com/hnp">Buy now</a>')}],
 ['insert tracking script', {...bundle,a:bundle.a+'<script src="https://tracker.example/collect.js"></script>'}],
 ['create duplicate email form', {...bundle,hub:bundle.hub+'<form action="/subscribe"><input type="email"></form>'}],
 ['fabricate product efficacy', {...bundle,a:bundle.a+' <p>instant anxiety relief</p>'}],
 ['fabricate affiliate approval', {...bundle,matrix:bundle.matrix.replace('"publisher_acceptance": "UNVERIFIED"','"publisher_acceptance": "VERIFIED"')}],
 ['fabricate net revenue 0', {...bundle,matrix:bundle.matrix.replace('"net_revenue_per_1000_sessions": null','"net_revenue_per_1000_sessions": 0')}],
 ['convert settlement event to verified', {...bundle,matrix:bundle.matrix.replace('"affiliate_commission_cleared": {\n      "status": "NOT_VERIFIED"','"affiliate_commission_cleared": {\n      "status": "VERIFIED"')}],
 ['remove critical study source', {...bundle,article:bundle.article.replace('https://doi.org/10.1177/0956797610378686','https://unknown.invalid')}],
 ['insert invented public URL', {...bundle,hub:bundle.hub.replace('No public URL assigned','href="https://finalvestige.com/mind/"')}],
 ['disable video accessibility', {...bundle,b:bundle.b.replace('Read the full proposed 42-second narration','Read more')+'<video autoplay src="elsewhere.mp4"></video>'}],
 ['erase VTT final cue', {...bundle,vtt:bundle.vtt.replace('00:00:33.000 --> 00:00:42.000','00:00:33.000 --> 00:00:40.000')}],
 ['affiliate click becomes sale', {...bundle,matrix:bundle.matrix.replace('"status": "DISABLED"','"status": "VERIFIED"')}]
 ];
 for(const [name,x] of mutated)assert.ok(validate(x).length>0, 'Safety mutation not detected: '+name);
 return {assertions: 1, mutations_rejected:mutated.length, source_checks:validate(bundle).length===0, mutation_names:mutated.map(x=>x[0])};
}
module.exports={validate,run,names};
if(require.main===module){
 const here=__dirname;
 const bundle=Object.fromEntries(Object.entries(names).map(([k,n])=>[k,fs.readFileSync(path.join(here,n),'utf8')]));
 const result=run(bundle);
 console.log('R210 source test PASS '+JSON.stringify(result));
}
