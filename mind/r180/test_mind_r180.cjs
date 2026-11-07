/* R180 source contract — node test_mind_r180.cjs
   Execute in Node >=18 from any cwd. Source-only checks; NOT a browser, checkout,
   video production, accessibility, affiliate acceptance, or sales verification.
*/
'use strict';
const fs=require('node:fs'), path=require('node:path');
const N=['the-moment-you-notice-mind-wandering-INVESTIGATION-UNPUBLISHED.md','zen12-premium-A-decision-text-UNPUBLISHED.html','zen12-premium-B-decision-optional-video-UNPUBLISHED.html','mind-archive-WORDPRESS-INTEGRATION-UNPUBLISHED.html','product-claim-source-and-activation-gates.json','offer-first-funnel-creator-fit-ab-revenue-acceptance.md'];
const load=()=>Object.fromEntries(N.map(n=>[n,fs.readFileSync(path.join(__dirname,n),'utf8')]));
const [articleName,Aname,Bname,hubName,claimName,planName]=N;
function validate(f) {
 const e=[]; let passed=0;
 function ok(condition,message){if(condition)passed++;else e.push(message);}
 const article=f[articleName], A=f[Aname], B=f[Bname], hub=f[hubName], plan=f[planName], matrix=JSON.parse(f[claimName]);
 ok(article.split(/\s+/).length>=1900,'Deep investigation >=1900 words');
 ok(/Hasenkamp/.test(article)&&/Mrazek/.test(article)&&/Lao/.test(article),'Nuanced three-study research');
 ok(/2016 systematic review/.test(article),'Opposing evidence summarized');
 ok(/Puységur/.test(article),'Historical source bridge');
 ok(/commercial: none/.test(article),'Research article commercial firewall');
 ok(!/awin1\.com|hop\.clickbank|aff_id=|affiliate_id=/.test(article),'No affiliate links in investigation');
 ok(/https:\/\/finalvestige\.com\/focus\//.test(article),'Existing Focus resource');
 ok(/https:\/\/pubmed\.ncbi\.nlm\.nih\.gov\/21782031/.test(article),'Primary fMRI citation');
 ok(/https:\/\/pubmed\.ncbi\.nlm\.nih\.gov\/23538911/.test(article),'Primary randomized study citation');
 ok(/not.*clinical|not a validated diagnostic|not clinical advice/i.test(article),'Exercise not clinical');
 const normalize=s=>s.replace(/<section class="section" aria-labelledby="shortstory">[\s\S]*?<\/section>/,'').replace('B — optional-video','A — text-only');
 ok(normalize(A)===normalize(B),'A/B identical except optional video concept block and title');
 for(const [label,h] of [['A',A],['B',B],['Hub',hub]]){
   ok(/<html lang="en">/.test(h),label+': language');
   ok(/<meta name="viewport"/.test(h),label+': responsive viewport');
   ok(/<meta name="robots" content="noindex,nofollow"/.test(h),label+': draft noindex');
   ok(/class="skip"/.test(h)&&/href="#main"/.test(h),label+': skip content');
   ok(/:focus-visible/.test(h),label+': visible keyboard focus');
   ok(/prefers-reduced-motion:reduce/.test(h),label+': respects reduced motion');
   ok(!/<script\b|<iframe\b|<form\b|<input\b|<link[^>]*stylesheet|onload=|onclick=/i.test(h),label+': no JS, frames, forms, external sheets or event handler');
   ok(!/<(?:video|audio)[^>]*\\bautoplay\\b|\\bautofocus(?:\\s|=)|meta http-equiv="refresh"/i.test(h),label+': no autoplay/focus hijack/redirect');
   ok(!/awin1\.com|hop\.clickbank|affiliate_id=|aff_id=|tracking\.js/i.test(h),label+': no earning URLs or duplicate trackers');
 }
 for(const [label,h] of [['A',A],['B',B]]){
   const block=h.indexOf('<div class="disclosure">'), btn=h.indexOf('class="hold" disabled aria-disabled="true"');
   ok(block>=0&&btn>block&&btn-block<560,label+': plain near-button FTC disclosure');
   ok(/No affiliate purchase link is active/.test(h),label+': prospectively worded commerce disclosure');
   ok(/<button[^>]*disabled aria-disabled="true"/.test(h),label+': native commerce disabled');
   ok(!/<a[^>]+href="[^"]*(?:checkout|order|buy-now|cart|cread\.php)/i.test(h),label+': no active checkout link');
   ok(/<a href="https:\/\/finalvestige\.com\/focus\//.test(h),label+': same free Focus path');
   ok(/<title>Zen12 Premium Buyer Decision/.test(h),label+': exact offer title');
   ok(!/guarantee(d|s)? better (focus|health|sleep)/i.test(h),label+': no invented efficacy guarantee');
 }
 ok(!/<video\b|<audio\b/i.test(A),'A no video or audio');
 ok(/Original static poster only/.test(B)&&/full timed 42-second video transcript/.test(B),'B poster and transcript but no fake MP4');
 ok(!/<video\b|<audio\b/.test(B),'B no falsely represented playable media');
 ok(/Perception &amp; Attention/.test(hub)&&/History of Suggestion/.test(hub)&&/Practice &amp; Reflection/.test(hub)&&/Tools Under Review/.test(hub),'Four archive streams');
 ok((hub.match(/href="https:\/\/finalvestige\.com\/focus\//g)||[]).length===1,'Hub one existing Focus path');
 ok(!/<form\b/.test(hub),'Hub no second opt-in form');
 ok(Array.isArray(matrix.sources)&&matrix.sources.length>=15,'Source matrix credible depth');
 ok(Array.isArray(matrix.claims)&&matrix.claims.length>=25,'Product claims comprehensive');
 ok(Array.isArray(matrix.gates)&&matrix.gates.length>=10,'Commercial gates comprehensive');
 ok(matrix.affiliate_earning_url===null&&matrix.commercial_cta_active===false,'No activated affiliate link');
 ok(matrix.merchant_publisher_acceptance==='NOT_VERIFIED','No publisher approval invented');
 ok(matrix.Payhip_owned_mind_product_verified===false,'No invented owned product');
 ok(matrix.paid_sales_verified===false&&matrix.realized_net_revenue===null,'No fabricated paid sales/revenue');
 ok(matrix.gates.some(g=>g.id==='partner_named_acceptance'&&g.status==='CLOSED'),'Partner approval hard hold');
 ok(matrix.gates.some(g=>g.id==='founder_release_approval'&&g.status==='CLOSED'),'Founder release hard hold');
 ok(matrix.sources.every(s=>/^https:\/\//.test(s.url)),'Sources have full URLs');
 ok(matrix.claims.every(c=>matrix.sources.some(s=>s.id===c.source_id)),'Every claim maps to a source');
 ok(/NOT COMPUTABLE/.test(plan),'Unknown denominator/revenue not converted to zero');
 ok(/actual.*asset_id|asset_id.*actual/i.test(plan),'Real Grok media ID not fabricated');
 ok(/affiliate_outbound/.test(plan)&&/paid_conversion_confirmed/.test(plan),'Clicks separated from confirmed purchase');
 ok(/no additional|No additional|No extra forms/.test(plan),'Single original funnel');
 ok(!/mailto:|password=|token=/.test(plan),'No leaked credentials in plan');
 return {passed,errors:e};
}
const files=load(), normal=validate(files);
if(normal.errors.length)throw new Error('Baseline failed: '+JSON.stringify(normal.errors));
const mutationCases=[
['activate button A',Aname,s=>s.replace('class="hold" disabled aria-disabled="true"','class="hold"')],
['activate button B',Bname,s=>s.replace('class="hold" disabled aria-disabled="true"','class="hold"')],
['remove A disclosure',Aname,s=>s.replace('<div class="disclosure">','<div class="unmarked">')],
['move B disclosure away',Bname,s=>s.replace('<div class="disclosure">','<div class="unmarked">')],
['add A affiliate url',Aname,s=>s.replace('</main>','<a href="https://www.awin1.com/cread.php?id=1">Buy</a></main>')],
['add B checkout link',Bname,s=>s.replace('</main>','<a href="https://example.com/checkout">Buy</a></main>')],
['add JS',Aname,s=>s.replace('</body>','<script>alert(1)</script></body>')],
['add iframe',Bname,s=>s.replace('</body>','<iframe src="https://elsewhere.example"></iframe></body>')],
['add form in hub',hubName,s=>s.replace('</main>','<form></form></main>')],
['add autoplay',Bname,s=>s.replace('</main>','<video autoplay></video></main>')],
['remove reduced motion',Aname,s=>s.replace('@media(prefers-reduced-motion:reduce)','@media(unknown)')],
['break A/B equivalence',Bname,s=>s.replace('Four questions before spending','Three questions before spending')],
['forge affiliate acceptance',claimName,s=>s.replace('"NOT_VERIFIED"','"ACCEPTED"')],
['forge earning URL',claimName,s=>s.replace('"affiliate_earning_url": null','"affiliate_earning_url": "https://affiliate.fake/link"')],
['forge merchant sales',claimName,s=>s.replace('"paid_sales_verified": false','"paid_sales_verified": true')],
['forge owned SKU',claimName,s=>s.replace('"Payhip_owned_mind_product_verified": false','"Payhip_owned_mind_product_verified": true')],
['remove research source',articleName,s=>s.replace('pubmed.ncbi.nlm.nih.gov/23538911','example.invalid/not-published')],
['remove historical link',articleName,s=>s.replace('Puységur','Nothing').replace(/Puységur/g,'Nothing')],
['remove net unknown language',planName,s=>s.replaceAll('NOT COMPUTABLE','UNKNOWN')],
['add tracking script hub',hubName,s=>s.replace('</body>','<script src="https://tracking.example/js"></script></body>')],
['remove article firewall',articleName,s=>s.replace('commercial: none','commercial: paid')],
['duplicate form A',Aname,s=>s.replace('</main>','<form action="/subscribe"></form></main>')]
];
let detected=0;const failures=[];
for(const [name,file,mutate] of mutationCases){const candidate={...files,[file]:mutate(files[file])};if(validate(candidate).errors.length)detected++;else failures.push(name);}
if(failures.length)throw new Error('Mutation missed: '+failures.join(', '));
console.log('R180 PASS: '+normal.passed+' baseline source assertions; '+detected+'/'+mutationCases.length+' unsafe mutations detected. SOURCE LEVEL ONLY; no browser, MP4, CI, checkout or sales acceptance.');
