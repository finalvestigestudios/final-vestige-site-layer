#!/usr/bin/env node
// Source-only safety verifier. Run: node mind/r433/verify.mjs
// Does not call web, CMS, merchant, Jetpack, social platforms, or analytics.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const dir = dirname(fileURLToPath(import.meta.url));
const read = (n) => readFileSync(join(dir,n),"utf8");
const a=read("ZEN12_A_TEXT_GUIDE.html");
const b=read("ZEN12_B_OPTIONAL_FILM_CONCEPT.html");
const hub=read("MIND_ARCHIVE_SOURCE_ONLY.html");
const vtt=read("film.vtt");
const article=read("THE_HAND_THAT_WASNT_YOURS.md");
const plan=read("CONVERSION_ACCEPTANCE.md");
const matrix=JSON.parse(read("CLAIM_SOURCE_PERMISSION_MATRIX.json"));
let checks=0;
const ok=(v,msg)=>{assert.ok(v,msg);checks++};
const no=(v,msg)=>{assert.ok(!v,msg);checks++};
const starts=(x,y,msg)=>ok(x.includes(y),msg);
for(const [label,html] of [["text",a],["film",b],["hub",hub]]){
 starts(html,"<!doctype html>","doctype "+label);
 starts(html,'<html lang="en">',"lang "+label);
 starts(html,'href="#',"skip anchor "+label);
 ok(html.includes('id="main"') || html.includes('id="content"'),"main landmark "+label);
 no(/<script\b/i.test(html),"no script "+label);
 no(/<iframe\b/i.test(html),"no iframe "+label);
 no(/<form\b/i.test(html),"no form "+label);
 no(/\bautoplay\b\s*=/i.test(html),"no autoplay attribute "+label);
 no(/href=["']https?:\/\/(?:www\.)?(?:zen12\.com|inspire3\.com|hypnosislive\.com|brainwaveshots\.com|affiliates\.inspire3\.com)/i.test(html),"no merchant or earning links "+label);
 starts(html,"prefers-reduced-motion","reduced motion CSS "+label);
 starts(html,"noindex,nofollow","draft robots "+label);
}
starts(a,'disabled aria-disabled="true"',"disabled merchant A");
starts(b,'disabled aria-disabled="true"',"disabled merchant B");
for(const [label,html] of [["text",a],["film",b]]){
 starts(html,"If an earning link is later approved","conditional disclosure "+label);
 const disclosure=html.indexOf("If an earning link is later approved");
 const button=html.indexOf("Offer unavailable");
 ok(disclosure>=0&&button>disclosure&&button-disclosure<800,"disclosure immediately before CTA "+label);
 ok(/five/i.test(html),"five objections "+label);
 ok(/what we cannot say/i.test(html),"claim restraint "+label);
 starts(html,'href="https://finalvestige.com/focus/"',"single fieldbook link "+label);
 no(/<video\b/i.test(html),"no false playable video "+label);
}
const core=(html)=>html.slice(html.indexOf('<header class="hero">'),html.indexOf("</main>"));
ok(core(a)===core(b),"identical substantive buyer body across A/B");
starts(b,"42-second film","film duration");
starts(b,"<svg","original poster");
starts(b,"<details>","transcript disclosure");
starts(b,"00:35–00:42","film closing cue");
starts(vtt,"WEBVTT","vtt label");
const cueLines=[...vtt.matchAll(/(\d\d:\d\d:\d\d\.\d{3}) --> (\d\d:\d\d:\d\d\.\d{3})/g)];
ok(cueLines.length===6,"six caption cues");
const sec=(t)=>{const x=t.split(":");return (+x[0])*3600+(+x[1])*60+parseFloat(x[2]);};
cueLines.forEach((c,i)=>{ok(sec(c[1])===i*7,"cue starts at "+i*7);ok(sec(c[2])===(i+1)*7,"cue ends at "+(i+1)*7)});
for(const str of ["Botvinick","Rohde","Lush","Slater","Puységur","synchronous","asynchronous","Demand Characteristics","no live shopping","refund","source"]){
 starts(article,str,"article evidence "+str);
}
starts(article,"https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/","archive source");
ok(article.split(/\s+/).length>=2300,"substantive original manuscript");
starts(article,"S1","source notes");
ok(matrix.claims.length>=30,"claim matrix complete");
ok(matrix.release_gates.length===28,"28 gates");
ok(matrix.release_gates.every(g=>g.status==="HOLD"),"all gates on hold");
ok(matrix.commercial_activated===false,"no commercial activation");
ok(matrix.approved_earning_urls.length===0,"zero approved URLs");
ok(matrix.settled_sales.length===0,"zero claimed settled sales");
for(const g of matrix.release_gates){ok(g.reason.length>30,"documented hold "+g.id)}
for(const c of matrix.claims){ok(c.id&&c.type&&c.status,"structured claim "+c.id);for(const id of c.source_ids){ok(Boolean(matrix.sources[id]),"valid source "+c.id+"."+id)}}
for(const key of ["affiliate_outbound","merchant_confirmed_purchase","qualified-human","refund","UNMATCHED","NOT COMPUTABLE","Existing","Founder","Consent","HOLD"]){ok(plan.toLowerCase().includes(key.toLowerCase()),"acceptance topic "+key)}
no(plan.includes("Grok posted all three"),"no fake creator postings");
console.log("PASS",checks,"source assertions; commercial gates",matrix.release_gates.length,"HOLD; no publication or merchant test");
