/* R152: execute with node mind/r152/test_mind_r152.cjs; no network calls or live writes. */
'use strict';
const fs = require('fs'); const path = require('path'); const assert = require('assert');
const d=__dirname; const get=n=>fs.readFileSync(path.join(d,n),'utf8');
function verify(a,g,h,j) {
let checks=0; function ok(v,msg){assert.ok(v,msg);checks++}
const m=JSON.parse(j);
ok(a.includes('Roediger')&&a.includes('McDermott')&&a.includes('Freyd'), 'sources and counter-generalization');
ok(a.includes('40%')&&a.includes('55%'), 'study numerical context');
ok(a.includes('**not**')||a.includes('not a'), 'limitations');
ok(a.includes('UNPUBLISHED')&&a.includes('no earning link'), 'article unreleased');
ok(a.includes('Puységur')&&a.includes('misleading questions'), 'history and suggestion');
ok(a.includes('https://finalvestige.com/focus/'), 'existing single Focus destination');
ok(!/(affiliate_id=|affiliateid=|clickbank\.|ref_id=|utm_content=ACTUAL)/i.test(a), 'no invented attribution links in article');
ok(g.includes('R149')&&g.includes('Total Focus'), 'reuse eligible exact guide');
ok(g.includes('HARD HOLD')&&g.includes('Payhip'), 'commercial gate and fallback');
ok(g.includes('NOT COMPUTABLE')&&g.includes('7d/30d'), 'measurable but not fabricated revenue');
ok(g.includes('GROK_ASSET_ID')&&g.includes('UNKNOWN'), 'do not fabricate asset ID');
ok(g.includes('consent')&&g.includes('qualified-human'), 'privacy and useful denominator');
ok(g.includes('refund')&&g.includes('merchant_confirmed_order'), 'real paid event separate from click');
ok(g.includes('hypothesis')&&g.includes('40-second'), 'unrun experiment');
ok(h.includes('data-release="HARD_HOLD"'), 'visible release gate');
ok(h.includes('data-affiliate-approval="UNVERIFIED"'), 'affiliate not approved');
ok(/<button[^>]*\sdisabled(?:\s|>)/i.test(h), 'real disabled HTML property');
ok(!/<a[^>]+(?:affiliates\.inspire3|clickbank|affiliate_id=)/i.test(h), 'no earning hyperlinks');
ok(!/<script\b|<form\b|<iframe\b|\bonclick\s*=|<video\b/i.test(h), 'no scripts, forms, embeds or video');
ok(h.includes('If you buy through an approved link') && h.includes('No such link is active here'), 'conditional honest disclosure');
ok(h.includes('https://finalvestige.com/focus/'), 'existing free CTA');
ok(h.includes('aria-describedby="fvm152-hold"'), 'accessible hold description');
ok(h.includes(':focus-visible')&&h.includes('prefers-reduced-motion'), 'focus and reduced motion');
ok(h.includes('min-height:48px'), 'touch targets');
ok(h.includes('grid-template-columns:1fr')&&h.includes('min-width:780px'), 'mobile first grid');
ok(!/https?:\/\/(?:cdn\.|analytics\.|googletagmanager\.|www\.googletagmanager)/i.test(h), 'no external measurement dependency');
ok(m.merchant_authorization==='UNVERIFIED'&&m.affiliate_url===null,'authorization and URL null');
ok(m.merchant_paid_sales_verified===false&&m.net_revenue_per_1000_qualified_humans==='NOT_COMPUTABLE','financial reporting truthful');
ok(m.sources.length>=12&&m.claims.length>=20,'substantiation depth');
ok(Object.values(m.gates).every(x=>x==='CLOSED_NOT_VERIFIED'),'all release gates closed');
ok(m.claims.find(x=>x.id==='C15').verdict==='REJECT','no public portal to approval');
ok(m.claims.find(x=>x.id==='C24').verdict==='REJECT','FTC claim not salvaged by disclosure');
ok(m.claims.find(x=>x.id==='C19').verdict==='REJECT_EVENT_CONFLATION','clicks not sales');
ok(m.claims.find(x=>x.id==='C23').verdict==='HYPOTHESIS_NOT_RUN','A/B not executed');
return checks;
}
let checks=verify(get('false-memory-source-investigation.md'),get('commercial-decision.md'),get('buyer-decision-REVIEW-ONLY.html'),get('claim-source-release-matrix.json'));
let muts=0;function shouldFail(f){try{f();throw Error('unsafe mutation was not detected')}catch(e){if(/unsafe mutation was not detected/.test(e.message))throw e;muts++}}
const args=[get('false-memory-source-investigation.md'),get('commercial-decision.md'),get('buyer-decision-REVIEW-ONLY.html'),get('claim-source-release-matrix.json')];
shouldFail(()=>verify(args[0],args[1],args[2].replace(/ disabled aria-describedby/,' aria-describedby'),args[3]));
shouldFail(()=>verify(args[0],args[1],args[2].replace('data-affiliate-approval="UNVERIFIED"','data-affiliate-approval="APPROVED"'),args[3]));
shouldFail(()=>verify(args[0],args[1],args[2]+'<script src="https://tracker.test/t.js"></script>',args[3]));
shouldFail(()=>verify(args[0],args[1],args[2].replace('No such link is active here','A verified affiliate link is live'),args[3]));
shouldFail(()=>verify(args[0],args[1],args[2],args[3].replace('"affiliate_url": null','"affiliate_url": "https://example.test/affiliate"')));
shouldFail(()=>verify(args[0],args[1],args[2],args[3].replace('"CLOSED_NOT_VERIFIED"','"OPEN"')));
shouldFail(()=>verify(args[0],args[1],args[2],args[3].replace('"NOT_COMPUTABLE"','0')));
shouldFail(()=>verify(args[0],args[1].replace('HARD HOLD','ACTIVATED'),args[2],args[3]));
console.log('PASS: '+checks+' source/compliance assertions and '+muts+' deliberate-negative mutations. Use native Node when available; CJS-compatible V8 harness is supported. No network, CMS or merchant calls.');