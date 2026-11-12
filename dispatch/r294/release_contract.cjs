"use strict";
/** FV R294 offline-only review helpers. NEVER wire into a sender or public analytics. */
function copyParity({dispatch, focus}) {
  const norm=x=>String(x||"").replace(/\s+/g," ").toLowerCase();
  const expects=x=>/recommendations?.{0,110}(earn|commission)|commission.{0,110}recommendations?/.test(norm(x));
  const e={dispatchDisclosure:expects(dispatch),focusDisclosure:expects(focus)};
  return {...e,parity:e.dispatchDisclosure&&e.focusDisclosure?"PASS_COPY_ONLY":"HOLD_COPY_REVIEW",
          providerConsentVerified:false};
}
function signupCandidate(x) {
  if(!x||x.provider!=="jetpack_authenticated"||x.lifecycle!=="confirmed"||
     x.active!==true||x.suppressed!==false||x.doubleOptIn!==true||
     x.sameJetpackList!==true||x.providerDedupeAttested!==true)
      return "UNKNOWN_NOT_A_LEAD";
  return "VERIFIABLE_PROVIDER_CANDIDATE_ONLY";
}
function issueGate(issue, proof) {
  const problems=[],commercial=[3,5].includes(issue?.number);
  const editorial=[1,2,4,6].includes(issue?.number);
  if(!commercial&&!editorial)return {state:"HOLD_UNSENT",sendAuthorized:false,problems:["invalid_issue"]};
  if(commercial!==Boolean(issue?.commercial))problems.push("mix");
  if(!issue.subject||!issue.preheader)problems.push("subject_preheader");
  if(!issue.cta || !/^https:\/\/finalvestige\.com\//.test(issue.cta))
    problems.push("unverified_guide");
  if(commercial){
    for(const field of ["affiliatePublisherAccepted","affiliateEmailPermission","earningLinkApproved","buyerGuideLive","currentTermsVerified","adjacentDisclosure"]){
      if(proof?.[field]!==true)problems.push(field);
    }
  }
  for(const field of ["eligibleAudienceVerified","realNativeJetpackPreview","receivedUnsubscribeVerified","fvPostalVerified","preheaderActuallyRendered","founderFinalCampaignApproval"]) {
    if(proof?.[field]!==true)problems.push(field);
  }
  return {state:"HOLD_UNSENT",sendAuthorized:false,problems,kind:commercial?"commercial":"editorial"};
}
function settledNet(order){
  if(!order || order.sourceConfirmed!==true || order.status!=="settled" ||
      order.verifiedRefunds!==true || order.verifiedFees!==true ||
      !Number.isFinite(order.gross) || !Number.isFinite(order.refunds) ||
      !Number.isFinite(order.fees) || order.gross<0 || order.refunds<0 ||
      order.fees<0 || order.refunds+order.fees>order.gross) return null;
  return +(order.gross-order.refunds-order.fees).toFixed(2);
}
function netPerThousand(sessions,orders){
  if(!Number.isInteger(sessions)||sessions<=0||!Array.isArray(orders)||
     orders.some(o=>settledNet(o)===null))return {status:"NOT_COMPUTABLE"};
  const net=+orders.reduce((s,o)=>s+settledNet(o),0).toFixed(2);
  return {status:"SYNTHETIC_ONLY",net,per1000:+(net*1000/sessions).toFixed(2)};
}
module.exports={copyParity,signupCandidate,issueGate,settledNet,netPerThousand};
