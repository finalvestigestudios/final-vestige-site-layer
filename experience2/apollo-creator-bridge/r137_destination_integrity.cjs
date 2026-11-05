'use strict';
/**
 * R137 independently checkable URL syntax for the Grok→Apollo→paid-offer proposal.
 * Does NOT visit sites, confirm a post, approve an offer, permit a CTA or attest sales.
 * Closed by default: other storefronts/custom domains need independent documented review.
 */
const YOUTUBE_ID=/^[A-Za-z0-9_-]{11}$/;
const PAYHIP_PRODUCT=/^\/b\/[A-Za-z0-9_-]{4,40}$/;
function exactHttps(raw){
 if(typeof raw!=='string'||raw!==raw.trim()||/\s|[\\<>"']/.test(raw))return null;
 try{
  const u=new URL(raw);
  if(u.protocol!=='https:'||u.username||u.password||u.port||u.hash||
     !u.hostname||u.hostname.endsWith('.')||u.origin==='null')return null;
  // Reject URL parser repairs, encoded hostname tricks, and normalization surprises.
  if(raw!==u.href||/%2f|%5c|%00/i.test(raw))return null;
  return u;
 }catch(_){return null;}
}
function inspectCreatorUrl(raw){
 const u=exactHttps(raw);
 if(!u)return {status:'INVALID',reason:'MALFORMED_OR_NONCANONICAL_HTTPS'};
 const host=u.hostname.toLowerCase();
 let id=null,kind=null;
 if(host==='youtube.com'||host==='www.youtube.com'){
  if(u.pathname==='/watch'&&u.searchParams.size===1&&u.searchParams.has('v')){
   id=u.searchParams.get('v');kind='LONG_FORM';
  }else if(/^\/shorts\/[A-Za-z0-9_-]{11}$/.test(u.pathname)&&!u.search){
   id=u.pathname.slice(8);kind='SHORT';
  }
 }else if(host==='youtu.be'&&!u.search&&/^\/[A-Za-z0-9_-]{11}$/.test(u.pathname)){
  id=u.pathname.slice(1);kind='YOUTUBE_SHORTLINK_UNTYPED';
 }
 if(!YOUTUBE_ID.test(id||''))return {status:'INVALID',reason:'UNSUPPORTED_YOUTUBE_ASSET_ROUTE'};
 return {status:'SYNTAX_ONLY_NOT_PUBLICATION_PROOF',platform:'youtube',kind,video_id:id,
  canonical_url:u.href,independently_published:false};
}
function inspectMerchantUrl(raw){
 const u=exactHttps(raw);
 if(!u)return {status:'INVALID',reason:'MALFORMED_OR_NONCANONICAL_HTTPS'};
 if(!['payhip.com','www.payhip.com'].includes(u.hostname.toLowerCase())||
    !PAYHIP_PRODUCT.test(u.pathname)||u.search)
  return {status:'INVALID',reason:'UNREVIEWED_MERCHANT_OR_PRODUCT_ROUTE'};
 return {status:'DOCUMENT_ONLY_NOT_MERCHANT_PROOF',product_url:u.href,
  verified_product:false,verified_delivery:false,founder_approved:false};
}
function inspectReferralDestination(raw,assetId){
 const u=exactHttps(raw);
 if(!u)return {status:'INVALID',reason:'MALFORMED_OR_NONCANONICAL_HTTPS'};
 if(u.hostname!=='finalvestige.com'||u.pathname==='/'||u.pathname.startsWith('//')||u.hash||
    !/^[a-z0-9_-]{6,80}$/.test(assetId||''))
  return {status:'INVALID',reason:'DESTINATION_OR_ASSET_NOT_CUSTODIED'};
 const keys=[...u.searchParams.keys()].sort();
 if(keys.join(',')!=='utm_campaign,utm_content,utm_medium,utm_source'||
    u.searchParams.get('utm_source')!=='youtube'||
    u.searchParams.get('utm_medium')!=='organic_social'||
    u.searchParams.get('utm_campaign')!=='history_pilot_2026_11'||
    u.searchParams.get('utm_content')!==assetId||
    !/^[a-z0-9/_-]+\/$/.test(u.pathname)||u.pathname.includes('//'))
  return {status:'INVALID',reason:'NONCANONICAL_OR_UNVERIFIED_CAMPAIGN_DESTINATION'};
 return {status:'CANDIDATE_ONLY_NOT_CLICK_ATTRIBUTION',landing_url:u.href,
  qualified_sessions:'UNOBSERVABLE',confirmed_orders:'UNOBSERVABLE'};
}
module.exports={exactHttps,inspectCreatorUrl,inspectMerchantUrl,inspectReferralDestination};
