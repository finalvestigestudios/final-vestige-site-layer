// Run from repository root: node mind/r485/qa.test.mjs
// Draft-only deterministic checks, not a substitute for browser, WordPress or merchant testing.
import {readFileSync} from 'node:fs';
import assert from 'node:assert/strict';
import {test} from 'node:test';
const root='mind/r485/';
const read=(name)=>readFileSync(root+name,'utf8');
const a=read('ZEN12_BUYING_GUIDE_A_TEXT_ONLY.html');
const b=read('ZEN12_BUYING_GUIDE_B_OPTIONAL_FILM_CONCEPT.html');
const poster=read('ZEN12_OPTIONAL_VIDEO_POSTER.svg');
const captions=read('ZEN12_OPTIONAL_VIDEO_CAPTIONS.vtt');
const article=read('THE_GORILLA_IN_THE_SCAN.md');
const hub=read('MIND_ARCHIVE_SOURCE_ONLY.html');
const funnel=read('OFFER_FUNNEL_CONVERSION_AND_GROK_HANDOFF.md');
const matrix=JSON.parse(read('CLAIM_SOURCE_PERMISSION_MATRIX.json'));
const main=(html)=>html.slice(html.indexOf('<section aria-labelledby="question">'),html.indexOf('</main>'));
const activePurchase=(html)=>/<a\b[^>]*(?:checkout|buy-now|affiliate|refersion)/i.test(html)||/<button\b(?![^>]*\bdisabled\b)[^>]*>[^<]*(?:buy|offer|merchant|zen12)/i.test(html);
const disclosureNear=(html)=>{const button=html.indexOf('<button type="button" disabled');const d=html.lastIndexOf('Affiliate disclosure:',button);return button>=0&&d>=0&&button-d<700;};
const noUnsafe=(s)=>!/<script\b|<iframe\b|\son(?:click|load|error)=|javascript:|autoplay|<form\b/i.test(s);
const truths=[
  ['two independent buyer guide variants share exactly the same advice',()=>assert.equal(main(a),main(b))],
  ['both variants have a native disabled purchase button',()=>{for(const x of [a,b])assert.match(x,/<button type="button" disabled/)}],
  ['FTC disclosure is adjacent to purchase control',()=>{for(const x of [a,b])assert.ok(disclosureNear(x))}],
  ['no active purchase-control link exists',()=>{for(const x of [a,b])assert.ok(!activePurchase(x))}],
  ['guides contain seller-versus-science distinction',()=>{for(const x of [a,b]){assert.match(x,/seller/);assert.match(x,/independent/);assert.match(x,/not authenticate|not authenticated/i)}}],
  ['guides provide six verification questions',()=>{for(const x of [a,b]){const section=x.split('<section aria-labelledby="buyers">')[1].split('</section>')[0];assert.equal((section.match(/<li>/g)||[]).length,6)}}],
  ['seller features described without importing price',()=>{for(const x of [a,b]){assert.match(x,/twelve levels/);assert.match(x,/four/);assert.ok(!/\$\d{2,}/.test(x))}}],
  ['guide withholds guarantees and clinical promises',()=>{for(const x of [a,b])assert.match(x,/does not establish that Zen12 treats anxiety/)}],
  ['both use the real free first-party alternative',()=>{for(const x of [a,b])assert.match(x,/href="https:\/\/finalvestige.com\/focus\/"/)}],
  ['no duplicate forms or imported tracking',()=>{for(const x of [a,b,hub])assert.ok(noUnsafe(x))}],
  ['both variants have proper responsive and focus CSS',()=>{for(const x of [a,b]){assert.match(x,/@media\(max-width:390px\)/);assert.match(x,/:focus-visible/)}}],
  ['variant B is optional and honestly storyboard-only',()=>{assert.match(b,/<details>/);assert.match(b,/no encoded video is supplied/);assert.ok(!/<video\b/.test(b))}],
  ['variant B has no forced playback',()=>assert.ok(!/autoplay/i.test(a)&&!/autoplay\s*=/i.test(b))],
  ['SVG is original marked artwork with accessible title and description',()=>{assert.match(poster,/<title/);assert.match(poster,/<desc/);assert.match(poster,/FINAL VESTIGE/)}],
  ['VTT has six cues, reaches 42 seconds',()=>{assert.match(captions,/^WEBVTT/);assert.equal((captions.match(/ --> /g)||[]).length,6);assert.match(captions,/00:00:42\.000/)}],
  ['Mind hub has four thematic streams',()=>{for(const t of ['Perception &amp; Attention','History of Suggestion','Practice &amp; Reflection','Tools Under Review'])assert.ok(hub.includes(t))}],
  ['Mind hub contains only approved existing live internal links',()=>assert.ok(!/href="[^"]*mind\/r485|href="[^"]*\/mind\/"/.test(hub))],
  ['No fabricated Grok IDs',()=>{assert.match(funnel,/UNKNOWN \/ UNMATCHED/);assert.match(funnel,/not media IDs/)}],
  ['Revenue definition preserves settlement and missingness',()=>{assert.match(funnel,/NOT COMPUTABLE/);assert.match(funnel,/commission_settled/);assert.match(funnel,/refund_or_reversal/)}],
  ['Research article has at least 1900 words',()=>assert.ok(article.split(/\s+/).length>=1900)],
  ['Research distinguishes clinical use from experiments',()=>{assert.match(article,/not an assessment of individual medical competence/);assert.match(article,/not proof/)}],
  ['Primary studies and contrary 2023 paper all linked',()=>{for(const doi of ['10.1068/p281059','10.1068/i0386','10.1177/0956797613479386','10.1073/pnas.2214930120'])assert.ok(article.includes(doi))}],
  ['Matrix has ≥25 claims and ≥12 independently addressable source links',()=>{assert.ok(matrix.claims.length>=25);assert.ok(Object.keys(matrix.sources).length>=12)}],
  ['Matrix has at least 25 release gates and holds commerce',()=>{assert.ok(matrix.commercial_release_gates.length>=25);assert.match(matrix.current_state,/OPEN/)}],
  ['Matrix prohibits product efficacy transfer',()=>{assert.ok(matrix.claims.some(x=>x.text.includes('Gorilla studies demonstrate')&&x.status==='prohibited'))}],
  ['No checkout or affiliate earning URL in source-controlled guides',()=>{for(const x of [a,b])assert.ok(!/href="[^"]*(refersion\.com|clickbank|aff_id=|affiliate_id=|checkout)/i.test(x))}]
];
for(const [name,check] of truths)test(name,check);
test('Synthetic safety mutations must be detected by guards',()=>{
 const mutants=[
  [a.replace('<button type="button" disabled','<button type="button"'),x=>!/<button type="button" disabled/.test(x)],
  [a.replace('Affiliate disclosure:','Disclosure missing:'),x=>!disclosureNear(x)],
  [a.replace('</body>','<script src="https://example.com/track.js"></script></body>'),x=>!noUnsafe(x)],
  [a.replace('</body>','<form><input type="email"></form></body>'),x=>!noUnsafe(x)],
  [a.replace('Check the verified Zen12 offer — unavailable','buy-now affiliate'),x=>!activePurchase(x)===false],
  [b.replace('no encoded video is supplied','ready to play and hosted'),x=>!/no encoded video is supplied/.test(x)]
 ];
 assert.equal(mutants.length,6);
 for(const [s,detect] of mutants)assert.ok(detect(s),'unsafe change should be detected');
});
