/** R434 pure manuscript adoption evaluator. Never authorizes email, WordPress or commerce operations. */
export const PINNED = Object.freeze({
"01":"16812b6cba277fd473a696d47086f4999e726fea",
"02":"590e886c0ab8a4a386de1a23001c9d29a9828f31",
"03":"c84417cf21e64837c44700ef03e488d87c73b7ee",
"04":"2ce980bb255905ec19742a36dbe916408f9ee99d",
"05":"afe690169137cb83586edb4ef8e5e1dbe177a415",
"06":"86113c9a0c482cbef2ad5cf103bc6612dbe78d50"
});
const sha = v => typeof v==="string" && /^[0-9a-f]{40}$/.test(v);
export function inspectCandidateRegistry(data, proof={}) {
  if (!data || !Array.isArray(data.entries) || data.entries.length!==6) throw Error("Exactly six candidate entries required");
  if (data.canonical?.pr!==175 || data.canonical?.head!=="d57ccdba3aee8f065e143e101c2945f4f3d01647") throw Error("Canonical source mismatch");
  if (data.allocation?.editorial!==4 || data.allocation?.commercial!==2) throw Error("Allocation mismatch");
  const ids = new Set();
  let editorials=0,commercial=0;
  const decisions = data.entries.map(e=>{
    if (ids.has(e.id) || !PINNED[e.id]) throw Error("Unknown or duplicate issue ID");
    ids.add(e.id);
    if (!sha(e.blob) || e.blob!==PINNED[e.id] || !sha(e.commit)) throw Error("Unpinned candidate or fake SHA");
    if (typeof e.subject!=="string" || !e.subject.trim() || e.subject.length>95) throw Error("Subject missing or excessive");
    if (typeof e.preheader!=="string" || !e.preheader.trim() || e.preheader.length>155) throw Error("Preheader missing or excessive");
    if (e.adopted!==false || e.actual_received_email_verified!==false || e.founder_final_send_approval!==false) throw Error("Cannot claim adoption, actual mail or final approval");
    const comm=e.kind==="commercial-review-pending";
    if(e.kind!=="editorial" && !comm) throw Error("Unknown slot type");
    if(comm) commercial++; else editorials++;
    if(comm && (e.destination!==null || e.merchant_email_rights_verified!==false || e.merchant_referral_link_verified!==false)) throw Error("Commercial activation without rights");
    if(!comm && (!e.destination || !e.destination.startsWith("https://finalvestige.com/"))) throw Error("Editorial destination must be first-party");
    const ownerSelected=proof.founder_copy_adoption?.[e.id]===e.blob;
    const independentSource=proof.source_verified?.[e.id]===true;
    const destinationVerified=proof.destination_verified?.[e.id]===true;
    const eligible=ownerSelected&&independentSource&&destinationVerified && (!comm || (proof.named_email_rights?.[e.id]===true && proof.merchant_exact_sku?.[e.id]===true && proof.issued_referral?.[e.id]===true && proof.checkout_terms_verified?.[e.id]===true));
    return {id:e.id,slot:e.kind,eligible_for_editorial_review:eligible,send_authorized:false,reason:eligible?"FOUNDER_CANDIDATE_REVIEW_ONLY":"HOLD_EVIDENCE_OR_FOUNDER_CHOICE"};
  });
  if(editorials!==4||commercial!==2) throw Error("Actual kind mix not 4:2");
  if(data.send_state!=="HOLD_UNSENT" || data.adoption_state!=="ALL_UNADOPTED") throw Error("Release flag tampering");
  if(typeof proof==="object" && Object.keys(proof).some(k=>/email_address|subscriber_email|ip_address|raw_url/i.test(k))) throw Error("PII not accepted");
  return {campaign:"HOLD_UNSENT",send_authorized:false,issues:decisions,commercial_slots:commercial,editorial_slots:editorials,unadopted:6};
}
