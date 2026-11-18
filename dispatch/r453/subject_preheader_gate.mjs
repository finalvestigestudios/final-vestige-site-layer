/** Dispatch R453: non-sending envelope manifest audit.
 * Never treat normalized output as founder-selected or validated by actual Jetpack render.
 */
export function lintEnvelopeField(value,type) {
  const issues=[];
  if(typeof value!=="string"||!value.trim())return ["missing_"+type];
  if(/[\r\n]/.test(value))issues.push("header_injection_newline");
  if(/^\s*(\*\*|__|#{1,6}\s|>\s)/.test(value)||/\*\*|__/.test(value))issues.push("markdown_contamination");
  if(/<[^>]+>/.test(value))issues.push("html_contamination");
  if(/(?:guaranteed|miracle cure|proven to work|100% effective)/i.test(value))issues.push("unsupported_outcome_language");
  if(value.length>(type==="subject"?78:145))issues.push("length_advisory");
  return issues;
}

export function lintManifestEnvelopes(manifest){
  if(!manifest||!Array.isArray(manifest.issues)||manifest.issues.length!==6)return {status:"FAIL",errors:["six_issues_required"]};
  const result=[];for(const issue of manifest.issues){
    for(const variant of ["original","alternative"]){
      const e=issue[variant],a=lintEnvelopeField(e?.subject,"subject"),b=lintEnvelopeField(e?.preheader,"preheader");
      result.push({issue:issue.number,variant,problems:[...a.map(x=>"subject:"+x),...b.map(x=>"preheader:"+x)]});
    }
  }
  return {status:result.some(x=>x.problems.length)?"REVIEW_REQUIRED":"PASS_STATIC_ONLY",total_subject_preheader_pairs:result.length,flagged_pairs:result.filter(x=>x.problems.length).length,results:result};
}
