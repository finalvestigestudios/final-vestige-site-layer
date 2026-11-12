#!/usr/bin/env node
/**
 * R311 source-only QA; no network, merchant calls, WordPress, tracking or writes.
 * Run: node mind/r311/verify_r311.cjs
 * Tests a source snapshot, not browser/WCAG/merchant checkout/affiliate approval.
 */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const dir = __dirname;
const filenames = {
  article: 'THE-CHOICE-THAT-CAME-BACK-WEARING-ANOTHER-FACE-UNPUBLISHED.md',
  a: 'ZEN12-A-TEXT-ONLY-BUYER-GUIDE-REVIEW.html',
  b: 'ZEN12-B-OPTIONAL-FILM-BUYER-GUIDE-REVIEW.html',
  hub: 'MIND-UNRELIABLE-WITNESS-ARCHIVE-WP-REVIEW.html',
  matrix: 'CHOICE-BLINDNESS-ZEN12-SOURCES-CLAIMS-AND-GATES.json',
  plan: 'ONE-OFFER-CREATOR-FIT-MEASUREMENT-AND-RELEASE-ACCEPTANCE.md',
  vtt: 'ORIGINAL-42S-FILM-CAPTION-CONCEPT.vtt'
};
const read = name => fs.readFileSync(path.join(dir, filenames[name]), 'utf8');
const base = Object.fromEntries(Object.keys(filenames).map(k => [k, read(k)]));
function assert(c,m){if(!c)throw Error(m)}
function count(s,re){return [...s.matchAll(re)].length}
function check(src){
  const {article,a,b,hub,matrix,plan,vtt}=src;
  let m;try{m=JSON.parse(matrix)}catch(e){throw Error('unparseable matrix')}
  assert(m.schema_version==='mind.r311.1','matrix version');
  assert(m.sources.length===18,'18 source rows');
  assert(m.claims.length===30,'30 classified claims');
  assert(m.authorization_gates.length===18,'18 auth gates');
  assert(m.authorization_gates.every(x=>x.status==='HARD_HOLD'),'unapproved auth gate');
  assert(m.claims.every(x=>x.source_ids.length && x.source_ids.every(id=>m.sources.some(s=>s.id===id))),'orphan claim source');
  assert(m.sources.every(s=>/^https:\/\//.test(s.url)),'malformed source url');
  assert(m.creator_paths.length===3 && m.creator_paths.every(x=>x.grok_asset_id===null),'invented creator asset id');
  assert(m.measurement.metric_status==='NOT_COMPUTABLE' && m.measurement.net_revenue_status==='NOT_VERIFIED','fabricated revenue metric');
  assert(m.seller_products.every(x=>x.affiliate_approval==='NOT_VERIFIED'&&x.price==='WITHHELD_VOLATILE'),'unverified offers or fabricated price');
  assert(article.includes('The Choice That Came Back Wearing Another Face'),'article missing');
  assert(article.includes('Johansson')&&article.includes('Puységur')&&article.includes('Choice Blindness Lab'),'article research/provenance');
  assert(article.includes('This is not')&&article.includes('does not'),'misleading limitation removal');
  assert(article.includes('https://finalvestige.com/2026/11/02/change-blindness/'),'wrong live editorial route');
  assert(article.includes('no new translation') || article.includes('not conducting a modern'),'historical scope');
  assert(article.includes('does not certify')&&article.includes('did not test Zen12'),'claim separation');
  const removeFilm = s => s.replace(/<section id="original-optional-film"[\s\S]*?<\/section>/,'');
  assert(removeFilm(b)===a,'A/B buyer text differs outside optional film');
  assert(a.includes('The free')||a.includes('free Focus Fieldbook'),'free alternative missing');
  assert(b.includes('id="original-optional-film"') && b.includes('42-second narration'),'missing optional storyboard');
  assert(b.includes('aria-labelledby="posterTitle posterDesc"') && b.includes('id="posterDesc"') && b.includes('Read the complete 42-second narration'),'film poster alt or transcript absent');
  for(const [label,html] of [['A',a],['B',b],['hub',hub]]){
    assert(html.startsWith('<!doctype html>')&&html.includes('<html lang="en">'),'HTML/lang '+label);
    assert(html.includes('name="viewport"')&&html.includes('noindex,nofollow'),'mobile/noindex '+label);
    assert(html.includes('prefers-reduced-motion'),'motion safeguard '+label);
    assert(html.includes(':focus-visible')&&html.includes('Skip to content'),'focus and skip link '+label);
    assert(/<button[^>]*disabled[^>]*>/.test(html),'actual disabled control '+label);
    assert(html.includes('commission at no additional cost'),'disclosure near withheld CTA '+label);
    assert(/<button[^>]*disabled[^>]*>[\s\S]*?<\/button>/.test(html),'purchase disabled '+label);
    assert(!/<script\b|<iframe\b|<form\b|<video\b|<audio\b|on(?:click|load|focus|error)\s*=/i.test(html),'unapproved active executable/form/media '+label);
    assert(!/\bautoplay\b\s*=|\bautoplay\s*>/i.test(html),'autoplay '+label);
    assert(!/<a\s[^>]*href=["']https:\/\/(zen12|hypnosislive|brainwaveshots|inspire3|affiliates\.inspire3)\.com/i.test(html),'merchant outbound before permission '+label);
    assert(!/https:\/\/[^"']*(?:ref=|aff_id=|affiliate_id=|hop=)/i.test(html),'unauthorized affiliate query '+label);
    assert(!/\bdataLayer\b|googletagmanager|fbq\(|gtag\(/i.test(html),'third-party analytics '+label);
    assert(!/name=["'](?:email|subscriber)["']/i.test(html),'duplicate signup '+label);
    assert(!/we (?:tried|used|tested) Zen12|my own Zen12 results/i.test(html),'fabricated firsthand endorsement '+label);
    assert(!/\$\d+\.\d{2}/.test(html),'fixed volatile prices '+label);
  }
  assert(hub.includes('Perception &amp; Attention')&&hub.includes('The History of Suggestion')&&hub.includes('Practice &amp; Reflection')&&hub.includes('Tools Under Review'),'hub four-stream taxonomy');
  assert(hub.includes('https://finalvestige.com/focus/')&&hub.includes('https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'),'hub source/free route');
  assert(hub.includes('WordPress review specimen only'),'no false CMS status');
  assert(vtt.startsWith('WEBVTT')&&vtt.includes('00:00:42.000')&&count(vtt,/-->/g)===6,'caption concept duration');
  assert(plan.includes('NOT COMPUTABLE')&&plan.includes('HARD HOLD')&&plan.includes('P0'),'measurement/release plan');
  return true;
}
function clone(overrides){return {...base,...overrides}}
const mutants=[
  ['unapproved gate',x=>({matrix:x.matrix.replace('"HARD_HOLD"','"APPROVED"')})],
  ['source removed',x=>({matrix:x.matrix.replace('"sources": [','"sources": [\n    ') .replace('"S18"','"REMOVED_SOURCE_ID"')})],
  ['orphan claim',x=>({matrix:x.matrix.replace('"S01",\n      "S02"','"MISSING_SOURCE_ID",\n      "S02"')})],
  ['invented asset id',x=>({matrix:x.matrix.replace('"grok_asset_id": null','"grok_asset_id": "invented"')})],
  ['fabricated revenue',x=>({matrix:x.matrix.replace('"metric_status": "NOT_COMPUTABLE"','"metric_status": "$1000"')})],
  ['fictitious affiliate approval',x=>({matrix:x.matrix.replace('"affiliate_approval": "NOT_VERIFIED"','"affiliate_approval": "APPROVED"')})],
  ['A active product link',x=>({a:x.a.replace('Zen12 overview','<a href="https://zen12.com/about">Zen12 overview</a>')})],
  ['B active product link',x=>({b:x.b.replace('Zen12 overview','<a href="https://zen12.com/about">Zen12 overview</a>')})],
  ['hub active product link',x=>({hub:x.hub.replace('12-level, 48-MP3','<a href="https://zen12.com/getstarted">12-level, 48-MP3</a>')})],
  ['A active button',x=>({a:x.a.replace('type="button" disabled','type="button"')})],
  ['B active button',x=>({b:x.b.replace('type="button" disabled','type="button"')})],
  ['hub active button',x=>({hub:x.hub.replace('<button disabled','<button')})],
  ['A removed disclosure',x=>({a:x.a.replace('may earn a commission at no additional cost','may be compensated')})],
  ['B removed disclosure',x=>({b:x.b.replace('may earn a commission at no additional cost','may be compensated')})],
  ['hub removed disclosure',x=>({hub:x.hub.replace('may earn a commission at no additional cost','may be compensated')})],
  ['A hidden script',x=>({a:x.a.replace('</body>','<script>alert(1)</script></body>')})],
  ['B tracker pixel',x=>({b:x.b.replace('</body>','<script>gtag("config","x")</script></body>')})],
  ['hub new signup',x=>({hub:x.hub.replace('</body>','<form><input name="email"></form></body>')})],
  ['hub autoplay',x=>({hub:x.hub.replace('</body>','<video autoplay></video></body>')})],
  ['B iframe',x=>({b:x.b.replace('</body>','<iframe src="https://example.org"></iframe></body>')})],
  ['A fabricated quote',x=>({a:x.a.replace('Final Vestige has not purchased','We tried Zen12. Final Vestige has not purchased')})],
  ['B price',x=>({b:x.b.replace('current checkout terms','$29.95 current checkout terms')})],
  ['no A/B parity',x=>({b:x.b.replace('A Source-Led Buyer','A Source-Led Special Buyer')})],
  ['remove film',x=>({b:x.b.replace('id="original-optional-film"','id="lost-film"')})],
  ['remove poster alt',x=>({b:x.b.replace('aria-labelledby="posterTitle posterDesc"','aria-labelledby="posterTitle"')})],
  ['remove researcher',x=>({article:x.article.replaceAll('Johansson','Researcher')})],
  ['fake scientific efficacy',x=>({article:x.article.replace('did not test Zen12','certified Zen12')})],
  ['broken live article URL',x=>({article:x.article.replace('https://finalvestige.com/2026/11/02/change-blindness/','https://finalvestige.com/old-change-blindness/')})],
  ['break captions',x=>({vtt:x.vtt.replace('00:00:42.000','00:00:40.000')})],
  ['false KPI',x=>({plan:x.plan.replaceAll('NOT COMPUTABLE','PAID AND PROVEN')})],
  ['delete hub fourth stream',x=>({hub:x.hub.replace('Tools Under Review','Tools Under Approval')})],
  ['missing publication status',x=>({hub:x.hub.replace('WordPress review specimen only','Published on WordPress')})]
];
function run(){
 check(base);
 let pass=0;
 for(const [name,f] of mutants){
  const update=f(base); const victim=clone(update);
  if(Object.keys(update).every(k=>update[k]===base[k]))throw Error('fixture did not change: '+name);
  let rejected=false;try{check(victim)}catch(e){rejected=true}
  if(!rejected)throw Error('UNDETECTED NEGATIVE FIXTURE: '+name);
  pass++;
 }
 console.log('R311 baseline PASS; deliberately unsafe mutations REJECTED '+pass+'/'+mutants.length);
}
if(require.main===module)run();
module.exports={check,run};
