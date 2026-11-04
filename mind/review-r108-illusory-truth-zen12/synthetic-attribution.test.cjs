"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const {validateSynthetic,reportSyntheticOnly,recordLiveEvent,MIN_GROUP}=require("./synthetic-attribution.cjs");
const row = (extra={})=>({event_type:"guide_view",topic:"zen12",variant:"A",source_bucket:"organic",day:"2026-11-03",synthetic:true,...extra});
const file = name=>fs.readFileSync(path.join(__dirname,name),"utf8");
const a=()=>file("zen12-A-text-only.html"), b=()=>file("zen12-B-storyboard-plus-guide.html");
test("accept exact synthetic schema",()=>assert.equal(validateSynthetic(row()).topic,"zen12"));
for(const key of ["email","ip","referrer","user_agent","utm","order_id","click_id","purchase_id","timestamp","phone","device_id"]) {
  test("reject extra identifying field "+key,()=>assert.throws(()=>validateSynthetic(row({[key]:"sensitive"}))));
}
test("reject human/live events",()=>assert.throws(()=>validateSynthetic(row({synthetic:false}))));
test("reject unknown topic",()=>assert.throws(()=>validateSynthetic(row({topic:"my-secret-query"}))));
test("reject raw referrer as source bucket",()=>assert.throws(()=>validateSynthetic(row({source_bucket:"https://example.com/?email=user"}))));
test("reject high resolution timestamp",()=>assert.throws(()=>validateSynthetic(row({day:"2026-11-03T12:34:56Z"}))));
test("reject impossible schema and absent fields",()=>assert.throws(()=>validateSynthetic({email:"a@example.com"})));
test("reject arrays and null",()=>{assert.throws(()=>validateSynthetic([]));assert.throws(()=>validateSynthetic(null));});
test("19 events suppress",()=>assert.deepEqual(reportSyntheticOnly(Array.from({length:19},()=>row())),[]));
test("20 events aggregate",()=>assert.equal(reportSyntheticOnly(Array.from({length:20},()=>row()))[0].events,20));
test("distinct groups under 20 suppress separately",()=>assert.deepEqual(reportSyntheticOnly([...Array.from({length:19},()=>row()),...Array.from({length:19},()=>row({variant:"B"}))]),[]));
test("live kill switch throws",()=>assert.throws(recordLiveEvent));
test("minimum threshold locked",()=>assert.equal(MIN_GROUP,20));
test("A/B identical guide once nonplaying storyboard is excluded",()=>{
  const bb=b(); const start=bb.indexOf('<figure class="fv-original-video-concept">'), end=bb.indexOf("<h2>What comes in the offer?</h2>");
  assert.ok(start>0 && end>start);
  assert.equal(bb.slice(0,start)+bb.slice(end),a());
});
for(const [name,get] of [["A",a],["B",b]]){
  test(name+" native disabled CTA and near disclosure",()=>{
    const s=get(),pos=s.indexOf('<button type="button" disabled'), disclosure=s.indexOf("If you purchase through an approved link in the future");
    assert.ok(pos>disclosure && pos-disclosure<420);
    assert.doesNotMatch(s,/<a[^>]+href=["']https?:\/\/(?:www\.)?(?:inspire3|zen12)\.com/i);
    assert.doesNotMatch(s,/<(?:script|iframe|form)\b/i);
    assert.doesNotMatch(s,/(?:\sautoplay(?:\s|=|>)|dataLayer|navigator\.sendBeacon|localStorage|trackPixel|<video\b)/i);
  });
}
test("B original static poster has meaningful accessibility text and transcript",()=>{assert.match(b(),/role="img"/);assert.match(b(),/<title id="film-title"/);assert.match(b(),/Complete storyboard transcript/);assert.match(b(),/no playable MP4/i);});
test("WebVTT covers 0 to 40 seconds in six contiguous cues",()=>{
 const t=file("zen12-storyboard-40s.vtt");
 assert.ok(t.startsWith("WEBVTT"));
 const cues=[...t.matchAll(/(\d\d):(\d\d):(\d\d)\.(\d{3}) --> (\d\d):(\d\d):(\d\d)\.(\d{3})/g)];
 assert.equal(cues.length,6);
 const ms=(a,b,c,d)=>((Number(a)*60+Number(b))*60+Number(c))*1000+Number(d);
 let end=0;for(const [,h,m,s,ms1,hh,mm,ss,ms2] of cues){const start=ms(h,m,s,ms1),finish=ms(hh,mm,ss,ms2);assert.equal(start,end);assert.ok(finish>start);end=finish;}
 assert.equal(end,40000);
});
test("closed release gates, no affiliate activation",()=>{
 const d=JSON.parse(file("evidence-and-release-matrix.json"));assert.ok(d.release_gates.every(g=>g.status==="HOLD_CLOSED" && !g.passed));
 assert.equal(d.activation.affiliate_enabled,false);assert.equal(d.activation.tracking_enabled,false);
});
