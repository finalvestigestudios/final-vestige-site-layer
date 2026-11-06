// R166 zero-dependency source, security, disclosure, research-boundary & release-gate regression.
// Native execution (when repository checked out): node mind/r166/test_mind_r166.cjs
// The source test is necessary but NOT a substitute for real browser, merchant or accessibility QA.
'use strict';
const fs=require('node:fs'), path=require('node:path'), assert=require('node:assert/strict');
const root=__dirname;
const names={
 article:'the-face-that-changes-thatcher-illusion-INVESTIGATION-UNPUBLISHED.md',
 guide:'zen12-premium-exact-offer-independent-PRESELL-UNPUBLISHED.html',
 matrix:'product-claims-authorizations-revenue-gates.json',
 plan:'creator-fit-exact-offer-revenue-acceptance-and-ab-test.md',
 hub:'mind-hub-wordpress-block-COMPANION-UNPUBLISHED.html'
};
const data=Object.fromEntries(Object.entries(names).map(([k,n])=>[k,fs.readFileSync(path.join(root,n),'utf8')]));
function validate(d){
 const a=d.article,g=d.guide,p=d.plan,h=d.hub; const m=JSON.parse(d.matrix);let checks=0;
 const check=(truth,label)=>{assert.ok(truth,label);checks++};
 check(a.length>6000,'substantive original article');
 check(a.includes('Thatcher illusion')&&a.includes('face inversion'),'specific topic');
 check(a.includes('https://pubmed.ncbi.nlm.nih.gov/6999452/'),'primary Thompson paper');
 check(a.includes('https://pmc.ncbi.nlm.nih.gov/articles/PMC4191594/'),'local-feature primary study');
 check(a.includes('https://doi.org/10.1068/p7853'),'nonface counterexample');
 check(a.includes('https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'),'history integration');
 check(a.includes('https://finalvestige.com/2026/11/02/change-blindness/'),'perception integration');
 check(a.includes('https://finalvestige.com/focus/'),'existing free resource');
 check(a.includes('not a clinical intervention')&&a.includes('not a promise'),'no medical/profit promise');
 check(!/Buy using our affiliate link|href=[^>]*affid=/i.test(a),'independent investigation no affiliate sale copy');
 check(g.includes('<html lang="en">'),'HTML language');
 check(g.includes('name="viewport"'),'mobile viewport');
 check(g.includes('name="robots" content="noindex,nofollow"'),'private draft noindex');
 check(g.includes('class="skip"')&&g.includes('href="#main"'),'skip link');
 check(g.includes('id="main"'),'main landmark target');
 check(g.includes('role="img" aria-labelledby="art-title art-desc"'),'SVG accessible description');
 check(g.includes('prefers-reduced-motion'),'reduced motion');
 check(g.includes('focus-visible'),'keyboard focus');
 check(g.includes('@media(max-width:780px)'),'responsive breakpoint');
 check(g.includes('https://zen12.com/?no-popup=1'),'exact official product link');
 check(g.includes('48 MP3'),'specific merchant inventory');
 check(g.includes('twelve levels'),'offer-specific content');
 check(g.includes('$87.99')&&g.includes('November 6, 2026'),'historical seller display price');
 check(g.includes('not a promise')===false||g.includes('without product-specific'),'does not invent benefits'); // claim guards below stronger
 check(g.includes('without product-specific substantiation')||g.includes('without product-specific'),'evidence boundary');
 check(g.includes('Actual access and delivery are untested')||g.includes('actual access and delivery are untested'),'unverified delivery');
 check(g.includes('not entered checkout'),'no verified checkout assertion');
 check(g.includes('refund')&&g.includes('independently tested'),'qualified guarantee');
 check(/<button[^>]*disabled[^>]*>Explore Zen12 Premium/.test(g),'native disabled merchant button');
 check(g.includes('Affiliate disclosure for any future earning link'),'near-button disclosure text');
 check(g.indexOf('Affiliate disclosure for any future earning link')>g.indexOf('id="decision"'),'disclosure in decision section');
 check(g.indexOf('Affiliate disclosure for any future earning link')<g.indexOf('Explore Zen12 Premium — awaiting'),'disclosure directly before control');
 check(!/<script\b/i.test(g),'no JS');
 check(!/<form\b/i.test(g),'no duplicated signup');
 check(!/<iframe\b/i.test(g),'no external embeds');
 check(!/<video[^>]*\sautoplay(?:\s|>)/i.test(g)&&!/\sonload=|\sonclick=/i.test(g),'no autoplay or inline JS handler');
 check(!/href="[^"]*(?:affiliate_id|affid|refid|utm_campaign|clickbank|hop=)[^"]*"/i.test(g),'no affiliate redirect');
 check(!/href="https?:\/\/[^"]*\/(?:checkout|order|buy-now)[^"]*"/i.test(g),'no direct merchant checkout bypass');
 check(g.includes('42-second')&&g.includes('00:31–00:42'),'42 second storyboard');
 check(g.includes('No video file is embedded here'),'no false claim of playable video');
 check(g.includes('https://finalvestige.com/focus/'),'existing active free offer');
 check(h.includes('fv-mind-r166'),'isolated hub CSS class');
 check(h.includes('UNPUBLISHED — NO LINK'),'no unpublished article href');
 check(h.includes('href="https://finalvestige.com/focus/"'),'hub free-resource route');
 check(!/<form\b|<script\b|<iframe\b/i.test(h),'no hub forms/scripts/external embeds');
 check(h.includes('PR #172')&&h.includes('PR #49'),'canonical hub and homepage preserved');
 check(p.includes('HARD HOLD')&&p.includes('NOT COMPUTABLE'),'commerce and KPI gates');
 check(p.includes('utm_content=<real_grok_asset_id>'),'asset ID placeholder not guessed');
 check(p.includes('affiliate_click')&&p.includes('affiliate_confirmed_sale'),'click separate from paid sale');
 check(p.includes('1000 * sum(settled_net_revenue)'),'net per 1000 formula');
 check(p.includes('42-second')&&p.includes('text-only'),'controlled text-video hypothesis');
 check(p.includes('no new Jetpack list')||p.includes('Do not duplicate forms'),'one funnel');
 check(m.claims.length>=35,'evidence register at least 35 claims');
 check(Object.keys(m.sources).length>=15,'at least 15 sources');
 check(m.release_gates.length>=30,'at least 30 release gates');
 check(m.release_gates.every(x=>x.state==='CLOSED'),'all release gates closed');
 check(m.claims.some(x=>x.id==='Z12-10'&&x.classification==='seller-unsubstantiated-omit'),'equivalence claim excluded');
 check(m.claims.some(x=>x.id==='TI-05'&&x.classification==='independent-supported'),'2014 orientation claim qualified');
 check(m.commercial_authorization.named_final_vestige_acceptance===null,'no invented approval');
 check(m.commercial_authorization.earning_url===null,'no invented earning URL');
 check(m.commercial_authorization.payhip_paid_mind_sku===null,'no invented Payhip SKU');
 check(m.commercial_authorization.realized_net_revenue===null,'no invented revenue');
 check(m.commercial_authorization.qualified_human_sessions===null,'no invented human traffic');
 check(m.claims.every(x=>m.sources[x.source_id]),'all claims linked to source ID');
 return checks;
}
const baseline=validate(data); const mutationTests=[
 ['purchase-enabled','guide',s=>s.replace('type="button" disabled aria-disabled="true"','type="button"')],
 ['remove-proximate-disclosure','guide',s=>s.replace('Affiliate disclosure for any future earning link','Disclosure moved to footer')],
 ['inject-script','guide',s=>s.replace('</body>','<script src="https://track.example"></script></body>')],
 ['inject-form','guide',s=>s.replace('</body>','<form><input type="email"></form></body>')],
 ['inject-iframe','guide',s=>s.replace('</body>','<iframe src="https://player.example"></iframe></body>')],
 ['allow-autoplay','guide',s=>s.replace('</body>','<video autoplay></video></body>')],
 ['inject-inline-handler','guide',s=>s.replace('<main id="main"','<main onclick="evil()" id="main"')],
 ['remove-focus','guide',s=>s.replaceAll('https://finalvestige.com/focus/','/missing-focus/')],
 ['invent-product-efficacy','guide',s=>s.replace('without product-specific substantiation','with product-specific proof')],
 ['remove-viewport','guide',s=>s.replace('name="viewport"','name="desktop-only"')],
 ['remove-alt','guide',s=>s.replace('aria-labelledby="art-title art-desc"','aria-labelledby="no-desc"')],
 ['remove-keyboard','guide',s=>s.replaceAll('focus-visible','f0cus-visible')],
 ['remove-noindex','guide',s=>s.replace('noindex,nofollow','index,follow')],
 ['remove-video-timeline','guide',s=>s.replace('00:31–00:42','00:31–00:43')],
 ['inject-buy-checkout','guide',s=>s.replace('</body>','<a href="https://zen12.com/checkout">Pay now</a></body>')],
 ['inject-affiliate','guide',s=>s.replace('</body>','<a href="https://zen12.com/?affid=999">Earn</a></body>')],
 ['erase-history-source','article',s=>s.replaceAll('https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/','/')],
 ['erase-primary-paper','article',s=>s.replaceAll('https://pubmed.ncbi.nlm.nih.gov/6999452/','missing')],
 ['introduce-affiliate-in-investigation','article',s=>s+'\nBuy using our affiliate link today'],
 ['remove-hub-focus','hub',s=>s.replaceAll('href="https://finalvestige.com/focus/"','href="/missing/"')],
 ['hub-create-form','hub',s=>s+'<form><input type="email"></form>'],
 ['delete-campaign-id','plan',s=>s.replace('utm_content=<real_grok_asset_id>','utm_content=unknown')],
 ['equate-click-sale','plan',s=>s.replace('affiliate_confirmed_sale','outbound_only')],
 ['erase-revenue-formula','plan',s=>s.replace('1000 * sum(settled_net_revenue)','1000 * sum(clicks)')],
 ['open-one-gate','matrix',s=>s.replace('"state": "CLOSED"','"state": "OPEN"')],
 ['forge-affiliate','matrix',s=>s.replace('"earning_url": null','"earning_url": "https://example.com/aff"')],
 ['forge-payhip','matrix',s=>s.replace('"payhip_paid_mind_sku": null','"payhip_paid_mind_sku": "FAKE"')],
 ['forge-net-revenue','matrix',s=>s.replace('"realized_net_revenue": null','"realized_net_revenue": 1000')],
 ['falsify-seller-equivalence','matrix',s=>s.replace('"seller-unsubstantiated-omit"','"independent-supported"')]
];
let killed=0;for(const [name,key,edit] of mutationTests){const changed=edit(data[key]);assert.notEqual(changed,data[key],'mutation did not change '+name);try{validate({...data,[key]:changed})}catch(_){killed++;continue}throw Error('SURVIVED mutation: '+name)}
console.log('R166 PASS baseline assertions='+baseline+' ; unsafe mutations detected='+killed+'/'+mutationTests.length);
