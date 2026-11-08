'use strict';
// Dispatch R210: deterministic source-only audit. Never send, post, access mail or infer subscriber consent.
const auditCanonical=function auditCanonical(manifest, texts) {
  const kinds={1:'editorial',2:'editorial',3:'commercial-review-pending',4:'editorial',5:'commercial-review-pending',6:'editorial'};
  if (!manifest || !Array.isArray(manifest.issues)||manifest.issues.length!==6||new Set(manifest.issues.map(x=>x.number)).size!==6) throw Error('six unique canonical issues required');
  const output=[];
  for(const i of manifest.issues){
    if(!Object.hasOwn(kinds,i.number)||kinds[i.number]!==i.kind)throw Error('4:2 editorial/offer allocation changed');
    const text=texts[i.number];if(typeof text!=='string'||text.length<300)throw Error('manuscript missing or incomplete');
    const subject=(text.match(/^\*\*Subject:\*\* (.+)$/m)||[])[1], preheader=(text.match(/^\*\*Preheader:\*\* (.+)$/m)||[])[1];
    if(i.subject!==subject||i.preheader!==preheader)throw Error('manifest subject/preheader inconsistent with canonical manuscript');
    const findings=[];
    if(!text.includes('UNSENT DRAFT'))findings.push('MISSING_UNSENT_NOTICE');
    if(!text.includes('[[VALID_POSTAL_ADDRESS_REQUIRED]]')||!text.includes('[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]'))findings.push('LEGAL_PLACEHOLDER_OR_PROOF_MISSING');
    if(i.kind==='commercial-review-pending'){
      if(!i.editorial_cta.startsWith('[[')||!text.includes('Commercial disclosure:'))findings.push('MERCHANT_PLACEHOLDER_OR_DISLCOSURE_MISSING');
      findings.push('MERCHANT_EMAIL_RIGHTS_GUIDE_AND_LINK_UNVERIFIED');
      const body=text.split('**Pre-send compliance block')[0];
      if(body.includes('](https://finalvestige.com/'))findings.push('SECONDARY_ACTIVE_LINK_COMPETES_WITH_HELD_GUIDE');
    } else if(!/^https:\/\/finalvestige\.com\/[^?#]*$/.test(i.editorial_cta))findings.push('EDITORIAL_CTA_NOT_SAFE_FIRST_PARTY');
    if(i.number===4&&subject.startsWith('Fourteen seconds')&&!/first indication.{0,120}rupture/i.test(text))findings.push('APOLLO_14_SECONDS_NO_EXPLANATION_IN_EMAIL');
    if(i.number===5&&!text.includes('Total Focus'))findings.push('TOTAL_FOCUS_OFFER_NOT_NAMED');
    if(i.number===6&&i.editorial_cta==='https://finalvestige.com/focus/')findings.push('EXISTING_SUBSCRIBERS_REENTER_SIGNUP');
    output.push({issue:i.number,kind:i.kind,subject,preheader,findings});
  }
  if(manifest.issues[0].editorial_cta===manifest.issues[1].editorial_cta){output[0].findings.push('DUPLICATE_DESTINATION_WITH_ISSUE_02');output[1].findings.push('DUPLICATE_DESTINATION_WITH_ISSUE_01');}
  return {canonical_issue_count:6,editorial:4,prospective_commercial:2,status:'HOLD_UNSENT',commercial_hold:'HOLD_MERCHANT',send_authorized:false,issues:output};
};
module.exports={auditCanonical};
