import {readFileSync} from "node:fs";
import test from "node:test";
import assert from "node:assert/strict";
import {validateSynthetic, aggregateSynthetic, recordOutboundEvent, ACTIVATION_ENABLED} from "./attribution.mjs";

const get = name => readFileSync(new URL("./" + name, import.meta.url), "utf8");
const article = get("investigation.md");
const guide = get("total-focus-guide-core.html");
const a = get("total-focus-a-text.blocks.html");
const b = get("total-focus-b-film.blocks.html");
const hub = get("mind-hub-noncanonical.blocks.html");
const matrix = JSON.parse(get("claim-source-matrix.json"));
const vtt = get("film-captions.vtt");
const count = (s,re) => [...s.matchAll(re)].length;

test("article is substantial and explicitly sourced", () => {
  assert.ok(article.trim().split(/\s+/).length >= 1900);
  for (const term of ["1974","1978","2025","2026","Puységur","suggestion","Source trail"]) assert.ok(article.includes(term), term);
  assert.match(article,/10\.1016\/S0022-5371\(74\)80011-3/);
  assert.match(article,/10\.1037\/xlm0001529/);
});
test("investigation stays commercially separate", () => {
  assert.doesNotMatch(article,/https?:\/\/(?:inspire3|hypnosislive|zen12)\.com/i);
  assert.doesNotMatch(article,/affiliate (?:buy|checkout|purchase) link/i);
});
test("exact named product and bounded evidence", () => {
  for (const token of ["Total Focus", "33-minute","47 MB","J. A. Amos","not a hands-on review","not independently", "not a treatment"]) {
    assert.ok(guide.includes(token), token);
  }
  assert.ok(guide.split(/\s+/).length > 1400);
});
test("A and B contain byte-identical complete source guide", () => {
  assert.equal(a.split(guide).length,2);
  assert.equal(b.split(guide).length,2);
  assert.ok(b.length>a.length+1000);
});
test("native purchase controls are actually disabled in BOTH variants", () => {
  for (const page of [a,b]) {
    assert.equal(count(page,/<button\b[^>]*\bdisabled\b[^>]*>/gi),1);
    assert.match(page,/<button\b[^>]*type="button"[^>]*disabled[^>]*aria-disabled="true"/);
    assert.doesNotMatch(page,/<a\s+[^>]*href="(?:https?:\/\/)?(?:www\.)?(?:hypnosislive|inspire3|zen12)\.com\//i);
  }
});
test("commission disclosure appears next to merchant control", () => {
  for (const page of [a,b]) {
    const notice=page.indexOf("Final Vestige may earn a commission at no additional cost to you");
    const button=page.indexOf('<button type="button" disabled');
    assert.ok(notice>0 && button>notice && button-notice<430);
  }
});
test("no live signup, autoplay, scripts, iframe, merchant tracking or fake hosted video", () => {
  for (const page of [a,b,hub]) {
    assert.doesNotMatch(page,/<(?:form|script|iframe|video|audio)\b/i);
    assert.doesNotMatch(page,/\bautoplay\s*=/i);
    assert.doesNotMatch(page,/dataLayer|googletagmanager|fetch\s*\(|localStorage\s*\(/i);
  }
});
test("B alone contains original film storyboard and accessible transcript", () => {
  assert.doesNotMatch(a, /The Question After the Crash/);
  assert.match(b, /The Question After the Crash/);
  assert.match(b, /<details>\s*<summary>/);
  assert.equal(count(b, /<li><b>00:/g),6);
  assert.match(b,/no playable source/);
});
test("responsive accessible scoped templates", () => {
  for (const p of [a,b,hub]) {
    assert.match(p, /focus-visible/);
    assert.match(p, /prefers-reduced-motion/);
    assert.match(p, /max-width:480px|max-width:740px/);
    assert.match(p, /<h1\b/);
  }
});
test("hub links only to already published destinations", () => {
  for (const url of ["https://finalvestige.com/explore/","https://finalvestige.com/focus/","https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"]) assert.ok(hub.includes(url),url);
  assert.doesNotMatch(hub, /href="https:\/\/finalvestige\.com\/mind\//);
});
test("matrix source and decisions match declared counts", () => {
  assert.equal(matrix.sources.length,matrix.source_count);
  assert.equal(matrix.decisions.length,matrix.decision_count);
  assert.ok(matrix.sources.length>=18 && matrix.decisions.length>=35);
  assert.ok(matrix.sources.every(s=>/^https:\/\//.test(s.url)));
  assert.ok(matrix.decisions.every(c=>matrix.sources.some(s=>s.id===c.source_id)));
});
test("all publication and commercial gates explicitly false", () => {
  assert.ok(Object.keys(matrix.gates).length>=12);
  assert.ok(Object.values(matrix.gates).every(v=>v===false));
  assert.equal(matrix.commercial_activation,false);
  assert.equal(matrix.live_site_mutations,0);
});
test("seller conditions caveated, inconsistent prices absent", () => {
  assert.match(guide,/different amounts/);
  assert.match(guide,/must be rechecked/);
  assert.doesNotMatch(guide,/\$\d{2}(?:\.\d\d)?/);
});
test("VTT captions cover exactly 40 seconds and six contiguous cues", () => {
  assert.match(vtt,/^WEBVTT/);
  const ts=[...vtt.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d{3}) --> (\d\d):(\d\d):(\d\d)\.(\d{3})/g)];
  assert.equal(ts.length,6);
  const ms=v=>((+v[0])*3600+(+v[1])*60+(+v[2]))*1000+(+v[3]);
  let next=0;for(const m of ts){const t=ms(m.slice(1,5)),e=ms(m.slice(5,9));assert.equal(t,next);assert.ok(e>t);next=e}
  assert.equal(next,40000);
});
test("tracking remains disabled", () => {
  assert.equal(ACTIVATION_ENABLED,false);
  assert.equal(recordOutboundEvent({event:"offer_intent"}).accepted,false);
});
test("synthetic attribution rejects identifying data and hostile inputs", () => {
  const valid={synthetic:true,topic:"total_focus",variant:"a_text",placement:"guide_end",event:"offer_intent",count:1};
  for(const extra of [{email:"x@example.com"},{ip:"192.0.2.1"},{referrer:"https://x.test/id"},{userId:"x"},{url:"https://seller.test"}]){
    assert.throws(()=>validateSynthetic({...valid,...extra}));
  }
  for(const count of [NaN,Infinity,-1,1.5]) assert.throws(()=>validateSynthetic({...valid,count}));
  assert.throws(()=>validateSynthetic({...valid,synthetic:false}));
  assert.throws(()=>validateSynthetic(Object.assign(Object.create(null),valid)));
});
test("synthetic low-cell suppression makes no sales or user claims", () => {
  const mk=(count,variant="a_text")=>({synthetic:true,topic:"total_focus",variant,placement:"guide_end",event:"offer_intent",count});
  const r=aggregateSynthetic([mk(19),mk(20,"b_optional_film")]);
  assert.equal(r.cells.length,1);
  assert.equal(r.cells[0].count,20);
  assert.match(r.label,/NOT PURCHASES/);
  assert.equal(r.activation,false);
});
