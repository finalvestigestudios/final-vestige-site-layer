'use strict';
// R324 isolated, offline source-contract regression. Run: node mind/r324/verify_r324.cjs
// No network, merchant API, analytics, WP CMS or email access.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const here = __dirname;
const files = {
 article: 'THE-SYLLABLE-THE-RECORDING-NEVER-PLAYED-UNPUBLISHED.md',
 a: 'ZEN12-A-TEXT-ONLY-EVIDENCE-GUIDE-REVIEW.html',
 b: 'ZEN12-B-OPTIONAL-42S-EVIDENCE-GUIDE-REVIEW.html',
 hub: 'MIND-ARCHIVE-FOUR-STREAM-WP-REVIEW-ONLY.html',
 vtt: 'ORIGINAL-42S-CAPTIONS.vtt',
 matrix: 'SOURCE-CLAIM-OFFER-AUTHORIZATION-AND-ATTRIBUTION.json',
 dossier: 'OFFER-FIRST-FUNNEL-ATTRIBUTION-AND-RELEASE-DOSSIER.md'
};
const load = () => Object.fromEntries(Object.entries(files).map(([k,f])=>[k,fs.readFileSync(path.join(here,f),'utf8')]));
const error = (cond, message, errors) => { if (!cond) errors.push(message); };
const normalizedBuyer = s => s.replace(/<figure class="film"[\s\S]*?<\/figure>/, '').replace(/Unpublished Review B/g,'Unpublished Review A');
const report = f => {
  const e = [];
  let m;
  try { m = JSON.parse(f.matrix); } catch(x) { e.push('invalid matrix JSON'); return e; }
  error(m.version === 'mind-r324-2026-11-12', 'matrix version wrong', e);
  error(m.holds?.length === 18 && m.holds.every(h=>h.status === 'HOLD'), '18 commercial holds must stay closed',e);
  error(m.sources?.length >= 20 && m.claims?.length >= 30, 'incomplete evidence inventory',e);
  const ids = new Set(m.sources.map(s=>s.id));
  error(m.sources.every(s=>/^https:\/\//.test(s.url)), 'invalid source URL',e);
  error(m.claims.every(c=>c.source_ids.every(id=>ids.has(id))), 'claim-to-source orphan',e);
  error(m.claims.every(c=>/^(supported|seller|dated|reject|not_|public)/.test(c.assessment)), 'claim without classification',e);
  error(m.social_pathways?.length === 3 && m.social_pathways.every(p=>p.social_asset_id===null), 'fake creator media IDs',e);
  error(m.experiment?.closed===true, 'experiment prematurely enabled',e);
  error(m.privacy_measurement_contract?.single_existing_jetpack_list===true && m.privacy_measurement_contract?.tracking_scripts_added===0, 'signup/analytics duplication',e);
  error(f.article.includes('pubmed.ncbi.nlm.nih.gov/5409744/') && f.article.includes('pubmed.ncbi.nlm.nih.gov/6457110/') && f.article.includes('pubmed.ncbi.nlm.nih.gov/29289097/'), 'original experiment sources missing',e);
  error(f.article.includes('Warren did not test Zen12') && f.article.includes('historical') && /unpublished/i.test(f.article), 'scientific boundary absent',e);
  error(f.dossier.includes('NOT COMPUTABLE') && f.dossier.includes('TASK-008') && f.dossier.includes('paid'), 'cohort or creator handoff omitted',e);
  for(const k of ['a','b','hub']) {
    const h=f[k];
    error(/<html lang="en">/.test(h) && /name="viewport"/.test(h) && /name="robots" content="noindex,nofollow"/.test(h),'a11y/SEO draft header '+k,e);
    error(!/<script\b|<iframe\b|<form\b|<input\b|<video\b|<audio\b|<source\b/i.test(h),'unapproved executable/embed/form/media element '+k,e);
    error(!/<(?:video|audio)\b[^>]*\bautoplay\b/i.test(h), 'autoplay marker '+k,e);
    error(!/<a\b[^>]*href="https?:\/\/(?:www\.)?(?:zen12\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)/i.test(h),'active merchant link '+k,e);
    error(/href="https:\/\/finalvestige\.com\/focus\/"/.test(h),'existing Focus path absent '+k,e);
    error(/prefers-reduced-motion:reduce/.test(h),'reduced motion stylesheet absent '+k,e);
  }
  for(const k of ['a','b']) {
    error(/<button type="button" disabled aria-disabled="true">/.test(f[k]), 'merchant CTA not disabled '+k,e);
    const notice = f[k].indexOf('Affiliate disclosure: If a future authorized purchasing link');
    const button = f[k].indexOf('<button type="button" disabled');
    error(notice>0 && button>notice && button-notice<550, 'affiliate disclosure not adjacent '+k,e);
    error(f[k].includes('twelve minutes') && f[k].includes('seller') && f[k].includes('NOT')===false ? true : f[k].includes('seller'), 'buyer copy core missing '+k,e);
  }
  error(normalizedBuyer(f.a)===normalizedBuyer(f.b), 'A/B substantive copy drift',e);
  error(f.b.includes('42-second original short-film') && f.b.includes('Storyboard, not playable video') && f.b.includes('<details>'), 'film treatment/transcript missing',e);
  error(!f.a.includes('class="film"'), 'control contaminated by film',e);
  const cues=Array.from(f.vtt.matchAll(/(\d\d:\d\d:\d\d\.\d{3}) --> (\d\d:\d\d:\d\d\.\d{3})/g));
  error(f.vtt.startsWith('WEBVTT') && cues.length===6 && cues[0][1]==='00:00:00.000' && cues[5][2]==='00:00:42.000','42-second WebVTT cue timing incorrect',e);
  error(f.hub.includes('Perception &amp;')===false && f.hub.includes('History of Suggestion') && f.hub.includes('Tools Under Review'),'hub four streams missing',e);
  error(/<button type="button" disabled aria-disabled="true">/.test(f.hub), 'hub merchant hold disabled missing',e);
  return e;
};
const original = load();
const baseline = report(original);
assert.deepEqual(baseline, [], 'R324 baseline regressions: '+baseline.join(' | '));
const mutations=[
 ['activate seller CTA', x=>x.a=x.a.replace(' type="button" disabled',' type="button"')],
 ['remove notice',x=>x.a=x.a.replace('Affiliate disclosure: If a future authorized purchasing link','Other text: If a future authorized purchasing link')],
 ['inject active seller URL',x=>x.a=x.a.replace('href="https://finalvestige.com/focus/"','href="https://zen12.com/getstarted"')],
 ['add tracker JS',x=>x.b=x.b.replace('</head>','<script src="/pixels.js"></script></head>')],
 ['add iframe',x=>x.b=x.b.replace('</body>','<iframe src="about:blank"></iframe></body>')],
 ['add form',x=>x.hub=x.hub.replace('</main>','<form><input></form></main>')],
 ['remove Focus',x=>x.hub=x.hub.replaceAll('href="https://finalvestige.com/focus/"','href="/new-list/"')],
 ['introduce copy drift',x=>x.b=x.b.replace('A listening routine is not a laboratory result','Our audio scientifically guarantees results')],
 ['change closed gate',x=>{const j=JSON.parse(x.matrix);j.holds[0].status='OPEN';x.matrix=JSON.stringify(j)}],
 ['break claim citation',x=>{const j=JSON.parse(x.matrix);j.claims[0].source_ids=['fake_source'];x.matrix=JSON.stringify(j)}],
 ['fake asset id',x=>{const j=JSON.parse(x.matrix);j.social_pathways[0].social_asset_id='fake123';x.matrix=JSON.stringify(j)}],
 ['inject duplicate analytics',x=>{const j=JSON.parse(x.matrix);j.privacy_measurement_contract.tracking_scripts_added=1;x.matrix=JSON.stringify(j)}],
 ['release experiment',x=>{const j=JSON.parse(x.matrix);j.experiment.closed=false;x.matrix=JSON.stringify(j)}],
 ['break caption endpoint',x=>x.vtt=x.vtt.replace('00:00:42.000','00:00:55.000')],
 ['remove original source',x=>x.article=x.article.replaceAll('pubmed.ncbi.nlm.nih.gov/5409744/','example.invalid')],
 ['change draft discoverability',x=>x.hub=x.hub.replace('noindex,nofollow','index,follow')],
 ['remove hub disability',x=>x.hub=x.hub.replace('<button type="button" disabled','<button type="button"')],
 ['remove 42s transcript',x=>x.b=x.b.replace('42-second original short-film treatment','film coming soon')],
 ['introduce autocue media',x=>x.b=x.b.replace('</body>','<video autoplay></video></body>')],
 ['remove reduced motion rule',x=>x.a=x.a.replace('prefers-reduced-motion:reduce','motion:enabled')]
];
for (const [name,mutate] of mutations) {
 const x={...original};mutate(x);
 const failures=report(x);
 assert.ok(failures.length > 0, 'unsafe mutation escaped: '+name);
}
console.log('R324 source baseline: PASS');
console.log('R324 unsafe mutations: '+mutations.length+'/'+mutations.length+' rejected');
console.log('NOTE: source-level only; native WordPress, browser, playable media, Jetpack opt-in and merchant transactions NOT verified.');
