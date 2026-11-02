import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {dirname,join} from "node:path";
import {ACTIVE,MIN_GROUP_SIZE,validateSyntheticInput,collectOutboundEvent,summarizeSynthetic} from "./privacy-attribution.mjs";

const dir=dirname(fileURLToPath(import.meta.url));
const read=n=>readFileSync(join(dir,n),"utf8");
const a=read("offer-a-text.blocks.html"), b=read("offer-b-film.blocks.html"), core=read("guide-core.html");
const claim=JSON.parse(read("claims-and-release.json")), inv=read("investigation.md"), cap=read("captions.vtt"), red=read("README.md");

test("A/B pages each contain byte-identical complete guide core",()=>{
  assert.ok(a.includes(core));assert.ok(b.includes(core));
  assert.equal(a.split(core).length,2);assert.equal(b.split(core).length,2);
});
test("A/B no merchant buy hyperlinks, javascript redirects or external checkout",()=>{
  for(const s of [a,b]){
    assert.doesNotMatch(s,/<a[^>]+href=["']https?:\/\/(?:www\.)?(?:zen12|inspire3|affiliates\.inspire3)/i);
    assert.doesNotMatch(s,/<script\b|window\.location|location\.href|http-equiv=["']refresh/i);
  }
});
test("CTA remains genuinely natively disabled and disclosed adjacently",()=>{
  for(const s of [a,b]){
    assert.match(s,/<button\s+type="button"\s+disabled\s+aria-disabled="true">/);
    const i=s.indexOf("Affiliate disclosure:");
    const j=s.indexOf("<button",i);
    assert.ok(i>0&&j>i&&j-i<850,"disclosure must be before adjacent CTA");
    assert.match(s,/may earn a commission at no additional cost/);
  }
});
test("No email forms, pixels, third-party videos, auto-play, tracking or dangerous embeds",()=>{
  for(const s of [a,b]){
    assert.doesNotMatch(s,/<form\b|<iframe\b|<img\b|<script\b|<(?:audio|video)[^>]*\sautoplay\b|<object\b|<embed\b|navigator\.sendBeacon|gtag\(|fbq\(/i);
  }
});
test("Poster variant includes accessible readable full transcript and actual media hold",()=>{
  assert.ok(!a.includes('fv-r66-film-heading'));
  assert.match(b,/<section class="fv-r66-film" aria-labelledby="fv-r66-film-heading">/);
  assert.match(b,/<svg[^>]+role="img"[^>]+aria-label=/);
  assert.match(b,/<details><summary>Read full timed transcript/);
  assert.match(b,/00:34–00:40/);
  assert.match(b,/not enabled on this unpublished site candidate/);
});
test("Mobile and reduced motion styles plus keyboard focus are implemented",()=>{
  for(const s of [a,b]){
    assert.match(s,/@media\(max-width:700px\)/);
    assert.match(s,/@media\(prefers-reduced-motion:reduce\)/);
    assert.match(s,/:focus-visible\{outline:/);
    assert.match(s,/grid-template-columns:1fr/);
  }
});
test("Separate source conclusions from product-effectiveness promises",()=>{
  assert.match(inv,/affiliate_links: none/);
  assert.doesNotMatch(inv,/https:\/\/zen12\.com|https:\/\/inspire3\.com/);
  assert.match(core,/not.*tests of Zen12|not.*test.*Zen12/i);
  assert.match(core,/not.*product-specific substantiation|no such product-specific substantiation/i);
  assert.match(core,/not.*clinically tested|not.*independently verified|has not.*purchased/i);
});
test("Seller claim matrix remains approval-gated and specific",()=>{
  assert.equal(claim.affiliate_link,null);
  assert.equal(claim.commercial_status,"HARD_HOLD");
  assert.equal(claim.claims.length,31);
  assert.ok(claim.claims.filter(x=>x.status.includes("UNVERIFIED")).length>=4);
  assert.ok(claim.claims.filter(x=>x.classification==="seller_feature").length>=6);
  assert.ok(claim.claims.some(x=>x.statement.includes("12 minutes of Zen12")&&x.status.includes("NOT_INDEPENDENTLY_SUBSTANTIATED")));
});
test("Separate partner program recruitment from approval",()=>{
  assert.match(red,/verified account permission|publisher-specific/i);
  assert.ok(claim.affiliate_link===null);
  assert.equal(claim.publisher_acceptance,"UNVERIFIED");
  assert.equal(claim.email_rights,"UNVERIFIED");
});
test("No affiliate or commercial conclusions in independent investigation",()=>{
  assert.match(inv,/Simons, D\. J\., & Chabris/);
  assert.match(inv,/doi\.org\/10\.1068\/i0386/);
  assert.match(inv,/doi\.org\/10\.1073\/pnas\.2214930120/);
  assert.doesNotMatch(inv,/Zen12|Inspire3|Brainwave Shots/);
});
test("Six continuous captions cover precisely 0 to 40 seconds",()=>{
  const ranges=[...cap.matchAll(/(\d\d):(\d\d):(\d\d)\.\d{3} --> (\d\d):(\d\d):(\d\d)\.\d{3}/g)].map(m=>[+m[1]*3600 + +m[2]*60 + +m[3],+m[4]*3600 + +m[5]*60 + +m[6]]);
  assert.equal(ranges.length,6);
  assert.deepEqual(ranges,[[0,7],[7,14],[14,20],[20,27],[27,34],[34,40]]);
});
test("Attribution is unconditionally disabled",()=>{assert.equal(ACTIVE,false);assert.throws(collectOutboundEvent,/not activated/);});
test("Synthetic model rejects arbitrary / identifying keys and URLs",()=>{
  assert.throws(()=>validateSyntheticInput({source:"organic",topic:"zen12-guide",variant:"text",clicked:true,email:"sample@domain.test"}),/Unexpected field/);
  assert.throws(()=>validateSyntheticInput({source:"organic",topic:"zen12-guide",variant:"text",clicked:true,referrer:"https://example.com/?email=x"}),/Unexpected field/);
  assert.throws(()=>validateSyntheticInput({source:"organic",topic:"zen12-guide",variant:"text",clicked:true,utm:"hack"}),/Unexpected field/);
  assert.throws(()=>validateSyntheticInput({source:"organic",topic:"zen12-guide",variant:"text",clicked:true,url:"https://example.com"}),/Unexpected field/);
});
test("Synthetic model rejects unapproved source/topic/variant",()=>{
  const base={source:"organic",topic:"zen12-guide",variant:"text",clicked:true};
  assert.throws(()=>validateSyntheticInput({...base,source:"social/inject"}));
  assert.throws(()=>validateSyntheticInput({...base,topic:"unknown-path"}));
  assert.throws(()=>validateSyntheticInput({...base,variant:"new"}));
  assert.throws(()=>validateSyntheticInput({...base,clicked:"yes"}));
});
test("Synthetic aggregation suppresses groups smaller than threshold",()=>{
  assert.equal(MIN_GROUP_SIZE,20);
  const row={source:"organic",topic:"zen12-guide",variant:"text",clicked:true};
  assert.equal(summarizeSynthetic(Array(19).fill(row)).length,0);
  const out=summarizeSynthetic(Array(20).fill(row));
  assert.equal(out.length,1);
  assert.equal(out[0].impressions,20);
  assert.equal(out[0].click_rate,1);
});
test("Synthetic aggregation does not pool study variants across small cells",()=>{
  const rowA={source:"organic",topic:"zen12-guide",variant:"text",clicked:true};
  const rowB={source:"organic",topic:"zen12-guide",variant:"film",clicked:false};
  assert.equal(summarizeSynthetic([...Array(19).fill(rowA),...Array(19).fill(rowB)]).length,0);
});
