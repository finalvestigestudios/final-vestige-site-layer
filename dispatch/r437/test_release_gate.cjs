"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const {test}=require("node:test");
const root=__dirname;
const man=JSON.parse(fs.readFileSync(path.join(root,"source_manifest.json"),"utf8"));
const {adjudicate}=require("./release_gate.cjs");
test("source manifest canonical unchanged, six and mix",()=>{
 assert.equal(man.canonical_head,"d57ccdba3aee8f065e143e101c2945f4f3d01647");
 assert.equal(man.status,"HOLD_UNSENT");
 assert.equal(man.records.length,6);
 assert.equal(man.records.filter(r=>r.kind==="editorial").length,4);
 assert.equal(man.records.filter(r=>r.kind==="commercial-review-pending").length,2);
});
test("each reviewer asset has one real first paragraph, external chrome, safe inert merchant destinations",()=>{
 for(const r of man.records){
 const html=fs.readFileSync(path.join(root,"previews","issue-"+String(r.number).padStart(2,"0")+".html"),"utf8");
 const text=fs.readFileSync(path.join(root,"previews","issue-"+String(r.number).padStart(2,"0")+".txt"),"utf8");
 assert.match(html,/<html lang="en">/);
 assert.match(html,/role="presentation"/);
 assert.ok(html.indexOf("INTERNAL REVIEW")<html.indexOf("FINAL VESTIGE STUDIOS"));
 assert.ok(text.includes(r.first_paragraph));
 assert.doesNotMatch(html,/<script|<iframe|<form|onerror=|onclick=/i);
 assert.doesNotMatch(html,/href="https:\/\/(?:zen12|inspire3|hypnosislive)/i);
 assert.doesNotMatch(html,/VALID_POSTAL_ADDRESS_REQUIRED|JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED/);
 }
});
test("missing approvals always block every issue",()=>{const result=adjudicate(man,{});assert.equal(result.may_send,false);assert.equal(result.findings.length,6);assert.ok(result.findings.every(x=>x.blocked.length));});
test("even synthetic all-true proof NEVER permits send",()=>{
 const keys=["founder_final_approval","provider_eligible_inboxes_verified","welcome_received_verified","native_jetpack_preview_verified","valid_fv_postal_in_received_mail","working_unsubscribe_in_received_mail","named_partner_email_permission","current_exact_offer_and_terms","approved_live_warmup_guide","issued_earning_link","seller_checkout_and_settlement_verified"];
 const result=adjudicate(man,Object.fromEntries(keys.map(k=>[k,true])));
 assert.equal(result.may_send,false);assert.ok(result.findings.filter(x=>x.kind==="commercial-review-pending").every(x=>x.may_send===false));
 assert.ok(result.findings.filter(x=>[1,2,4].includes(x.issue)).every(x=>x.blocked.includes("founder_copy_selection_and_review")));
});
test("corrupt or missing source records rejected",()=>{assert.throws(()=>adjudicate({...man,records:[]},{}));assert.throws(()=>adjudicate({...man,status:"READY"},{}));assert.throws(()=>adjudicate(null,{}));});
