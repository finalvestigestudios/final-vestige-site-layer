'use strict';
// Read-only QA of the actual six ORIGINAL manuscripts. Never authorizes a send.
function audit(manifest, manuscripts) {
 if(!manifest || !Array.isArray(manifest.issues) || !manuscripts) throw Error('manifest and source texts required');
 const findings=[]; const add=(n,sev,code)=>findings.push({issue:n,severity:sev,code});
 const ids=manifest.issues.map(x=>x.number).join(',');
 if(ids!=='1,2,3,4,5,6') add(0,'ERROR','ISSUE_SET');
 if(manifest.status!=='DRAFT_UNSENT_NO_SCHEDULING') add(0,'ERROR','UNSENT_STATUS');
 if(manifest.issues.filter(x=>x.kind==='editorial').map(x=>x.number).join(',')!=='1,2,4,6' ||
    manifest.issues.filter(x=>x.kind==='commercial-review-pending').map(x=>x.number).join(',')!=='3,5')
   add(0,'ERROR','EDITORIAL_COMMERCIAL_MIX');
 const labels={1:'Open the primary-source trail',2:'Read the file',3:'Read the Zen12 evaluation',4:'Read the investigation',5:'See the forthcoming independent guide',6:'Open the free Fieldbook'};
 for(const i of manifest.issues){
   const s=manuscripts[i.slug], n=i.number;
   if(typeof s!=='string'||!s.trim()){add(n,'ERROR','MISSING_SOURCE');continue;}
   if(!s.includes('STATUS: UNSENT DRAFT')||!s.includes('DO NOT PUBLISH OR EMAIL')) add(n,'ERROR','NO_SEND_GUARD');
   if(!s.includes('**Subject:** '+i.subject)||!s.includes('**Preheader:** '+i.preheader)) add(n,'ERROR','SUBJECT_PREHEADER_DRIFT');
   if(!s.includes('[[VALID_POSTAL_ADDRESS_REQUIRED]]')||!s.includes('[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]')) add(n,'ERROR','FOOTER_GUARD_MISSING');
   if(!s.includes('**'+labels[n]+':**')) add(n,'ERROR','PRIMARY_CTA_MISSING');
   if(!i.editorial_cta||!s.includes(i.editorial_cta)) add(n,'ERROR','CTA_DESTINATION_DRIFT');
   if(i.merchant_affiliate_url!==null) add(n,'ERROR','AFFILIATE_ACTIVATED');
   if(/https?:\/\/(?:www\.)?(zen12\.com|hypnosislive\.com|affiliates\.inspire3\.com)\b/i.test(s)) add(n,'ERROR','MERCHANT_LINK_IN_DRAFT');
   if(n===3||n===5){
      if(!i.editorial_cta.startsWith('[[APPROVED_')||!i.editorial_cta.endsWith('_REQUIRED]]')) add(n,'ERROR','UNAPPROVED_GUIDE_ACTIVATED');
      const a=s.indexOf('**'+labels[n]+':**'), b=s.indexOf('**Commercial disclosure:**',a);
      if(b<a||b-a>500) add(n,'ERROR','COMMERCIAL_DISCLOSURE_NOT_NEAR_CTA');
   }
   // "Editorial" is an allocation label, NOT a legal exemption for marketing email.
   add(n,'HOLD','CAN_SPAM_PRIMARY_PURPOSE_AND_FOOTER_REVIEW');
   add(n,'HOLD','NATIVE_RECEIPT_AND_CONSENT_UNPROVEN');
 }
 if(manifest.issues[0]?.editorial_cta===manifest.issues[1]?.editorial_cta) add(1,'REVIEW','ISSUES_01_02_DUPLICATE_CTA');
 if(manifest.issues[5]?.editorial_cta==='https://finalvestige.com/focus/') add(6,'REVIEW','ISSUE_06_REPEATS_WELCOME_FIELD_BOOK');
 const i4=manifest.issues[3],s4=manuscripts[i4?.slug];
 if(i4&&/fourteen seconds/i.test(i4.subject)&&s4&&!/\b(?:fourteen|14)\b/i.test(s4.split('\n---\n').slice(1).join('\n---\n')))
   add(4,'REVIEW','ISSUE_04_SUBJECT_NUMBER_NOT_EXPLAINED');
 return {status:findings.some(x=>x.severity==='ERROR')?'INVALID_DRAFT_SOURCE':'HOLD_NO_SEND',
   authentic_consent:false,authorized_to_send:false,paid_revenue:'NOT_COMPUTABLE',findings};
}
module.exports={audit};