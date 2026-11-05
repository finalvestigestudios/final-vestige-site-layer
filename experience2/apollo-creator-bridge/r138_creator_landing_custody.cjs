'use strict';
/**
 * R138: bind a proposed Grok video to one explicitly reviewed first-party
 * landing route. Syntax/preflight only; not publication, human traffic, consent,
 * checkout, sale, merchant ownership or founder-release evidence.
 *
 * The reviewed landing URL MUST be supplied separately from the campaign.
 * Do not default to an invented WordPress permalink or to the campaign's claim.
 */
const {exactHttps,inspectCreatorUrl,inspectReferralDestination}=
 require('./r137_destination_integrity.cjs');
const STATUS='BOUND_CANDIDATE_NOT_PUBLICATION_OR_VISIT_PROOF';
function reviewedRoute(raw){
 const u=exactHttps(raw);
 if(!u||u.hostname!=='finalvestige.com'||u.search||u.hash||
    u.pathname==='/'||u.pathname.includes('//')||
    !/^\/[a-z0-9/_-]+\/$/.test(u.pathname))return null;
 return u.href;
}
function inspectBoundCampaign(c, independentlyReviewedLandingUrl){
 const errors=[];
 if(!c||typeof c!=='object'||Array.isArray(c))
  return {status:'INVALID',errors:['CAMPAIGN_NOT_OBJECT'],independently_verified:false};
 const source=inspectCreatorUrl(c.public_url);
 if(source.status!=='SYNTAX_ONLY_NOT_PUBLICATION_PROOF')
  errors.push('PUBLIC_VIDEO_URL_UNSUPPORTED');
 if(typeof c.youtube_video_id!=='string'||c.youtube_video_id!==source.video_id)
  errors.push('VIDEO_ID_NOT_BOUND_TO_PUBLIC_URL');
 const expected=reviewedRoute(independentlyReviewedLandingUrl);
 if(!expected)errors.push('REVIEWED_APOLLO_WORDPRESS_ROUTE_NOT_SUPPLIED');
 const candidate=inspectReferralDestination(c.destination_url,c.asset_id);
 if(candidate.status!=='CANDIDATE_ONLY_NOT_CLICK_ATTRIBUTION')
  errors.push('GROK_UTM_DESTINATION_INVALID');
 if(expected&&candidate.status==='CANDIDATE_ONLY_NOT_CLICK_ATTRIBUTION'){
  // No implicit redirects, alternate pages, or query/fragment destinations.
  // Only the path approved outside this untrusted campaign object may pass.
  const dest=new URL(candidate.landing_url);
  if(dest.origin+dest.pathname!==expected)
   errors.push('DESTINATION_DIFFERS_FROM_REVIEWED_APOLLO_ROUTE');
 }
 return {status:errors.length?'INVALID':STATUS,errors,
  independently_verified:false,publication_confirmed:false,
  human_sessions_observed:false,paid_orders_observed:false,
  reviewed_landing_supplied:!!expected};
}
module.exports={inspectBoundCampaign,reviewedRoute,STATUS};
