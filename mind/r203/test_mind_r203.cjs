'use strict';
// Mind R203 reproducible source-level smoke/regression suite. Run: node mind/r203/test_mind_r203.cjs
// No dependencies or network. Tests source files in a full repository checkout.
// Does NOT replace real browser/keyboard/contrast/Lighthouse/checkout/CI tests.
const fs=require('node:fs');const path=require('node:path');const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..');
const get=p=>fs.readFileSync(path.join(root,p),'utf8');
const dir='mind/r203/';
const paths={article:dir+'the-decision-they-switched-choice-blindness-UNPUBLISHED.md',hub:dir+'mind-archive-four-stream-WP-PREVIEW-UNPUBLISHED.html',a:dir+'zen12-decision-record-A-TEXT-UNPUBLISHED.html',b:dir+'zen12-decision-record-B-OPTIONAL-42S-UNPUBLISHED.html',matrix:dir+'CHOICE-BLINDNESS-ZEN12-SOURCE-CLAIM-AUTHORIZATION-MATRIX.json',plan:dir+'ONE-OFFER-CHOICE-TO-REVENUE-AB-ACCEPTANCE.md',captions:dir+'zen12-optional-choice-film-42s-UNRENDERED.vtt',r201:'mind/r201/self-hypnosis-the-skill-versus-the-recording-UNPUBLISHED.md',r202:'mind/r202/the-claim-you-heard-twice-ILLUSORY-TRUTH-UNPUBLISHED.md'};
const files=Object.fromEntries(Object.entries(paths).map(([key,p])=>[key,get(p)]));
const checks=[];function ok(label,condition){assert.ok(condition,label);checks.push(label)}
const matrix=JSON.parse(files.matrix);
ok('19 actual source records',matrix.sources.length===19);
ok('31 evaluated claims',matrix.claims.length===31);
ok('30 unresolved commercial/release gates',matrix.commerce_gates.length===30);
ok('all gates OPEN',matrix.commerce_gates.every(g=>g.status==='OPEN'));
ok('all source IDs distinct',new Set(matrix.sources.map(s=>s.id)).size===matrix.sources.length);
ok('all source urls https',matrix.sources.every(s=>s.url.startsWith('https://')));
ok('all claim source references exist',matrix.claims.every(c=>c.source_ids.every(id=>matrix.sources.some(s=>s.id===id))));
ok('claims have dispositions',matrix.claims.every(c=>c.decision&&c.limit));
ok('no fake revenue values',matrix.revenue.net_revenue_per_1000_qualified_sessions===null&&matrix.revenue.status.startsWith('NOT_COMPUTABLE'));
ok('approval unverified',matrix.inspire3_publisher.state==='UNVERIFIED');
ok('owned Payhip fallback unverified',matrix.owned_payhip_mind_fallback.state==='UNVERIFIED');
ok('original investigation substantive',files.article.split(/\s+/).length>=2200);
ok('original primary source',files.article.includes('10.1126/science.1111709'));
ok('supermarket source',files.article.includes('20637455'));
ok('moral attitude limitation',files.article.includes('69%'));
ok('hypothetical pension caveat',files.article.includes('hypothetical'));
ok('paper exercise explicitly not validated',/not (an experiment|a scientifically validated|a clinical)/i.test(files.article));
ok('Puységur route',files.article.includes('puysegurs-animal-magnetism-files'));
ok('source list includes FTC',files.article.includes('health-products-compliance-guidance'));
ok('no merchant endorsement in investigation',!files.article.includes('href="https://zen12.com/hnp'));
ok('A/B research text invariant',files.a.slice(files.a.indexOf('<section><h2>The decision')).split('</main>')[0]===files.b.slice(files.b.indexOf('<section><h2>The decision')).split('</main>')[0]);
ok('original WebVTT draft present',files.captions.startsWith('WEBVTT'));ok('42-second caption end',files.captions.includes('00:00:42.000'));ok('captions marked unrendered',files.captions.includes('NOT RENDERED'));ok('film concept only in B',!files.a.includes('id="optional-film"')&&files.b.includes('id="optional-film"'));
ok('film nonplaying disclaimer',files.b.includes('not playable'));
ok('film has textual transcript',files.b.includes('<details><summary>Full 42-second storyboard'));
ok('static poster described',files.b.includes('role="img"')&&files.b.includes('aria-label='));
for(const name of ['a','b','hub']){
 const h=files[name];
 ok(name+' declares language',h.includes('<html lang="en">'));
 ok(name+' viewport set',h.includes('name="viewport"'));
 ok(name+' native disabled button',/<button[^>]+disabled/.test(h));
 ok(name+' no user capture form',!/<form\b/i.test(h));
 ok(name+' no javascript loader',!/<script\b/i.test(h));
 ok(name+' no autoplay',!/<video[^>]*autoplay|<audio[^>]*autoplay/i.test(h));
 ok(name+' near-CTA disclosure',(h.lastIndexOf('Affiliate disclosure:')>=0)&&(h.indexOf('<button type="button" disabled')-h.lastIndexOf('Affiliate disclosure:')<700));
 ok(name+' commission language',h.includes('may earn a commission at no additional cost to you'));
 ok(name+' no active affiliate earning query',!/(href|src)="[^"]+(aff_id|clickid|ref_id|hop=|affiliate_id)/i.test(h));
 ok(name+' free Focus route',h.includes('https://finalvestige.com/focus/'));
 ok(name+' no external fonts',!/@import|fonts\.googleapis\.com|<link[^>]+stylesheet/i.test(h));
 ok(name+' reduced-motion policy',h.includes('prefers-reduced-motion'));
 ok(name+' unpublished',/UNPUBLISHED|Unpublished|unpublished/.test(h));
 const ids=[...h.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);ok(name+' unique ids',new Set(ids).size===ids.length);
 const desc=[...h.matchAll(/aria-describedby="([^"]+)"/g)].map(m=>m[1]);ok(name+' describedby points to id',desc.every(id=>ids.includes(id)));
}
ok('marketing site matches exact Zen12 seller url',files.a.includes('https://zen12.com/hnp'));
ok('seller price is explicitly dated',files.a.includes('November 7, 2026'));
ok('no claimed merchant checkout',files.a.includes('does not establish the current checkout total'));
ok('claim limit stated',files.a.includes('seller efficacy representations'));
ok('original R201 bias correction included',files.r201.includes('low certainty with high risk of bias'));
ok('original R201 unpoolable attention included',files.r201.includes('attention outcomes could not be pooled'));
ok('R202 methodological limitation',files.r202.includes('not** a trial of web searches'));
ok('R202 fake news measure limited',files.r202.includes('had appeared as fake news on social media'));
ok('R202 2022 corrigendum citation',files.r202.includes('10.1016/j.cognition.2021.104996'));
ok('plan has approved ownership boundaries',files.plan.includes('Grok remains sole creator/publisher'));
ok('plan has real paid outcome specification',files.plan.includes('net revenue per 1,000 qualified-human landing sessions'));
ok('plan avoids duplication',files.plan.includes('no duplicate tags')||files.plan.includes('no duplicate'));
ok('plan explicitly keeps hold',files.plan.includes('HARD HOLD'));
ok('no forced external resources',!/<iframe|<object|<embed/i.test(files.a+files.b+files.hub));
// Deliberately unsafe mutations: ensure the contract checks that matter would catch these.
let mutations=0;function rejected(label,mutant,validator){assert.ok(!validator(mutant),label+' should be rejected');mutations++}
rejected('activated link',files.a.replace('disabled aria-describedby','aria-describedby'),s=>/<button[^>]+disabled/.test(s));
rejected('suppress disclosure',files.a.replace('Affiliate disclosure:','Affiliate notice:'),s=>s.includes('Affiliate disclosure:'));
rejected('removed free option',files.a.replaceAll('https://finalvestige.com/focus/','/nothing'),s=>s.includes('https://finalvestige.com/focus/'));
rejected('new newsletter form',files.a+'<form></form>',s=>!/<form\b/i.test(s));
rejected('injected tracker',files.a+'<script src="/collect.js"></script>',s=>!/<script\b/i.test(s));
rejected('fake live video',files.b.replace('not playable','now playable'),s=>s.includes('not playable'));
rejected('lost caption transcript',files.b.replace('Full 42-second storyboard','Missing storyboard'),s=>s.includes('Full 42-second storyboard'));
rejected('faked approval',files.matrix.replace('"state": "UNVERIFIED"','"state": "APPROVED"'),s=>JSON.parse(s).owned_payhip_mind_fallback.state==='UNVERIFIED');
rejected('moved revenue from missing to zero',files.matrix.replace('"net_revenue_per_1000_qualified_sessions": null','"net_revenue_per_1000_qualified_sessions": 0'),s=>JSON.parse(s).revenue.net_revenue_per_1000_qualified_sessions===null);
rejected('misread choice finding',files.article.replace('does not say everybody misses substitutions','PROVES everybody misses substitutions'),s=>/does not say everybody misses substitutions/i.test(s));
console.log('Mind R203 PASS '+checks.length+'/'+checks.length+' source assertions; '+mutations+'/'+mutations+' unsafe mutations detected. Source-level only; no browser, hosted CI, affiliate authorization or purchase verified.');
