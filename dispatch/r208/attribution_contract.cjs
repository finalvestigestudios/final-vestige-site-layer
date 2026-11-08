'use strict';
/**
 * Dispatch R208: OFFLINE source-only attribution and consent QA.
 * NOT production analytics. No network, WordPress writes, cookies, or sends.
 */
const MEDIA = new Set(['tiktok','youtube','instagram','facebook','linkedin','bluesky','x','snapchat']);
const PARAMS = new Set(['utm_source','utm_medium','utm_campaign','utm_content','asset_id']);
const TYPES = Object.freeze({'01':'editorial','02':'editorial','03':'commercial','04':'editorial','05':'commercial','06':'editorial'});
const TOKEN = /^[A-Za-z0-9][A-Za-z0-9_-]{2,99}$/;
function parseCreatorLanding(raw, registry) {
  if(typeof raw!=='string' || !registry || typeof registry!=='object') throw Error('unverifiable landing');
  let url; try {url=new URL(raw);} catch {throw Error('invalid URL');}
  if(url.protocol!=='https:'||url.hostname!=='finalvestige.com'||url.username||url.password||url.port||url.hash) throw Error('invalid first-party destination');
  const keys=[...url.searchParams.keys()];
  if(keys.some(k=>!PARAMS.has(k))||new Set(keys).size!==keys.length) throw Error('unknown or duplicate query parameter');
  const p=Object.fromEntries(url.searchParams.entries());
  if(p.utm_medium!=='social'||!MEDIA.has(p.utm_source)||!TOKEN.test(p.asset_id||'')||!TOKEN.test(p.utm_campaign||'')) throw Error('asset/source/campaign not verified');
  if(p.utm_content && !TOKEN.test(p.utm_content)) throw Error('unsafe content parameter');
  const ref=registry[p.asset_id];
  if(!ref||ref.reviewed!==true||ref.source!==p.utm_source||ref.campaign!==p.utm_campaign||ref.pathname!==url.pathname||typeof ref.post_url!=='string'||!ref.post_url.startsWith('https://')) throw Error('creator asset absent from independently reviewed registry');
  return Object.freeze({status:'VERIFIABLE_SOURCE_ROUTE_ONLY',source:p.utm_source,asset_id:p.asset_id,campaign:p.utm_campaign,pathname:url.pathname,paid_order:false});
}
function countConfirmedProviderEvents(events) {
  if(!Array.isArray(events)) throw Error('provider records required');
  const seen=new Set(); let pending=0, excluded=0;
  for(const e of events){
    if(!e||typeof e!=='object'||['email','recipient','phone','name','ip','raw_token'].some(k=>Object.prototype.hasOwnProperty.call(e,k))) throw Error('PII or invalid record in reviewer');
    if(e.provider_source!=='jetpack_subscription_state'||e.explicit_newsletter_consent!==true||e.subscription_state!=='subscribed'){
      if(e.subscription_state==='pending') pending++; else excluded++;
      continue;
    }
    if(typeof e.opaque_provider_id!=='string'||!TOKEN.test(e.opaque_provider_id)||!/^\d{4}-\d{2}-\d{2}T/.test(e.confirmed_at||'')) throw Error('claimed subscription lacks provider evidence');
    seen.add(e.opaque_provider_id);
  }
  return Object.freeze({confirmed_unique:seen.size,pending_excluded:pending,other_excluded:excluded,provider_count_only:true,does_not_prove_welcome_delivery:true});
}
function classifyCTA(issue, raw, evidence={}){
  if(!TYPES[issue]) throw Error('unknown canonical issue');
  let u;try{u=new URL(raw);}catch{return Object.freeze({issue,status:'HOLD_DESTINATION',authorized_send:false});}
  if(u.protocol!=='https:'||u.hostname!=='finalvestige.com'||u.searchParams.has('email')) return Object.freeze({issue,status:'HOLD_DESTINATION',authorized_send:false});
  if(evidence.already_subscribed===true&&u.pathname==='/focus/') return Object.freeze({issue,status:'HOLD_REDUNDANT_SIGNUP_CTA',authorized_send:false});
  if(evidence.cms_published!==true) return Object.freeze({issue,status:'HOLD_CMS_PUBLISH_PROOF',authorized_send:false});
  if(TYPES[issue]==='commercial'&&!(evidence.partner_named_email_permission===true&&evidence.issued_link_verified===true&&evidence.guide_approved===true&&evidence.guide_disclosure_adjacent===true)) return Object.freeze({issue,status:'HOLD_MERCHANT',authorized_send:false});
  return Object.freeze({issue,status:'COPY_REVIEW_ONLY',authorized_send:false});
}
module.exports={parseCreatorLanding,countConfirmedProviderEvents,classifyCTA,TYPES};
