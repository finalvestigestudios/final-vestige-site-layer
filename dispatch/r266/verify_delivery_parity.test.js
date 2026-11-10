"use strict";
/* Pure synthetic adversarial fixture tests, no network or sending.
 * Run: node dispatch/r266/verify_delivery_parity.test.js
 */
const assert=require("node:assert/strict");
const {audit,canonicalPDF}=require("./delivery_parity.js");
const fixture=require("./observed_snapshot.json");
const clone=()=>JSON.parse(JSON.stringify(fixture));
let passed=0;
function check(name,fn){
 try{fn();passed++;console.log("PASS "+name);}
 catch(e){console.error("FAIL "+name+" "+e.message);process.exitCode=1;}
}
check("baseline valid but never send-ready",()=>{const r=audit(clone());assert.equal(r.pass,true);assert.equal(r.status,"HOLD_UNSENT");assert.equal(r.evidence_status,"CONFIGURATION_PARITY_ONLY");});
check("link and media observed, inbox unknown",()=>{const r=audit(clone());assert.equal(r.stages.media_registered,"OBSERVED");assert.equal(r.stages.three_links_match,"OBSERVED");assert.equal(r.stages.received_welcome,"UNKNOWN");});
check("never invent subscriber count or orders",()=>{const r=audit(clone());assert.equal(r.actual_eligible_recipients,null);assert.equal(r.independently_paid_orders,null);assert.equal(r.realized_net_revenue,null);});
for(const [i,u] of ["http://finalvestige.com/a.pdf","https://evil.example/a.pdf","https://finalvestige.com.evil.example/a.pdf","https://u:p@finalvestige.com/a.pdf","https://finalvestige.com/wp-content/uploads/a.pdf?ref=x","https://finalvestige.com/wp-content/uploads/a.pdf#f","https://finalvestige.com/private/a.pdf","javascript:alert(1)","",null].entries()) check("unsafe URL "+i,()=>assert.equal(canonicalPDF(u),false));
const mutations=[
 ["no evidence",s=>delete s.evidence],
 ["empty gates",s=>s.evidence={} ],
 ["extra evidence",s=>s.evidence.user_email="bad"],
 ["unexpected PII root",s=>s.subscriber_email="leak"],
 ["tamper welcome link",s=>s.newsletter.welcome_pdf_url="https://finalvestige.com/wp-content/uploads/alt.pdf"],
 ["tamper Focus link",s=>s.focus.download_url="https://finalvestige.com/wp-content/uploads/alt.pdf"],
 ["offsite PDF",s=>s.media.source_url="https://bad.example/wp-content/uploads/a.pdf"],
 ["wrong MIME",s=>s.media.mime_type="image/png"],
 ["media absent",s=>delete s.media],
 ["wrong media size",s=>s.media.bytes=30],
 ["wrong media id",s=>s.media.id=1],
 ["wrong Focus page id",s=>s.focus.page_id=100],
 ["unpublished Focus",s=>s.focus.published=false],
 ["unpublished Dispatch",s=>s.dispatch.published=false],
 ["commercial notice suppressed Focus",s=>s.focus.discloses_possible_commissions=false],
 ["commercial notice altered Dispatch",s=>s.dispatch.discloses_possible_commissions=true],
 ["removed restart advice risk",s=>s.focus.troubleshooting_says_sign_up_again=false],
 ["newsletter off",s=>s.newsletter.subscriptions=false],
 ["auto email on",s=>s.newsletter.email_new_posts_by_default=true],
 ["excerpt mode",s=>s.newsletter.email_content_format="excerpt"],
 ["sender tampered",s=>s.newsletter.from_name="Unknown"],
 ["reply-to tampered",s=>s.newsletter.reply_to="author"],
 ["welcome not configured",s=>s.newsletter.welcome_configured=false],
 ["no timestamp",s=>delete s.observed_at],
 ["invalid timestamp",s=>s.observed_at="today"],
 ["missing source references",s=>s.sources.references=[]],
 ["external unknown source",s=>s.sources.references.push("https://evil.example")],
 ["negative diagnostic",s=>s.diagnostics.confirmed=-1],
 ["fractional diagnostic",s=>s.diagnostics.total=3.2],
 ["missing diagnostic",s=>delete s.diagnostics.unconfirmed],
 ["partial followers",s=>s.followers.partial=true],
 ["false sent-proof",s=>s.evidence.received_welcome={status:"VERIFIED",proof_id:null}],
 ["unauthenticated proof ID",s=>s.evidence.public_http={status:"VERIFIED",proof_id:"fake"}],
 ["unexpected proof field",s=>s.evidence.public_http.email="secret"],
 ["missing founder gate",s=>delete s.evidence.founder_final_send_approval],
 ["missing address gate",s=>delete s.evidence.postal_address_render]
];
for(const [name,fn] of mutations)check("fail closed: "+name,()=>{
  const s=clone();fn(s);const result=audit(s);
  assert.equal(result.pass,false,JSON.stringify(result));assert.equal(result.status,"HOLD_UNSENT");
});
check("attested received-message evidence never grants release",()=>{
 const s=clone();s.evidence.received_welcome={status:"VERIFIED",proof_id:"fvproof-confirm-00001234"};
 const r=audit(s);assert.equal(r.status,"HOLD_UNSENT");assert.equal(r.stages.received_welcome,"ATTESTED_NOT_INDEPENDENTLY_VALIDATED");
});
console.log("TOTAL "+passed+" checks "+(process.exitCode?"FAILED":"PASSED"));
