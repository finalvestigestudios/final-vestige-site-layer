// Node v18+ zero-dependency, source-only QA. Run: node --test mind/r482/qa.test.cjs
const test=require('node:test'); const assert=require('node:assert/strict'); const fs=require('node:fs'); const path=require('node:path');
const read=n=>fs.readFileSync(path.join(__dirname,n),'utf8');
const A=read('ZEN12_GUIDE_A_TEXT_ONLY.html');
const B=read('ZEN12_GUIDE_B_OPTIONAL_42S_FILM.html');
const V=read('ZEN12_OPTIONAL_FILM_42S.vtt');
const S=read('RUBBER_HAND_ZEN12_POSTER.svg');
const H=read('MIND_ARCHIVE_HUB_SOURCE_ONLY.html');
const M=JSON.parse(read('PRODUCT_CLAIM_EVIDENCE_PERMISSION_MATRIX.json'));
const D=read('OFFER_FUNNEL_SALE_ACCEPTANCE.md');
const ARTICLE=read('THE_HAND_THAT_WASNT_YOURS.md');
const stripFilm=s=>s.replace(/<section class="rule" id="optional-film"[\s\S]*?<\/section>/,'').replace(/\s+/g,' ').trim();
function safety(s){
 assert.match(s,/type="button" disabled/,'native disabled merchant CTA');
 assert.match(s,/data-test="near-cta-disclosure"/);
 assert.match(s,/Affiliate disclosure:/);
 assert.ok(s.indexOf('data-test="near-cta-disclosure"') < s.indexOf('type="button" disabled'),'disclosure before CTA');
 assert.doesNotMatch(s,/<a\s+[^>]*href="https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|hypnosislive\.com)/i,'no active merchant outbound link');
 assert.doesNotMatch(s,/<script\b|<iframe\b|<form\b|autoplay\b|onload\s*=|onclick\s*=/i);
 assert.match(s,/not a product endorsement/i);
}
test('text guide and optional film have same substantive buyer HTML',()=>assert.equal(stripFilm(A),stripFilm(B)));
test('native commercial hold and near-link disclosure in both variants',()=>{safety(A);safety(B);});
test('only film variant supplies exact optional storyboard',()=>{assert.doesNotMatch(A,/data-test="film-only"/);assert.match(B,/data-test="film-only"/);assert.match(B,/transcript/i);});
test('HTML has basic semantic and responsive baseline',()=>{for(const s of [A,B,H]){assert.match(s,/<!doctype html>/i);assert.match(s,/<html lang="en">/);assert.match(s,/<meta name="viewport"/);assert.match(s,/<main>/);assert.match(s,/<h1>/);assert.match(s,/:focus-visible/);assert.match(s,/<meta name="robots" content="noindex,nofollow"/);assert.equal((s.match(/<h1\b/g)||[]).length,1);}});
test('zero new signup forms and no active seller links across hub and guides',()=>{for(const s of [A,B,H]){assert.doesNotMatch(s,/<form\b/i);assert.doesNotMatch(s,/<script\b/i);}});
test('poster is original accessible SVG and no external resources',()=>{assert.match(S,/<svg /);assert.match(S,/<title id=/);assert.match(S,/<desc id=/);assert.doesNotMatch(S,/<script\b|<image\b|https?:\/\//i);});
test('captions six cues, 42 seconds, monotonic boundaries',()=>{const cues=[...V.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d\d\d) --> (\d\d):(\d\d):(\d\d)\.(\d\d\d)/g)];assert.equal(cues.length,6);let prev=0;for(const c of cues){const start=+c[1]*3600000 + +c[2]*60000 + +c[3]*1000 + +c[4];const end=+c[5]*3600000 + +c[6]*60000 + +c[7]*1000 + +c[8];assert.equal(start,prev);assert.ok(end>start);prev=end;}assert.equal(prev,42000);});
test('claims source and permission gates explicit',()=>{assert.equal(M.must_not_activate,true);assert.equal(M.has_affiliate_url,false);assert.ok(M.decisions.length>=20);assert.ok(M.release_gates.length>=20);assert.ok(M.sources.length>=10);assert.equal(M.status,'DRAFT_ONLY_HARD_HOLD');});
test('article anchored to original, counterevidence, ethical limits and no sales',()=>{assert.match(ARTICLE,/10\.1038\/35784/);assert.match(ARTICLE,/10\.1525\/collabra\.325/);assert.match(ARTICLE,/10\.1525\/collabra\.116190/);assert.match(ARTICLE,/proprioceptive drift/i);assert.match(ARTICLE,/Puységur/);assert.match(ARTICLE,/NOT.*Zen12|does not test Zen12/i);});
test('revenue contract distinguishes click, sale and settlement',()=>{for(const s of ['affiliate_click','merchant_confirmed_purchase','confirmed_signup','qualified_human_sessions','refund','NOT COMPUTABLE','Grok'])assert.ok(D.includes(s),s);});
test('synthetic unsafe mutations rejected',()=>{const bad=[
 A.replace('type="button" disabled','type="button"'),
 A.replace('data-test="near-cta-disclosure"','data-test="omitted-disclosure"'),
 A.replace('Affiliate disclosure:','Other:'),
 A.replace('type="button" disabled','type="button" disabled onclick="buy()"'),
 A.replace('</main>','<form><input type="email"></form></main>'),
 A.replace('</main>','<a href="https://zen12.com/secret/">Buy</a></main>')
 ];for(let i=0;i<bad.length;i++){assert.throws(()=>safety(bad[i]),undefined,'mutation '+i+' escaped detection');}});
