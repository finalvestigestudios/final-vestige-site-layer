"use strict";
/* Source identity audit, deliberately NOT a sending program.
   Call auditSourceBinding only on immutable source records. */
const PINNED_MASTER="d57ccdba3aee8f065e143e101c2945f4f3d01647";
const FIELDS=["source_sha","subject","preheader","cta","kind"];
function auditSourceBinding(record,options={}){
 const problems=[],differences=[],counts={source_sha:0,subject:0,preheader:0,cta:0,kind:0};
 if(!record||typeof record!=="object")return {ready_to_send:false,source_bound:false,state:"HOLD_BAD_INPUT",problems:["record absent"],differences:[],counts};
 if(record.master?.commit!==PINNED_MASTER||record.master?.pr!==175)problems.push("master commit or PR not pinned");
 if(!Array.isArray(record.canonical)||record.canonical.length!==6)problems.push("canonical must have exactly six editions");
 if(!Array.isArray(record.downstream_r235)||record.downstream_r235.length!==6)problems.push("downstream must have exactly six editions");
 const canonical=record.canonical||[],downstream=record.downstream_r235||[];
 const ids=(rows)=>rows.map(x=>x.number);
 if(new Set(ids(canonical)).size!==6||new Set(ids(downstream)).size!==6)problems.push("duplicate edition IDs");
 if(ids(canonical).join(",")!=="1,2,3,4,5,6"||ids(downstream).join(",")!=="1,2,3,4,5,6")problems.push("edition order invalid");
 if(canonical.filter(x=>x.kind==="editorial").length!==4||canonical.filter(x=>x.kind==="commercial-review-pending").length!==2)problems.push("4:2 campaign allocation changed");
 for(const a of canonical){
   if(!/^[a-f0-9]{40}$/.test(a.source_sha||""))problems.push("canonical source hash invalid");
   const b=downstream.find(x=>x.number===a.number);
   if(!b){problems.push("downstream edition missing: "+a.number);continue;}
   for(const field of FIELDS)if(a[field]!==b[field]){counts[field]++; differences.push({issue:a.number,field,canonical:a[field],downstream:b[field]});}
 }
 if(record.authorization?.founder_final||record.authorization?.merchant_named_acceptance||record.authorization?.merchant_email_rights||record.authorization?.source_alternatives_adopted)problems.push("approval assertion in evidence-only ledger; requires external signed source");
 if(record.wordpress_readonly?.eligible_recipients!==null||record.wordpress_readonly?.received_welcome!==null)problems.push("unverified recipient or welcome asserted");
 if(record.wordpress_readonly?.auto_send_new_posts!==false)problems.push("site autosend no longer confirmed off");
 if(record.downstream_r235?.some(x=>("merchant_affiliate_url" in x&&x.merchant_affiliate_url)||x.send_authorized===true||x.real_sent===true))problems.push("unexpected live link or sending assertion");
 if(options.expect_diff===true&&differences.length===0)problems.push("expected source drift disappeared; human reconciliation needed");
 return {ready_to_send:false,source_bound:problems.length===0&&differences.length===0,
   state:problems.length?"HOLD_EVIDENCE_INTEGRITY":differences.length?"HOLD_SOURCE_DRIFT":"HOLD_RELEASE_GATES",
   problems,differences,counts,release_gate:"FOUNDER_AND_COMPLIANCE_APPROVAL_REQUIRED",
   note:"Source equality is not legal, merchant, consent or deliverability approval."};
}
module.exports={auditSourceBinding,PINNED_MASTER};
