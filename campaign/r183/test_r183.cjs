"use strict";
const {test}=require("node:test");
const assert=require("node:assert/strict");
const fs=require("node:fs");
const q=require("./lead_truth_oracle.cjs");
const source=fs.readFileSync(__dirname+"/lead_truth_oracle.cjs","utf8");
const letter=fs.readFileSync(__dirname+"/04_OPTIONAL_PIRI_REIS.md","utf8");
const plain=fs.readFileSync(__dirname+"/04_PLAINTEXT.txt","utf8");
const html=fs.readFileSync(__dirname+"/04_REVIEW_ONLY.html","utf8");
const n={total:3,confirmed:3,unconfirmed:2,suppressed:0,paid:0};
const f={email:0,wpcom:3};
test("provider count is nonadditive",()=>{const r=q.reconcileCounts(n,f);assert.equal(r.counted_subscribers,3);assert.equal(r.pending_unconfirmed_requests,2);assert.equal(r.unconfirmed_additive_to_total,false);});
test("follower breakdown does not establish recipients",()=>assert.equal(q.reconcileCounts(n,f).email_eligible_recipients,null));
test("configured welcome is not received welcome",()=>assert.equal(q.reconcileCounts(n,f).successful_welcome_receipts,null));
test("aggregate cannot generate confirmed signup",()=>assert.equal(q.reconcileCounts(n,f).confirmed_signup_events,null));
test("nonsense counts fail closed",()=>assert.throws(()=>q.reconcileCounts({...n,total:-1},f)));
test("noninteger counts fail closed",()=>assert.throws(()=>q.reconcileCounts({...n,total:3.5},f)));
test("contradictory provider counts fail closed",()=>assert.throws(()=>q.reconcileCounts({...n,total:1},f)));
test("bad follower counts fail closed",()=>assert.throws(()=>q.reconcileCounts(n,{...f,email:null})));
for(const [name,input] of [
["query-string success",{origin:"browser-query",status:"subscribed",email_permission:true}],
["CSS class",{origin:"browser-class",status:"subscribed",email_permission:true}],
["download-view",{origin:"download-click",status:"subscribed",email_permission:true}],
["unsupported source",{origin:"self-reported",status:"subscribed",email_permission:true}],
["unconfirmed",{origin:"authenticated-provider-export",status:"not-confirmed",email_permission:true}],
["not opted in",{origin:"authenticated-provider-export",status:"subscribed",email_permission:false}],
["missing refs",{origin:"authenticated-provider-export",status:"subscribed",email_permission:true}],
["leaked email",{origin:"authenticated-provider-export",status:"subscribed",email_permission:true,proof_ref:"somebody@example.com",event_ref:"opaque_000000000000"}],
["tokenized URL",{origin:"authenticated-provider-export",status:"subscribed",email_permission:true,proof_ref:"https://site.com/secret",event_ref:"opaque_000000000000"}]
])test("reject "+name,()=>assert.equal(q.checkLeadCandidate(input).candidate,false));
const candidate={origin:"authenticated-provider-export",status:"subscribed",email_permission:true,proof_ref:"opaqueProof123456",event_ref:"opaqueEvent123456"};
test("opaque record is ONLY review candidate",()=>{const d=q.checkLeadCandidate(candidate);assert.equal(d.candidate,true);assert.equal(d.public_event_name,null);assert.equal(d.send_authorized,false);});
for(const flag of ["opted_out","paused","bounced"]){test("reject "+flag,()=>assert.equal(q.checkLeadCandidate({...candidate,[flag]:true}).candidate,false));}
test("deduplicate refs without PII",()=>{const r=q.dedupeCandidates([candidate,candidate]);assert.equal(r.accepted.length,1);assert.deepEqual(r.rejected,["DUPLICATE_EVENT_REFERENCE"]);assert.equal(r.confirmed_signup_events,null);});
test("empty proofs always hold",()=>assert.equal(q.releaseGate({}).editorial,"HOLD_UNSENT"));
test("merchant without permissions holds",()=>assert.equal(q.releaseGate({founder_final_send_approval:true}).commercial,"HOLD_MERCHANT"));
test("even all-true flags do not initiate sending",()=>{const p=Object.fromEntries(["founder_final_send_approval","email_eligibility_verified","received_welcome_verified","native_email_footer_verified","publisher_postal_verified","unsubscribe_verified","merchant_email_permission_verified","merchant_link_authorized","live_warmup_guide_verified","checkout_terms_verified"].map(k=>[k,true]));assert.equal(q.releaseGate(p).send_authorized,false);});
test("no network or subscriber operations",()=>assert.doesNotMatch(source,/\bfetch\(|XMLHttpRequest|sendMail\(|createSubscriber\(|subscriber.*add\(/));
test("single authentic published editorial destination",()=>{assert.match(letter,/finalvestige.com\/2026\/11\/02\/piri-reis-map/);assert.match(letter,/10.1590\/S0101-47142009000100007/);});
test("subject preheader consistent and no commercial link",()=>{for(const s of [letter,plain,html]){assert.match(s,/The coast that outlived the certainty/);assert.match(s,/1513 chart/);assert.doesNotMatch(s,/awin1.com|clickbank|affiliates\.inspire3\.com/);}});
test("all reviewers are intentionally blocked",()=>{for(const s of [letter,plain,html]){assert.match(s,/UNSENT/);assert.match(s,/VALID_FV_POSTAL_ADDRESS_REQUIRED/);assert.match(s,/JETPACK_UNSUBSCRIBE_RENDER_AND_FUNCTION_REQUIRED/);}});
test("HTML reviewer has no network/email form/scripts",()=>{assert.doesNotMatch(html,/<script|<form|<iframe|onerror=|onclick=/i);assert.match(html,/<table/);assert.match(html,/lang="en"/);});
