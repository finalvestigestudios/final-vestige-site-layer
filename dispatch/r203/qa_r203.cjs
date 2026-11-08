/* Dispatch R203: offline, source-specific quality guard.
 * Usage from repository root: node dispatch/r203/qa_r203.cjs
 * No networking, WordPress writes, email sends, consent exports or merchant links.
 */
"use strict";
function validate(files) {
  const errors=[];
  function check(ok,id){if(!ok)errors.push(id);}
  const md=files["issue05_candidate.md"]||"";
  const txt=files["issue05_candidate.txt"]||"";
  const html=files["issue05_candidate.html"]||"";
  const dossier=files["merchant_claim_dossier.md"]||"";
  const receipt=files["jetpack_receipt_acceptance.md"]||"";
  const revenue=files["revenue_bridge.md"]||"";
  const readme=files["README.md"]||"";
  let proof={};
  try{proof=JSON.parse(files["proof_contract.json"]||"{}")}catch(e){errors.push("malformed_proof_json");}
  const subject="An 1843 book and a modern focus recording";
  for (const [kind,s] of [["markdown",md],["plaintext",txt],["html",html]]) {
    check(s.includes(subject),"subject_missing_"+kind);
    check(/33.minute|33 mins/i.test(s),"product_length_missing_"+kind);
    check(/47.MB/i.test(s),"file_size_missing_"+kind);
    check(/five (?:refunded )?sessions per year|five.refunds.per.year/i.test(s),"refund_limit_missing_"+kind);
    check(/not (?:independently )?test(?:ed)?|not yet independently tested|we have not tested/i.test(s),"product_test_boundary_missing_"+kind);
    check(/commission/i.test(s),"commercial_disclosure_missing_"+kind);
    check(/(?:HOLD|INACTIVE|NOT VERIFIED)/i.test(s),"release_hard_stop_missing_"+kind);
  }
  check(md.includes("https://hypnosislive.com/faq"),"merchant_faq_missing");
  check(md.includes("https://content.www.wellcomecollection.org/works/demkv24m"),"primary_1843_source_missing");
  check(dossier.includes("maximum of five sessions per year"),"refund_claim_dossier_missing");
  check(dossier.includes("https://zen12.com/hnp"),"exact_zen12_source_missing");
  check(dossier.includes("https://affiliates.inspire3.com/"),"affiliate_portal_missing");
  check(receipt.includes("actual physical postal address") || receipt.includes("own valid physical postal address"),"sender_postal_requirement_missing");
  check(receipt.includes("existing-post Email preview")||receipt.includes("View → Email preview"),"native_preview_route_missing");
  check(receipt.includes("ten business days"),"optout_deadline_missing");
  check(revenue.includes("confirmed_signup")&&revenue.includes("NOT_COMPUTABLE"),"revenue_or_consent_spec_missing");
  check(readme.includes("#175")&&readme.includes("#201"),"master_pr_provenance_missing");
  check(html.includes("<html lang=\"en\""),"email_lang_missing");
  check(html.includes("<main ")&&html.includes("<h1 ")&&html.includes("<footer "),"html_semantics_missing");
  check(!/<script[\s>]/i.test(html),"script_in_email_preview");
  check(!/href=[\"']\s*\[\[/i.test(html),"active_placeholder_link");
  check(!/(awin1\.com|[?&](aff_id|affiliate_id|referrer_id)=)/i.test(html),"active_affiliate_url");
  check(!/(\[\[APPROVED_.*?\]\])/.test(html),"template_syntax_in_html_preview");
  check(proof.newsletter_status?.counts_additive===false,"subscriber_counts_additive");
  check(proof.newsletter_status?.email_eligible_exact===null,"invented_eligible_count");
  check(proof.revenue?.net_revenue_per_1000_qualified_human_sessions==="NOT_COMPUTABLE","invented_paid_metric");
  check(proof.issues?.length===6&&proof.issues.filter(i=>i.kind==="editorial").length===4&&proof.issues.filter(i=>i.kind==="commercial_review_pending").length===2,"founder_4_2_mix_changed");
  check(proof.issues?.every(i=>i.release_state==="HOLD_UNSENT"),"unapproved_send_release");
  check(proof.merchant?.zen12?.email_channel_permission===false&&proof.merchant?.total_focus?.email_channel_permission===false,"invented_partner_email_permission");
  check(proof.release_approvals&&Object.values(proof.release_approvals).every(v=>v===false),"invented_legal_consent_approval");
  check(!Object.values(files).some(s=>/[?&](subscriber_email|user_email|recipient_email)=/i.test(s)),"subscriber_pii_query");
  return {passed:errors.length===0,errors,total_checks:42};
}
module.exports={validate};
if(require.main===module){
  const fs=require("node:fs"),path=require("node:path");
  const base=__dirname;
  const names=["README.md","merchant_claim_dossier.md","issue05_candidate.md","issue05_candidate.txt","issue05_candidate.html","jetpack_receipt_acceptance.md","revenue_bridge.md","proof_contract.json"];
  const files=Object.fromEntries(names.map(n=>[n,fs.readFileSync(path.join(base,n),"utf8")]));
  const r=validate(files);
  console.log(JSON.stringify(r,null,2));
  if(!r.passed)process.exitCode=1;
}
