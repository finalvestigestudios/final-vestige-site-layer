"use strict";
const fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict");
const d=__dirname,l=JSON.parse(fs.readFileSync(path.join(d,"r156-offer-proof.json"),"utf8"));let n=0;
function ok(label,fn){fn();n++;console.log("PASS "+label)}
for(const id of ["03","05"]){const m=l.messages.find(x=>x.id===id),md=fs.readFileSync(path.join(d,id+"-OPTIONAL-UNSENT.md"),"utf8"),h=fs.readFileSync(path.join(d,id+"-reviewer.html"),"utf8"),t=fs.readFileSync(path.join(d,id+"-reviewer.txt"),"utf8");
ok(id+" unsent review",()=>{for(const s of [md,h,t])assert.match(s,/UNSENT|NOT EMAIL READY|NOT FOR SEND/)});
ok(id+" honest subject preheader",()=>{assert.ok(m.subject.length<65&&m.preheader.length<125);for(const s of [md,h,t])assert.ok(s.includes(m.subject)&&s.includes(m.preheader))});
ok(id+" exact product",()=>{assert.ok(md.includes(m.product));assert.ok(md.length>2500)});
ok(id+" disclosure",()=>{for(const s of [md,h,t])assert.match(s,/Commercial disclosure:/);assert.ok(md.indexOf("Commercial disclosure:")>md.indexOf(m.cta))});
ok(id+" source fidelity",()=>{for(const u of m.sources)for(const s of [md,h,t])assert.ok(s.includes(u))});
ok(id+" inactive offer",()=>{assert.equal(m.merchant_affiliate_url,null);assert.equal(m.substitution_approved,false);assert.ok(md.includes(m.cta)&&t.includes(m.cta));assert.ok(h.includes("NO CLICKABLE CTA"))});
ok(id+" legal holds",()=>{for(const s of [md,h,t])for(const p of ["[[VALID_POSTAL_ADDRESS_REQUIRED]]","[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"])assert.ok(s.includes(p))});
ok(id+" safe email reviewer",()=>{assert.match(h,/<html lang="en">/);assert.match(h,/table role="presentation"/);assert.match(h,/name="viewport"/);assert.doesNotMatch(h,/<script|<form|<iframe|<img|<style|<link/i)});
}
ok("canonical 4:2",()=>{assert.equal(l.canonical_mix.editorial,4);assert.equal(l.canonical_mix.commercial_reservations,2)});
ok("all false permissions",()=>{assert.ok(Object.values(l.merchant_approval).every(v=>v===false));assert.ok(Object.values(l.legal_preview).every(v=>v===false));assert.equal(l.founder_send_approval,false)});
ok("no fake revenue",()=>{assert.equal(l.verified_paid_orders,null);assert.equal(l.realized_net_revenue,null);assert.equal(l.qualified_human_sessions,null);assert.equal(l.net_revenue_per_1000,null)});
ok("nonadditive snapshot",()=>{assert.equal(l.subscriber.nonadditive,true);assert.equal(l.subscriber.email_eligible,null)});
console.log("R156 native Node static tests: "+n+" PASS (not real email or merchant QA)");