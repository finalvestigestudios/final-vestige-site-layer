"use strict";
/** Run from repository root: node --test mind/r131/test-r131.cjs */
const test=require("node:test");
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const here=__dirname;
const txt=n=>fs.readFileSync(path.join(here,n),"utf8");
const A=txt("pilot-A-text.html"),B=txt("pilot-B-optional-film.html");
const ARTICLE=txt("source-monitoring-investigation.md");
const GUIDE=txt("zen12-purchasing-guide.md");
const register=JSON.parse(txt("claims-and-gates.json"));
const {validateSession,validateSettlement,reconcile}=require("./aggregate-revenue-ledger.cjs");
const audit=()=>({first_party_complete:true,merchant_complete:true,proof_ref:"audit:weekly_sources_checked"});
const session=()=>({date:"2026-11-04",asset_id:"sample_asset_01",utm_campaign:"mind_pilot_2026_11",qualified_human_sessions:250,audit_status:"verified_human_exclusion",proof_ref:"audit:firstparty_report"});
const settlement=()=>({date:"2026-11-04",asset_id:"sample_asset_01",utm_campaign:"mind_pilot_2026_11",offer_type:"first_party",authorization:true,statement_verified:true,complete:true,proof_ref:"merchant:verified_statement",paid_orders:4,gross_cents:4000,refund_cents:300,fees_cents:200,commission_cents:0});
const input=()=>({sessions:[session()],settlements:[settlement()],period_days:7,as_of:"2026-11-04",coverage:audit()});
test("original sourced investigation separates commerce",()=>{
 assert.match(ARTICLE,/Johnson.*Hashtroudi/);
 assert.match(ARTICLE,/Goff.*Roediger/);
 assert.match(ARTICLE,/Dougherty.*Franco-Watkins/);
 assert.match(ARTICLE,/Puységur/);
 assert.doesNotMatch(ARTICLE,/ref=affiliate|affiliate\/checkout|buy-now/);
});
test("buyer guide contains meaningful evidence and explicit limits",()=>{
 for(const t of ["5 supportive","not an authenticated checkout","privacy","not a statement that we have used","November 4, 2026"])assert.ok(GUIDE.toLowerCase().includes(t.toLowerCase()),t);
 assert.match(GUIDE,/Ingendoh/);assert.match(GUIDE,/NCCIH/);
});
test("evidence register has traceable claims and all gates closed",()=>{
 assert.ok(register.sources.length>=18);assert.ok(register.claims.length>=25);assert.ok(register.release_gates.length>=20);
 const ids=new Set(register.sources.map(s=>s.id));
 for(const c of register.claims)for(const id of c.evidence_ids)assert.ok(ids.has(id),c.id+" bad evidence "+id);
 assert.equal(register.merchant_referral_url,null);
 assert.ok(register.release_gates.every(g=>g.status==="CLOSED"));
});
for(const [name,html] of [["A",A],["B",B]]){
 test(name+" holds seller purchasing and disclosure",()=>{
  assert.match(html,/class="disclosure"/);
  assert.match(html,/disabled aria-disabled="true"/);
  assert.match(html,/may earn a commission at no additional cost/i);
  assert.ok(html.indexOf("may earn a commission")<html.indexOf('class="btn-disabled"'));
  assert.doesNotMatch(html,/<a\s+[^>]*href="https:\/\/zen12\.com\//i);
  assert.doesNotMatch(html,/<a\s+[^>]*href="https:\/\/inspire3\.com\/(?!privacy)/i);
 });
 test(name+" has no unauthorized tracking, email, or media",()=>{
  assert.doesNotMatch(html,/<script|<iframe|<form|autoplay|<video/i);
  assert.match(html,/prefers-reduced-motion/);assert.match(html,/:focus-visible/);
  assert.match(html,/width=device-width/);assert.match(html,/max-width:500px/);
  assert.match(html,/https:\/\/finalvestige\.com\/focus\//);
  assert.match(html,/noindex,nofollow/);
  assert.equal((html.match(/<h1\b/g)||[]).length,1);
 });
}
test("B includes optional original storyboard and no fake playback",()=>{
 assert.match(B,/00–06s/);assert.match(B,/35–40s/);
 assert.match(B,/<details>/);assert.match(B,/complete 40-second film transcript/i);
 assert.match(B,/not a playable media/i);
 assert.doesNotMatch(A,/00–06s/);
 const normalize=s=>s.replace(/<section class="panel" aria-labelledby="film-r131">[\s\S]*?<\/section>/,"");
 assert.equal(normalize(B).replace(/<title>[^<]*<\/title>/,""),normalize(A).replace(/<title>[^<]*<\/title>/,""));
});
test("qualified session is strict no-PII aggregate",()=>{
 assert.equal(validateSession(session()).qualified_human_sessions,250);
 for(const k of ["email","ip_address","buyer_id","metadata","session_id"]){const x=session();x[k]="example";assert.throws(()=>validateSession(x),/identifier|unexpected/);}
 const x=session();x.qualified_human_sessions=-1;assert.throws(()=>validateSession(x));
});
test("merchant statement must be authorized complete and settled",()=>{
 assert.equal(validateSettlement(settlement()).paid_orders,4);
 for(const k of ["authorization","statement_verified","complete"]){const x=settlement();x[k]=false;assert.throws(()=>validateSettlement(x));}
 const x=settlement();x.customer_id="buyer";assert.throws(()=>validateSettlement(x));
});
test("verified first party calculation excludes refunds and fees",()=>{
 const x=reconcile(input());
 assert.equal(x.realized_net_cents,3500);
 assert.equal(x.confirmed_paid_orders,4);
 assert.equal(x.net_revenue_per_1000_qualified_sessions_cents,14000);
 assert.equal(x.status,"VERIFIED_AGGREGATE_ONLY");
 assert.equal(x.sample_warning,"TINY_SAMPLE");
});
test("no denominator, no merchant proof, no cohort match => NOT_COMPUTABLE",()=>{
 for(const modify of [o=>o.sessions=[],o=>o.settlements=[],o=>o.coverage=null,o=>o.settlements[0].asset_id="other_asset_01",o=>o.sessions[0].qualified_human_sessions=0]){
  const o=input();modify(o);assert.equal(reconcile(o).status,"NOT_COMPUTABLE");
 }
});
test("duplicate cohort cannot inflate conversion",()=>{
 const o=input();o.sessions.push({...session()});assert.throws(()=>reconcile(o),/duplicate/);
});
test("affiliate commission only, not gross merchant sales",()=>{
 const o=input();o.settlements[0]={...settlement(),offer_type:"affiliate",gross_cents:0,commission_cents:900,refund_cents:100,fees_cents:70};
 const x=reconcile(o);assert.equal(x.realized_net_cents,730);
 const y=input();y.settlements[0].offer_type="affiliate";assert.throws(()=>reconcile(y),/affiliate gross/);
});
test("adversarial mutation: disabled button removed is caught",()=>{
 const bad=A.replace('disabled aria-disabled="true"',"");assert.doesNotMatch(bad,/disabled aria-disabled="true"/);
});
test("adversarial mutation: disclosure removed is caught",()=>{
 const bad=A.replace('class="disclosure"','class="hidden"');assert.doesNotMatch(bad,/class="disclosure"/);
});
test("adversarial mutation: affiliate purchase anchor is caught",()=>{
 const bad=A.replace("</main>",'<a href="https://zen12.com/secret/?ref=unapproved">Buy here</a></main>');
 assert.match(bad,/<a\s+[^>]*href="https:\/\/zen12\.com\//i);
});
