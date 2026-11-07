'use strict';
/* R192: purely local/source-only checks. Run from repository root:
      node mind/r192/test_mind_r192.cjs
   No network calls or production writes. V8-compatible standalone Node CommonJS.
   Assertions are NOT real-browser, consent, checkout, seller authorization or accessibility verification.
*/
const FILES={
 article:'mind/r192/the-hand-that-wasnt-yours-RUBBER-HAND-INVESTIGATION-UNPUBLISHED.md',
 ledger:'mind/r192/CLAIMS-PRODUCT-AUTHORIZATION-PAID-REVENUE-GATES.json',
 plan:'mind/r192/ONE-OFFER-THREE-CREATOR-FITS-PAID-PROOF-ACCEPTANCE.md',
 hub:'mind/r192/mind-archive-FOUR-STREAM-WP-REVIEW-UNPUBLISHED.html',
 inherited:'mind/r191/the-face-you-didnt-choose-CHOICE-BLINDNESS-INVESTIGATION-UNPUBLISHED.md',
 A:'mind/r188/zen12-variant-A-independent-text-UNPUBLISHED.html',
 B:'mind/r188/zen12-variant-B-optional-42s-storyboard-UNPUBLISHED.html'
};
function elements(html,tag){return Array.from(html.matchAll(new RegExp('<'+tag+'\\b[^>]*>', 'gi')),m=>m[0]);}
function nativeDisabled(tag){return /(?:\s|^)disabled(?:\s|>|=)/i.test(tag);}
function withoutFilm(html){return html.replace(/<section id="optional-film" class="film"[\s\S]*?<\/section>/i,'');}
function check(f){
 const checks=[],ok=(test,label)=>checks.push({label,pass:!!test});
 let d=null;try{d=JSON.parse(f.ledger)}catch(_){}
 const buttons=elements(f.hub,'button'),links=Array.from(f.hub.matchAll(/<a\b[^>]*href=["']([^"']+)["'][^>]*>/gi),x=>x[1]);
 const actualSources=d?.source_links||[],claims=d?.claim_decisions||[],gates=d?.release_gates||[];
 const ids=new Set(actualSources.map(x=>x.id)),g=(key)=>gates.find(x=>x.id===key);
 ok(f.article.trim().split(/\s+/).length>=2000,'substantive original experiment narrative >=2000 words');
 for(const term of ['Botvinick','Cohen','Tsakiris','Haggard','Rohde','Ehrsson','proprioceptive drift','synchronized','Puységur','UNPUBLISHED'])ok(f.article.includes(term),'article sourced method/limitation term: '+term);
 for(const link of ['https://doi.org/10.1038/35784','https://pubmed.ncbi.nlm.nih.gov/15709864/','https://doi.org/10.1371/journal.pone.0021659','https://www.psy.ox.ac.uk/publication/19214','https://finalvestige.com/focus/'])ok(f.article.includes(link),'article contains verified primary/reference link: '+link);
 ok(/does not test either product/i.test(f.article),'no study->branded audio outcome inference');
 ok(/not a validated cognitive test/i.test(f.article),'free exercise not represented as validated test');
 ok(!/guaranteed focus gains|proves Zen12 works|rubber hand proves hypnosis/i.test(f.article),'avoid unsupported branded outcomes');
 ok(!/awin1\.com\/cread|hop\.clickbank|affiliate\/ref=/i.test(f.article),'no earning link embedded in investigation');
 ok(f.inherited.includes('a concealed slip was removed to reveal wording with the opposite meaning'),'precise R191 experiment-mechanism correction retained');
 ok(!f.inherited.includes('an altered mark or answer as a trustworthy reminder'),'old misleading paper mechanism removed');
 ok(d&&d.milestone==='R192','ledger R192 JSON');
 ok(actualSources.length>=18,'substantial sourced claims register');
 ok(claims.length>=25,'claim decisions >=25');
 ok(gates.length>=15,'commercial release gates >=15');
 ok(ids.size===actualSources.length,'no duplicated source IDs');
 ok(claims.every(c=>ids.has(c.source_id)),'all ledger claims resolve to real source ID');
 ok(actualSources.every(s=>/^https:\/\//.test(s.url)),'actual HTTPS source URLs, not placeholders');
 ok(g('publisher_named_acceptance')?.status==='BLOCKED','named partner approval blocked');
 ok(g('affiliate_channels')?.status==='BLOCKED','channel authorization blocked');
 ok(g('authorized_url')?.status==='BLOCKED','earning URL blocked');
 ok(g('fv_owned_mind_sku')?.status==='UNKNOWN','owned fallback product not invented');
 ok(g('paid_net_1k')?.status==='NOT_COMPUTABLE','net revenue cannot be computed');
 ok(g('cms_release')?.status==='BLOCKED','production release blocked');
 ok(d?.controls?.affiliate_earning_link_enabled===false&&d?.controls?.merchant_cta_enabled===false,'explicit merchant off flags');
 ok(d?.controls?.additional_signup_form===false&&d?.controls?.published_to_wordpress===false,'no duplicate signup/live claim');
 ok(claims.some(c=>c.id==='zen_equiv'&&c.decision.startsWith('REJECT')),'invalid equivalence claim rejected');
 ok(claims.some(c=>c.id==='affiliate_click'&&c.decision.includes('NON_REVENUE')),'clicks explicitly non-sale');
 ok(f.plan.includes('utm_content={REAL_GROK_ASSET_ID}'),'UTM uses real media ID requirement');
 ok(f.plan.includes('Grok retains original creative'),'Grok ownership preserved');
 ok(f.plan.includes('Praxxis owns independent'),'Praxxis coordination preserved');
 ok(f.plan.includes('NET')||f.plan.includes('net revenue'),'net revenue metric prioritized');
 ok(f.plan.includes('NOT COMPUTABLE')&&f.plan.includes('7-day')&&f.plan.includes('30-day'),'cohorts and no fabricated revenue');
 ok(/merchant\/affiliate exports/i.test(f.plan)&&f.plan.includes('refunds/chargebacks'),'merchant proof terms');
 ok(f.plan.includes('https://finalvestige.com/focus/'),'single Focus CTA destination');
 ok(f.plan.includes('HARD HOLD'),'auth blocker explicit');
 ok(f.plan.includes('R188'),'A/B inherited, not another merchant-page proliferation');
 ok(f.plan.includes('no-JS')||f.plan.includes('no autoplay'),'no forced video');
 ok(f.plan.includes('Clicks, leads, wishlist or checkout starts never count as paid sales.'),'outbound clicks not sale');
 ok(f.hub.includes('<meta name="robots" content="noindex,nofollow">'),'unpublished hub noindex');
 ok(f.hub.includes('id="content"')&&f.hub.includes('href="#content"'),'functional skip target');
 ok(f.hub.includes('id="page-title"')&&f.hub.includes('aria-labelledby="page-title"'),'hero aria title');
 ok(f.hub.includes('id="buyer"')&&f.hub.includes('href="#buyer"'),'buyer section anchor');
 ok(f.hub.includes('id="merchant-gate"')&&f.hub.includes('aria-describedby="merchant-gate"'),'disabled merchant explanation accessible');
 ok(elements(f.hub,'button').length===1,'one and only one merchant control');
 ok(buttons.length===1&&buttons.every(nativeDisabled),'native HTML disabled on merchant controls');
 ok(/If you purchase through a future approved earning link, Final Vestige may earn a commission at no additional cost to you\./.test(f.hub),'explicit near-CTA commission disclosure');
 ok(f.hub.indexOf('Final Vestige may earn a commission')<f.hub.indexOf('<button')&&f.hub.indexOf('<button')-f.hub.indexOf('Final Vestige may earn a commission')<250,'disclosure physically adjacent to merchant control');
 ok(f.hub.includes('Seller')||f.hub.includes('seller'),'vendor descriptions identified as vendor');
 ok(f.hub.includes('not a verified final checkout charge'),'avoids unverified checkout total');
 ok(/<a\b[^>]*href="https:\/\/zen12\.com\/hnp"[^>]*rel="nofollow noopener noreferrer"/.test(f.hub),'vendor source link informational and non-earning');
 ok(!links.some(x=>/awin1\.com|hop\.clickbank|\/cread\.php|affiliate[?/]ref=/.test(x)),'no affiliate earning URLs');
 ok(!/<form\b/i.test(f.hub),'no duplicate subscriber form');
 ok(!/<script\b/i.test(f.hub),'no active JS, analytics or third-party scripts');
 ok(!/<(?:video|iframe|audio)\b/i.test(f.hub),'no autoplay/video embed/iframe');
 ok(!/autoplay|autofocus/i.test(f.hub),'no autoplay/autofocus');
 ok(f.hub.includes('@media(prefers-reduced-motion:reduce)'),'reduced motion');
 ok(f.hub.includes('@media(max-width:390px)'),'small viewport design rules');
 ok(f.hub.includes('https://finalvestige.com/2026/11/02/change-blindness/'),'previously checked canonical Change Blindness route');
 ok(f.hub.includes('https://finalvestige.com/2026/11/02/mesmerism/'),'corrected canonical Mesmerism route');
 ok(f.hub.includes('https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'),'existing Puységur article');
 ok(f.hub.includes('https://finalvestige.com/focus/'),'existing Focus destination retained');
 ok(!/<a\b[^>]*href=["'][^"']*mind\/r19[0-9]/i.test(f.hub),'unpublished GitHub paths not promoted as live');
 ok(elements(f.A,'button').length>0&&elements(f.A,'button').every(nativeDisabled),'inherited A merchant button natively disabled');
 ok(elements(f.B,'button').length>0&&elements(f.B,'button').every(nativeDisabled),'inherited B merchant button natively disabled');
 ok(!/<script\b/i.test(f.A)&&!/<script\b/i.test(f.B),'inherited guides no active tracking script');
 ok(f.B.includes('optional-film')&&withoutFilm(f.B)===f.A,'A/B only difference is optional film section');
 ok(!/<video\b/i.test(f.B)&&!/<(?:video|audio)[^>]*\sautoplay(?:\s|>|=)/i.test(f.B),'film remains storyboard, no rendered autoplay');
 return checks;
}
function mutations(files){
 const scenarios=[
  ['hub merchant button activation',f=>f.hub=f.hub.replace('<button type="button" disabled','<button type="button"')],
  ['hub earning link',f=>f.hub=f.hub.replace('href="#buyer"','href="https://www.awin1.com/cread.php?s=1"')],
  ['hub missing disclosure',f=>f.hub=f.hub.replace('Final Vestige may earn a commission at no additional cost to you','Final Vestige may be compensated')],
  ['hub extra signup',f=>f.hub=f.hub.replace('</main>','<form action="/subscribe"><input name="email"></form></main>')],
  ['hub injected analytics',f=>f.hub=f.hub.replace('</main>','<script src="https://thirdparty.example/track.js"></script></main>')],
  ['hub wrong Mesmerism slug',f=>f.hub=f.hub.replace('/2026/11/02/mesmerism/','/2026/11/02/mesmerism-history/')],
  ['hub autoplay iframe',f=>f.hub=f.hub.replace('</main>','<iframe autoplay src="https://example.com"></iframe></main>')],
  ['hub disclosed focus replaced',f=>f.hub=f.hub.replaceAll('https://finalvestige.com/focus/','https://example.com/subscribe')],
  ['article false branded proof',f=>f.article=f.article.replace('Nothing physically transferred','rubber hand proves hypnosis: Nothing physically transferred')],
  ['article missing primary 1998 DOI',f=>f.article=f.article.replaceAll('https://doi.org/10.1038/35784','https://example.com')],
  ['ledger fake publisher authorization',f=>{let d=JSON.parse(f.ledger);d.release_gates.find(x=>x.id==='publisher_named_acceptance').status='VERIFIED';f.ledger=JSON.stringify(d)}],
  ['ledger fake earning URL',f=>{let d=JSON.parse(f.ledger);d.release_gates.find(x=>x.id==='authorized_url').status='VERIFIED';f.ledger=JSON.stringify(d)}],
  ['ledger fake Payhip SKU',f=>{let d=JSON.parse(f.ledger);d.release_gates.find(x=>x.id==='fv_owned_mind_sku').status='VERIFIED';f.ledger=JSON.stringify(d)}],
  ['ledger fake paid proof',f=>{let d=JSON.parse(f.ledger);d.release_gates.find(x=>x.id==='paid_net_1k').status='VERIFIED';f.ledger=JSON.stringify(d)}],
  ['ledger broken source reference',f=>{let d=JSON.parse(f.ledger);d.claim_decisions[0].source_id='nonexistent';f.ledger=JSON.stringify(d)}],
  ['plan fabricate media ID',f=>f.plan=f.plan.replace('utm_content={REAL_GROK_ASSET_ID}','utm_content=fake')],
  ['plan affiliate sale from click',f=>f.plan=f.plan.replace('Clicks, leads, wishlist or checkout starts never count as paid sales.','Clicks, leads, wishlist or checkout starts should count as paid sales.')],
  ['A button activated',f=>f.A=f.A.replace(/\sdisabled(?=[\s=>])/i,'')],
  ['B button activated',f=>f.B=f.B.replace(/\sdisabled(?=[\s=>])/i,'')],
  ['R191 mechanism correction reverted',f=>f.inherited=f.inherited.replace('a concealed slip was removed to reveal wording with the opposite meaning','a rating mark was moved on the page')]
 ];
 const baseline=check(files),failures=[];
 for(const [name,mutate] of scenarios){
  const next={...files};mutate(next);
  const after=check(next);if(!after.some((r,i)=>baseline[i].pass&&!r.pass))failures.push(name);
 }
 return {total:scenarios.length,caught:scenarios.length-failures.length,failures};
}
if(require.main===module){
 const fs=require('fs');
 const files=Object.fromEntries(Object.entries(FILES).map(([k,v])=>[k,fs.readFileSync(v,'utf8')]));
 const checks=check(files),bad=checks.filter(x=>!x.pass),mutation=mutations(files);
 for(const x of bad)console.error('FAIL '+x.label);
 console.log('R192 source assertions: '+(checks.length-bad.length)+'/'+checks.length+' PASS');
 console.log('R192 adversarial modifications detected: '+mutation.caught+'/'+mutation.total);
 if(mutation.failures.length)console.error('Escaped mutations: '+mutation.failures.join(', '));
 if(bad.length||mutation.failures.length)process.exitCode=1;
}
module.exports={check,mutations,FILES};