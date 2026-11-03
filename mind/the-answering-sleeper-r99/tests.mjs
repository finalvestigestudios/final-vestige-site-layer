// Node 20+ only. No network or affiliate credentials. Run: node --test mind/the-answering-sleeper-r99/tests.mjs
import test from "node:test"; import assert from "node:assert/strict"; import {readFileSync} from "node:fs";
import {safeRecord,syntheticAggregate} from "./measurement.mjs";
const here=new URL(".",import.meta.url);
const read=x=>readFileSync(new URL(x,here),"utf8");
const a=read("pilot-a.html"),b=read("pilot-b.html"),hub=read("mind-hub.html");
const m=JSON.parse(read("claims-and-sources.json"));
const guide=x=>x.split("<!-- GUIDE-START -->")[1]?.split("<!-- GUIDE-END -->")[0];
test("identical substantive guide across A/B",()=>assert.equal(guide(a),guide(b)));
for(const [label,html] of [["a",a],["b",b]]){
test(label+" merchant links withheld",()=>assert.doesNotMatch(html,/<a\b[^>]*href="https:\/\/(?:zen12|inspire3|hypnosislive|affiliates\.)/i));
test(label+" disabled control and near disclosure",()=>{assert.match(html,/<button type="button" disabled/);assert.ok(html.indexOf("Affiliate disclosure:")<html.indexOf("<button"));});
test(label+" no active tracker/embed/form/media",()=>assert.doesNotMatch(html,/<(?:script|iframe|form|video|audio)\b/i));
test(label+" no subscription duplicate",()=>assert.doesNotMatch(html,/mailchimp|beehiiv|substack\.com|newsletter-form/i));
test(label+" noindex",()=>assert.match(html,/name="robots" content="noindex,nofollow"/));
test(label+" keyboard skip",()=>assert.match(html,/class="skip" href="#main"/));
}
test("film only in B",()=>{assert.match(b,/class="film"/);assert.doesNotMatch(a,/class="film"/);assert.match(b,/Read the complete film transcript/);});
test("VTT timed six-cue coverage",()=>{let v=read("film-40s.vtt");assert.equal((v.match(/--> /g)||[]).length,6);assert.match(v,/00:00:00\.000/);assert.match(v,/00:00:40\.000/);});
test("source-controlled original SVG no external assets",()=>{let p=read("poster.svg");assert.match(p,/<svg/);assert.doesNotMatch(p,/<script|<image|xlink:href|href="https?:/i);});
test("four-stream accessible Mind hub",()=>{assert.match(hub,/01 \/ Perception/);assert.match(hub,/04 \/ Tools Under Review/);assert.match(hub,/id="main"/);});
test("claim matrix never approves unsupported efficacy",()=>{assert.ok(m.claims.length>=20);for(const c of m.claims){if(/seller_efficacy|seller_health_claim|seller_mental_financial/.test(c.classification))assert.equal(c.disposition,"REJECT_UNSUPPORTED");}});
test("release gates all fail closed",()=>{assert.ok(m.release_gates.length>20);assert.ok(m.release_gates.every(g=>g.pass===false));assert.equal(m.tracking_policy.live_enabled,false);});
test("legal and commerce sources registered",()=>{for(const id of ["S5","S6","S7","S8","S13","S14"])assert.ok(m.sources.some(x=>x.id===id));});
test("synthetic rows only",()=>{const r={topic:"zen12",variant:"text",event:"guide_view"};assert.equal(safeRecord(r),"zen12|text|guide_view");assert.deepEqual(syntheticAggregate(Array(19).fill(r)),[]);assert.equal(syntheticAggregate(Array(20).fill(r))[0].count,20);});
test("privacy adversarial cases rejected",()=>{const valid={topic:"zen12",variant:"text",event:"guide_view"};for(const k of ["email","ip","referrer_url","user_id","buyer_name","order_id","timestamp","click_id"]){assert.throws(()=>safeRecord({...valid,[k]:"x"}));}for(const x of ["https://x","zen12?email=x",null,1]){assert.throws(()=>safeRecord({...valid,event:x}));}});
