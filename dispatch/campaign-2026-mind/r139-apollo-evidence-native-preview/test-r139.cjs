"use strict";
/* R139 non-sending source-based regression suite.
 * Run: node dispatch/campaign-2026-mind/r139-apollo-evidence-native-preview/test-r139.cjs
 * Native Node not claimed until actually executed. No requests or WordPress writes.
 */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
require("./guard-r139.cjs");
const gate=globalThis.FVDispatchR139;
const here=__dirname;
const md=fs.readFileSync(path.join(here,"issue04-optional.md"),"utf8");
const html=fs.readFileSync(path.join(here,"issue04-offline-email-review.html"),"utf8");
const matrix=JSON.parse(fs.readFileSync(path.join(here,"source-and-gates.json"),"utf8"));
let passed=0;
function test(label, fn){fn();passed++;process.stdout.write("PASS "+String(passed).padStart(2,"0")+" "+label+"\n");}
function mustFail(label, fn){test(label,()=>assert.equal(fn().pass,false));}
function replaceOne(src,a,b){assert(src.includes(a), "Fixture precondition missing: "+a);return src.replace(a,b);}
const originalMd=gate.auditManuscript(md);
const originalHtml=gate.auditPreview(html);
const originalMatrix=gate.auditSourceMatrix(matrix);
test("Apollo manuscript source guard passes",()=>assert(originalMd.pass,JSON.stringify(originalMd.checks.filter(x=>!x.pass))));
test("Email-safe HTML structural review passes",()=>assert(originalHtml.pass,JSON.stringify(originalHtml.checks.filter(x=>!x.pass))));
test("Evidence and release matrix passes",()=>assert(originalMatrix.pass,JSON.stringify(originalMatrix.checks.filter(x=>!x.pass))));
test("Total individual baseline invariants >= 30",()=>assert(originalMd.checks.length+originalHtml.checks.length+originalMatrix.checks.length>=30));
test("No real sending or release function exists",()=>assert.deepEqual(Object.keys(gate).sort(),["auditManuscript","auditPreview","auditSourceMatrix","nativeDecision"].sort()));
test("Native preview feasible but unapproved and HOLD",()=>{
  const out=gate.nativeDecision({subscriptions:true,site_can_send:true,email_new_posts_by_default:false,email_content_format:"excerpt"},
                                   {post_type:"post",preview_mode:"native_non_sending_editor",founder_final_approval:false,post_publication_authorized:false});
  assert.equal(out.status,"HOLD_UNSENT");assert(out.preview_plausible);assert(out.awaiting_founder_approval);
});
test("Even fictional approval cannot flip hardcoded HOLD",()=>{
  const out=gate.nativeDecision({subscriptions:true,site_can_send:true,email_new_posts_by_default:false,email_content_format:"excerpt"},
                                   {post_type:"post",preview_mode:"native_non_sending_editor",founder_final_approval:true,post_publication_authorized:true});
  assert.equal(out.status,"HOLD_UNSENT");
});
test("Page cannot substitute for post to claim native newsletter",()=>{
  const out=gate.nativeDecision({subscriptions:true,site_can_send:true,email_new_posts_by_default:false,email_content_format:"excerpt"},
                                   {post_type:"page",preview_mode:"native_non_sending_editor"});
  assert.equal(out.status,"HOLD_UNSENT");assert.equal(out.preview_plausible,false);
});
mustFail("Removed Apollo primary CTA",()=>gate.auditManuscript(replaceOne(md,"**Read the evidence →","**See later →")));
mustFail("Removed Apollo crew name",()=>gate.auditManuscript(replaceOne(md,"Roger Chaffee","Crew Member")));
mustFail("False conclusive ignition wording",()=>gate.auditManuscript(replaceOne(md,"the exact ignition point was **not conclusively established**","the exact ignition point was established")));
mustFail("Removed official NASA board source",()=>gate.auditManuscript(replaceOne(md,"https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/","https://example.test/board")));
mustFail("Invented unconditional guarantee",()=>gate.auditManuscript(md+"\nThis was guaranteed."));
mustFail("Inserted merchant destination in editorial manuscript",()=>gate.auditManuscript(md+"\nhttps://zen12.com/hnp"));
mustFail("Missing publisher compliance sentinel",()=>gate.auditManuscript(replaceOne(md,"[[FV_VALID_PHYSICAL_POSTAL_ADDRESS_REQUIRED]]","")));
mustFail("Missing unsubscribe sentinel",()=>gate.auditManuscript(replaceOne(md,"[[REAL_JETPACK_UNSUBSCRIBE_RENDERING_AND_FUNCTION_REQUIRED]]","")));
mustFail("Misleading 14-second certainty in manuscript",()=>gate.auditManuscript(md+"\nExactly fourteen seconds were proved."));
mustFail("Unsafe HTML script injection",()=>gate.auditPreview(html.replace("</body>","<script>console.log('unsafe')</script></body>")));
mustFail("HTML affiliate URL injection",()=>gate.auditPreview(html.replace("</body>","<a href=\"https://zen12.com/hnp\">Buy</a></body>")));
mustFail("HTML second first-party primary CTA",()=>gate.auditPreview(html.replace("</body>","<a href=\"https://finalvestige.com/focus/\">Second CTA</a></body>")));
mustFail("HTML missing NASA source",()=>gate.auditPreview(replaceOne(html,"https://sma.nasa.gov/sma-disciplines/accllp/apollo-1","https://example.test/")));
mustFail("HTML missing legal-address placeholder",()=>gate.auditPreview(replaceOne(html,"[[FV_VALID_PHYSICAL_POSTAL_ADDRESS_REQUIRED]]","")));
mustFail("HTML missing unsubscribe placeholder",()=>gate.auditPreview(replaceOne(html,"[[REAL_JETPACK_UNSUBSCRIBE_RENDERING_AND_FUNCTION_REQUIRED]]","")));
mustFail("HTML remove responsive viewport",()=>gate.auditPreview(replaceOne(html,'name="viewport"','name="none"')));
mustFail("HTML remove no-send warning",()=>gate.auditPreview(replaceOne(html,"DO NOT SEND OR PUBLISH","RELEASE READY")));
const mutated=(mutator)=>{const d=JSON.parse(JSON.stringify(matrix));mutator(d);return gate.auditSourceMatrix(d);};
mustFail("Commercial slot link activated",()=>mutated(d=>d.cta_destination_contract[2].destination="https://zen12.com/hnp"));
mustFail("Hidden claimed revenue",()=>mutated(d=>d.revenue_kpi.net_revenue_per_1000_qualified_sessions=300));
mustFail("Consent falsely attested",()=>mutated(d=>d.release_attestations.native_eligible_recipient_ledger=true));
mustFail("WordPress default sends toggled on",()=>mutated(d=>d.native_wordpress.email_new_posts_by_default=true));
mustFail("False additive subscriber count",()=>mutated(d=>d.native_wordpress.subscriber_totals.nonadditive=false));
mustFail("Uncited historical claim",()=>mutated(d=>d.claims[0].source=null));
mustFail("Editorial/commercial mix altered",()=>mutated(d=>d.campaign.commercial_hold_slots=[3,4,5]));
mustFail("Sender approval falsely asserted",()=>mutated(d=>d.campaign.approved_for_sending=true));
test("No PII or marketing tracking in local review HTML",()=>{
 assert(!/https?:\/\/[^\s"'<>]*[?&]utm_/.test(html));
 assert(!/mailto:|<form\b|<input\b|<iframe\b/i.test(html));
});
test("Full mail body includes NASA summary + one known local CTA",()=>{
 for(const anchor of ["not conclusively established","oxygen atmosphere","vulnerable wiring","90 seconds","escape or rescue","Apollo 204 Review Board"]){
  assert(md.includes(anchor),anchor);assert(html.includes(anchor),anchor);
 }
});
process.stdout.write("RESULT "+passed+"/"+passed+" PASS (source-only; no live WordPress, email, checkout or paid sale)\n");
