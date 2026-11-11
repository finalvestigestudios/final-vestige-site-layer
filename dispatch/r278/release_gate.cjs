'use strict';
/**
 * R278 read-only release-risk evaluator. It is NOT a certificate or a sender.
 * Never treats caller-supplied flags/URLs as authentic evidence.
 * No network calls, secrets, PII, browser writes or emails.
 */
const requiredGlobal = [
 'founder_final_campaign_send_approval',
 'eligible_recipients_reconciled_from_provider',
 'received_welcome_and_fieldbook_verified',
 'valid_fv_physical_postal_address_in_actual_email_verified',
 'rendered_functional_unsubscribe_verified',
 'native_jetpack_email_render_verified',
 'all_ctas_verified_live'
];
const requiredMerchant = [
 'affiliate_approval_verified','email_promotion_permission_verified',
 'exact_earning_link_verified','live_vetted_fv_guide_verified',
 'current_checkout_and_refund_verified'
];
function evaluateLedger(data) {
 if (!data || typeof data !== 'object' || Array.isArray(data)) throw Error('snapshot object required');
 const errors=[];
 const wp=data.read_only_wordpress, campaign=data.editorial_campaign, gate=data.gate, commerce=data.commercial;
 if (!wp || !campaign || !gate || !commerce) throw Error('missing required top-level evidence sections');
 if (!Number.isInteger(campaign.issue_count) || campaign.issue_count!==6) errors.push('six-issue baseline changed');
 if (JSON.stringify(campaign.editorial)!=='[1,2,4,6]' || JSON.stringify(campaign.commercial)!=='[3,5]') errors.push('4:2 issue ownership changed');
 if (wp.email_new_posts_by_default!==false) errors.push('default automatic sends not off');
 if (wp.newsletter_enabled!==true) errors.push('newsletter configuration unexpected');
 if (wp.email_format!=='full') errors.push('current email format drift');
 const c=wp.counts;
 if (!c || c.actual_eligible_recipients!==null) errors.push('provider-eligible recipient claim requires fresh evidence');
 if (c && (c.diagnostic_confirmed > c.diagnostic_total || c.diagnostic_confirmed<0)) errors.push('diagnostic totals inconsistent');
 if (!campaign.all_issues_hold || data.state!=='ALL_HOLD_UNSENT') errors.push('campaign HOLD state missing');
 for (const f of requiredGlobal) if(gate[f]!==false) errors.push('unattested global proof: '+f);
 for (const key of ['03','05']) {
   const offer=commerce[key];
   if (!offer || offer.activated_link!==null) {errors.push('activated/absent merchant link: '+key);continue;}
   for(const f of requiredMerchant) if(offer[f]!==false) errors.push('unattested merchant proof: '+key+':'+f);
 }
 const m=data.metrics;
 for (const f of ['attributable_paid_orders','gross_revenue','refunds','fees','net_realized_revenue','net_per_1000_qualified_human_sessions'])
   if(!m || m[f]!==null) errors.push('unverified financial/denominator metric: '+f);
 // An apparently clean snapshot is still a HOLD: this tool has no authenticated evidence pipeline.
 return {status:errors.length?'INVALID_SOURCE_SNAPSHOT':'HOLD_NO_SEND',errors,
 issue_states:Object.fromEntries([1,2,3,4,5,6].map(i=>[i,i===3||i===5?'HOLD_MERCHANT_AND_SEND':'HOLD_SEND'])),
 proof_is_provider_authenticated:false,founder_permission_to_send:false,
 reported_paid_revenue:'NOT_COMPUTABLE'};
}
module.exports={evaluateLedger,requiredGlobal,requiredMerchant};
