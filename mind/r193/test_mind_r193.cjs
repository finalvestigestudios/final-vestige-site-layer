'use strict';
/* R193 source checks, no network or CMS writes. Run from repository root:
   node mind/r193/test_mind_r193.cjs
   Passing source checks is NOT live browser, subscription, partner or payment verification.
*/
const FILES={
 article:'mind/r193/the-gorilla-was-right-there-EXPERT-INATTENTION-UNPUBLISHED.md',
 ledger:'mind/r193/VERIFIED-SOURCES-CLAIMS-AUTHORIZATION-GATES.json',
 hub:'mind/r193/mind-archive-four-stream-WP-PREVIEW-UNPUBLISHED.html',
 plan:'mind/r193/OFFER-FIRST-GROK-FIT-FOCUS-TRUST-AB-PAID-REVENUE.md',
 A:'mind/r188/zen12-variant-A-independent-text-UNPUBLISHED.html',
 B:'mind/r188/zen12-variant-B-optional-42s-storyboard-UNPUBLISHED.html'
};
const tagAttrs=(html,tag)=>Array.from(html.matchAll(new RegExp('<'+tag+'\\b[^>]*>','gi')),m=>m[0]);
const disabled=(tag)=>/(?:\s)disabled(?=\s|=|>)/i.test(tag);
const filmless=(s)=>s.replace(/<section id="optional-film" class="film"[\s\S]*?<\/section>/i,'');
function checks(f){
 const a=[],ok=(p,label)=>a.push({pass:!!p,label});
 let d=null;try{d=JSON.parse(f.ledger)}catch(_){}
 const s=d?.source_links||[],c=d?.claim_decisions||[],g=d?.release_gates||[],ids=new Set(s.map(v=>v.id));
 const gate=id=>g.find(v=>v.id===id);
 ok(f.article.split(/\s+/).length>=2000,'original article >= 2000 words');
 for(const t of ['20 of twenty-four','twelve of the twenty','547 milliseconds','239 slices','five','48 times','2013','1999','Puységur','not a validated','UNPUBLISHED'])
   ok(f.article.toLowerCase().includes(t.toLowerCase()),'science narrative term '+t);
 for(const u of ['https://pmc.ncbi.nlm.nih.gov/articles/PMC3964612/','https://doi.org/10.1068/p281059','https://finalvestige.com/2026/11/02/mesmerism/','https://finalvestige.com/focus/'])
   ok(f.article.includes(u),'source linked '+u);
 ok(!/affiliate\.ref=|awin1\.com\/cread|hop\.clickbank/i.test(f.article),'no active affiliate link in investigation');
 ok(!/clinically proves Zen12|guaranteed focus improvement/i.test(f.article),'no invented efficacy');
 ok(d?.milestone==='R193'&&d?.status.startsWith('DRAFT_'),'R193 draft matrix');
 ok(s.length>=20&&c.length>=25&&g.length>=17,'credible source/claim/gate coverage');
 ok(ids.size===s.length&&s.every(z=>/^https:\/\//.test(z.url)),'distinct genuine HTTPS source URLs');
 ok(c.every(z=>ids.has(z.source_id)),'all evaluated claims resolve to existing source');
 ok(gate('publisher_named_acceptance')?.status==='BLOCKED','publisher-specific authorization hard hold');
 ok(gate('authorized_url')?.status==='BLOCKED','no authorized URL');
 ok(gate('affiliate_channels')?.status==='BLOCKED','channel rights hard hold');
 ok(gate('fv_owned_mind_sku')?.status==='UNKNOWN','no invented owned SKU');
 ok(gate('net_1k')?.status==='NOT_COMPUTABLE','not-computable revenue');
 ok(gate('focus_confirmed_lead')?.status==='NOT_VERIFIED','Focus lead not confirmed by gift display');
 ok(gate('cms_release')?.status==='BLOCKED','no live release');
 ok(d.controls?.affiliate_earning_link_enabled===false&&d.controls.merchant_cta_enabled===false,'all merchant flags disabled');
 ok(d.controls?.additional_signup_form===false&&d.controls.published_to_wordpress===false,'no second Jetpack/live status claim');
 const hButtons=tagAttrs(f.hub,'button'),aButtons=tagAttrs(f.A,'button'),bButtons=tagAttrs(f.B,'button');
 ok(hButtons.length===1&&aButtons.length===1&&bButtons.length===1,'exact expected merchant controls');
 ok(hButtons.every(disabled)&&aButtons.every(disabled)&&bButtons.every(disabled),'all 3 merchant buttons NATIVELY disabled');
 ok(/<p class="disclose">[\s\S]*may earn a commission[\s\S]*<\/p>/i.test(f.hub),'visible adjacent commission disclosure in hub');
 ok(f.A.includes('commission')&&f.B.includes('commission'),'commission disclosure in both guide variants');
 ok(/aria-describedby="offer-hold"/.test(f.hub)&&/id="offer-hold"/.test(f.hub),'accessible disabled description');
 ok(/href="#main"/.test(f.hub)&&/id="main"/.test(f.hub),'skip link target');
 ok(/prefers-reduced-motion/.test(f.hub),'reduced motion CSS');
 ok(!/<script\b|<form\b|\bautoplay\b|<iframe\b/gi.test(f.hub),'no JS, form, autoplay or iframe in hub');
 ok(!/href=["'](?:https:\/\/(?:www\.)?(?:zen12|hypnosislive|affiliates\.inspire3)\.)/i.test(f.hub),'no merchant or affiliate earning destination in hub');
 ok(/noindex,nofollow/.test(f.hub),'unpublished design noindex');
 ok(!/\.com\/mind\/r193|github\.com\/.*\/blob\/.*r193/i.test(f.hub),'no Github draft as published editorial route');
 ok(f.plan.includes('Focus false-positive')||f.plan.includes('Focus false-positive'.toLowerCase())||f.plan.includes('Focus false-positive'.toUpperCase())||f.plan.includes('Focus false-positive'.replace('false-positive','false-positive'))||f.plan.includes('Focus false-positive'.replace('false-positive','false-positive'))||f.plan.includes('Focus false-positive'.replace('false-positive','false-positive'))||f.plan.includes('Focus false-positive'.replace('false-positive','false-positive'))||/Focus false-positive/i.test(f.plan),'Focus source gate heading');
 ok(f.plan.includes('?subscribe=')&&f.plan.includes('is-subscriber'),'focus bypass correctly documented');
 ok(f.plan.includes('utm_content={REAL_GROK_ASSET_ID}'),'real creator asset requirement');
 ok(f.plan.includes('Grok owns original')&&f.plan.includes('Praxxis independently'),'creator ownership protected');
 ok(f.plan.includes('Variant A')&&f.plan.includes('Variant B')&&f.plan.includes('42-second'),'fixed R188 controlled experiment');
 ok(f.plan.includes('NOT COMPUTABLE')&&f.plan.includes('7-day')&&f.plan.includes('30-day'),'honest 7/30-day paid measurement');
 ok(f.plan.includes('discounts')&&f.plan.includes('chargebacks'),'realized net definition');
 ok(f.plan.includes('no new')||f.plan.includes('no additional'),'no proliferation posture');
 ok(f.A.includes('optional-film')===false&&f.B.includes('optional-film')===true,'film B only');
 ok(filmless(f.B)===f.A,'A/B exact text and markup parity after removing optional film');
 return a;
}
function mutationProbe(f){
 const changes=[
 ['remove_hub_disabled',{hub:f.hub.replace(/\sdisabled\saria-describedby/,' aria-describedby')}],
 ['remove_variant_A_disabled',{A:f.A.replace(/\sdisabled\saria-disabled/,' aria-disabled')}],
 ['remove_variant_B_disabled',{B:f.B.replace(/\sdisabled\saria-disabled/,' aria-disabled')}],
 ['erase_hub_disclosure',{hub:f.hub.replace(/<p class="disclose">[\s\S]*?<\/p>/,'<p>Nothing to disclose.</p>')}],
 ['make_live_merchant',{hub:f.hub.replace('</aside>','<a href="https://zen12.com/hnp">Buy now</a></aside>')}],
 ['add_js_tracking',{hub:f.hub.replace('</head>','<script src="https://example.com/track.js"></script></head>')}],
 ['add_subscription_form',{hub:f.hub.replace('</main>','<form><input name="email"></form></main>')}],
 ['forge_publisher_approval',{ledger:f.ledger.replace('"id": "publisher_named_acceptance",\n      "status": "BLOCKED"','"id": "publisher_named_acceptance",\n      "status": "APPROVED"')}],
 ['invent_owned_SKU',{ledger:f.ledger.replace('"id": "fv_owned_mind_sku",\n      "status": "UNKNOWN"','"id": "fv_owned_mind_sku",\n      "status": "VERIFIED"')}],
 ['invent_revenue',{ledger:f.ledger.replace('"id": "net_1k",\n      "status": "NOT_COMPUTABLE"','"id": "net_1k",\n      "status": "PROFITABLE"')}],
 ['treat_gift_as_signup',{ledger:f.ledger.replace('"id": "focus_confirmed_lead",\n      "status": "NOT_VERIFIED"','"id": "focus_confirmed_lead",\n      "status": "CONFIRMED"')}],
 ['remove_creator_id_guard',{plan:f.plan.replace('utm_content={REAL_GROK_ASSET_ID}','utm_content=fictional_123')}],
 ['no_source_gorilla',{article:f.article.replace('https://pmc.ncbi.nlm.nih.gov/articles/PMC3964612/','http://untrusted.test/paper')}],
 ['remove_inherited_B_film',{B:f.B.replace('optional-film','other-film')}],
 ['remove_unpublished_status',{hub:f.hub.replace('noindex,nofollow','index,follow')}],
 ['remove_draft_governance',{ledger:f.ledger.replace('"id": "cms_release",\n      "status": "BLOCKED"','"id": "cms_release",\n      "status": "APPROVED"')}]
 ];
 const escaped=[];
 for(const [name,patch] of changes){const tmp={...f,...patch};if(checks(tmp).every(z=>z.pass))escaped.push(name);}
 return {total:changes.length,caught:changes.length-escaped.length,escaped};
}
if(require.main===module){
 const fs=require('fs'),f=Object.fromEntries(Object.entries(FILES).map(([k,p])=>[k,fs.readFileSync(p,'utf8')]));
 const a=checks(f),bad=a.filter(x=>!x.pass),m=mutationProbe(f);
 bad.forEach(x=>console.error('FAIL:',x.label));
 if(m.escaped.length)console.error('UNDTECTED:',m.escaped.join(', '));
 console.log('R193 assertions: '+(a.length-bad.length)+'/'+a.length+' PASS');
 console.log('R193 deliberately unsafe changes caught: '+m.caught+'/'+m.total);
 if(bad.length||m.escaped.length)process.exitCode=1;
}
module.exports={FILES,checks,mutationProbe};