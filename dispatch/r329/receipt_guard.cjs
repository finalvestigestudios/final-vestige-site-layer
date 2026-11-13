'use strict';
// Offline read-only inspector for an *authorized, private* received-message MIME specimen.
// Deliberately never outputs raw headers, addresses, identifiers, URLs, body or recipient PII.
// It is NOT a sender, subscriber importer, unsubscribe tester, or release authorization.
function headerMap(mime) {
  if (typeof mime !== 'string' || mime.length > 2_000_000 || !mime.includes('\n')) return {};
  const head=mime.split(/\r?\n\r?\n/,1)[0].replace(/\r?\n[ \t]+/g,' ');
  const headers={};
  for (const line of head.split(/\r?\n/)) {
    const i=line.indexOf(':');
    if(i>0){const k=line.slice(0,i).toLowerCase().trim();(headers[k]??=[]).push(line.slice(i+1).trim());}
  }
  return headers;
}
function inspectReceived(mime, evidence={}) {
  const h=headerMap(mime);
  const head=(k)=>(h[k]||[]).join(' ');
  const subj=head('subject');
  const unsub=head('list-unsubscribe');
  const post=head('list-unsubscribe-post');
  const body=typeof mime==='string' ? mime.split(/\r?\n\r?\n/).slice(1).join('\n\n') : '';
  const hasValidUnsubHeader=/<https:\/\/[^> \t\r\n]+>/i.test(unsub) || /<mailto:[^> \t\r\n]+>/i.test(unsub);
  const hasOneClick=/\bList-Unsubscribe=One-Click\b/i.test(post)&&/<https:\/\/[^> \t\r\n]+>/i.test(unsub);
  const containsPlaceholders=/\[\[(?:APPROVED_|VALID_POSTAL_|JETPACK_|[^]\n]{1,90}REQUIRED)[^\]\n]*\]\]/i.test(mime||'');
  const hasBodyUnsubscribe=/unsubscribe/i.test(body) && /https?:\/\//i.test(body);
  const senderDisplay=/\bFinal Vestige(?: Studios)?\b/i.test(head('from'));
  const matchingSubject=typeof evidence.expectedSubject==='string' && subj===evidence.expectedSubject;
  const checks={
    inputIsOriginalInboxMime:evidence.originalInboxWitnessed===true,
    senderDisplayMatched:senderDisplay,
    originalSubjectMatches:matchingSubject,
    providerUnsubscribeHeaderFound:hasValidUnsubHeader,
    providerOneClickHeadersFound:hasOneClick,
    renderedBodyMentionsUnsubscribe:hasBodyUnsubscribe,
    publisherAddressIndependentlyValidated:evidence.publisherPostalAddressVerified===true,
    visiblePostalFooterIndependentlyWitnessed:evidence.postalFooterRenderedVerified===true,
    unsubscribeActionIndependentlyTested:evidence.unsubFunctionVerified===true,
    welcomeAndFieldbookDeliveryIndependentlyWitnessed:evidence.welcomeAndFieldbookVerified===true,
    subscriberProviderConsentIndependentlyVerified:evidence.providerConsentVerified===true,
    noBlockingPlaceholders:!containsPlaceholders
  };
  // A raw MIME string cannot establish valid postal ownership, live link functionality,
  // consent, actual receipt of the welcome PDF, or the founder's final send authorization.
  const nextAction=Object.entries(checks).filter(([,v])=>!v).map(([k])=>k);
  return Object.freeze({status:'HOLD_UNSENT',reviewEvidenceComplete:nextAction.length===0,
    missingEvidence:nextAction,checks:Object.freeze(checks),
    consentCount:'NOT_DERIVED',paidSales:'NOT_DERIVED',realizedNetRevenue:'NOT_DERIVED'});
}
module.exports={headerMap,inspectReceived};
