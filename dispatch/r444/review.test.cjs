"use strict";const a=require("node:assert/strict"),fs=require("node:fs"),p=require("node:path"),d=__dirname;
const t=fs.readFileSync(p.join(d,"ISSUE01_OFFLINE.txt"),"utf8"),h=fs.readFileSync(p.join(d,"ISSUE01_OFFLINE.html"),"utf8"),m=fs.readFileSync(p.join(d,"ISSUE01_UNADOPTED.md"),"utf8"),j=JSON.parse(fs.readFileSync(p.join(d,"CLAIM_AND_CTA_LEDGER.json"),"utf8"));
let passed=0;function check(name,fn){fn();passed++;console.log("PASS",name)}
check("slot and offer allocation",()=>{a.equal(j.slot,1);a.deepEqual(j.commercial_slots,[3,5]);a.equal(j.merchant_names[5],"Hypnosis Live")});
check("subject and preheader parity",()=>{for(let x of [t,h,m]){a.ok(x.includes(j.subject));a.ok(x.includes(j.preheader));}});
check("primary CTA accurate and present",()=>{a.ok(j.primary_cta.endsWith("/change-blindness/"));for(let x of [t,h,m])a.ok(x.includes(j.primary_cta))});
check("source completeness",()=>{for(let s of j.sources)for(let x of [t,h,m])a.ok(x.includes(s))});
check("no ad claims or tracking in editorial",()=>{for(let x of [t,h,m])a.ok(!/utm_|buy now|act now|guaranteed income|cures anxiety|zen12\.com|hypnosislive\.com/i.test(x))});
check("hard stop survives",()=>{for(let x of [t,h,m]){a.ok(x.includes("VALID_FV_POSTAL_ADDRESS_REQUIRED"));a.ok(x.includes("VERIFIED_JETPACK_UNSUBSCRIBE_REQUIRED"));}});
check("no fabricated release attestations",()=>{for(let x of Object.values(j.all_release_proofs))a.equal(x,false)});
check("single promotional button",()=>a.equal((h.match(/>Read the investigation</g)||[]).length,1));
check("email-safe static markup",()=>{a.ok(h.includes('lang="en"'));a.ok(h.includes('role="presentation"'));a.ok(!/<script|<iframe|<form|<img/i.test(h))});
check("complete substantive email",()=>{a.ok(t.split(/\s+/).length>550);a.ok(t.includes("A person, a door, a missed substitution"));a.ok(t.includes("What it means for an evidence-first studio"))});
console.log(passed+" tests passed; REVIEW ONLY; NO SEND PERMISSION");
