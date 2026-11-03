// Native Node suite to run in a proper checkout. Not executed as Node by the agent.
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";
import {isSyntheticRow,summarizeSynthetic} from "./measurement.mjs";
const d=path.dirname(fileURLToPath(import.meta.url)), read=f=>fs.readFileSync(path.join(d,f),"utf8");
const A=read("pilot-a.html"),B=read("pilot-b.html"),H=read("mind-hub.html"),V=read("film-40s.vtt");
const C=JSON.parse(read("claims.json")), S=JSON.parse(read("sources.json"));
function substantive(s){return s.split('<div class="fv96-guide" id="fv96-guide">')[1]?.split("</div>")[0];}
test("identical substantive guide in A/B",()=>assert.equal(substantive(A),substantive(B)));
for(const [name,s] of [["text",A],["film",B]]){
 test(name+" CTA is disabled with adjacent disclosure",()=>assert.match(s,/<p class="disclosure">[\s\S]*?<\/p>\s*<button type="button" disabled>/));
 test(name+" excludes active merchant destinations",()=>assert.doesNotMatch(s,/<a[^>]+href="[^"]*(zen12|inspire3|hypnosislive|brainwaveshots)\./i));
 test(name+" excludes capture/tracking and broken video",()=>assert.doesNotMatch(s,/<(?:form|script|iframe|input|video)\b/i));
 test(name+" never asserts seller equivalence",()=>assert.doesNotMatch(s,/Zen12 (?:proves|delivers) (?:an hour|one hour)/i));
}
test("film variant has poster and full no-JS transcript",()=>{assert.match(B,/<svg/);assert.match(B,/<details open>/);assert.doesNotMatch(A,/<svg/);});
test("four hub streams",()=>{for(const n of ["mind96a","mind96b","mind96c","mind96d"])assert.ok(H.includes(n));});
test("sources and claims linked",()=>{const ids=new Set(S.map(s=>s.id));assert.ok(S.length>=20);assert.ok(C.claims.length>=40);for(const c of C.claims)for(const s of c.sources)assert.ok(ids.has(s));});
test("all release gates closed",()=>{assert.equal(C.gates.length,30);assert.ok(C.gates.every(g=>g.status==="CLOSED"));});
test("six consecutive VTT intervals to 40 seconds",()=>{const x=[...V.matchAll(/(\d\d:\d\d:\d\d\.\d\d\d) --> (\d\d:\d\d:\d\d\.\d\d\d)/g)];assert.equal(x.length,6);assert.equal(x[0][1],"00:00:00.000");assert.equal(x.at(-1)[2],"00:00:40.000");for(let i=1;i<x.length;i++)assert.equal(x[i][1],x[i-1][2]);});
const valid={count:20,event:"offer_intent",source:"search",synthetic:true,topic:"zen12",variant:"text"};
test("synthetic aggregate validates",()=>assert.ok(isSyntheticRow(valid)));
test("min 20 suppresses small cells",()=>assert.equal(summarizeSynthetic([{...valid,count:19}]).length,0));
test("forbid threshold override",()=>assert.throws(()=>summarizeSynthetic([valid],1)));
for(const field of ["email","ip","user_id","referrer_url","order_id","phone","cookie","click_id"]){test("reject "+field,()=>assert.equal(isSyntheticRow({...valid,[field]:"x"}),false));}
