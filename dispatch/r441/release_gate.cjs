'use strict';
/** Hard HOLD evaluator. This package has no send/publish capability. */
const canonical=Object.freeze({issue:3,offer:'Zen12',issue05:'Hypnosis Live',guide:'[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]'});
function evaluate(x={}){const blockers=[];if(x.issue!==3||x.offer!=='Zen12'||x.issue05!=='Hypnosis Live')blockers.push('OFFER_DRIFT');
if(x.guide!==canonical.guide||x.affiliate_url)blockers.push('CTA_NOT_APPROVED');
for(const k of ['email_partner_permission','live_approved_guide','exact_sku_checkout','publisher_postal','rendered_unsubscribe','jetpack_native_preview','received_welcome','founder_final_release'])if(x[k]!==true||!x[k+'_proof'])blockers.push(k.toUpperCase());
if(x.provider_subscribed!==3||x.provider_source!=='WordPress Subscribers')blockers.push('ELIGIBILITY_EVIDENCE');
if(x.send===true||x.publish===true)blockers.push('FORBIDDEN_ACTION');
return {status:'HOLD_UNSENT',ready_to_send:false,blockers};}
module.exports={evaluate,canonical};
