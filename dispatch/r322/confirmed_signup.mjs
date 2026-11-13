/** Non-sending reference classifier for provider-authenticated, NEW site signups.
 * Trust labels are NOT authentication: Claude must verify evidence at ingress.
 * No I/O, browser state, email address, consent mutation, or mail capability. */
const REF=/^[A-Za-z0-9:_-]{3,96}$/;
const PII=/(^|_)(email|phone|address|name|ip|recipient|contact)(_|$)|subscriberemail|emailaddress/i;
const iso=s=>typeof s==='string'&&/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d)$/.test(s)&&Number.isFinite(Date.parse(s))?Date.parse(s):null;
function noPII(o){if(Array.isArray(o)){o.forEach(noPII);return;}if(o&&typeof o==='object')for(const [k,v] of Object.entries(o)){if(!['email_delivery_eligible','email_state'].includes(k)&&PII.test(k))throw Error('PII_FIELD_REJECTED');noPII(v)}}
const requiredRef=(v)=>typeof v==='string'&&REF.test(v);
export function classifyConfirmedSignups(providerEvents, sessionEvents=[], window={}){
 if(!Array.isArray(providerEvents)||!Array.isArray(sessionEvents))throw Error('ARRAY_REQUIRED');
 noPII(providerEvents);noPII(sessionEvents);
 const start=window.start===undefined?-Infinity:iso(window.start),end=window.end===undefined?Infinity:iso(window.end);
 if(start===null||end===null||start>end)throw Error('BAD_COHORT');
 const reasons=[],valid=[],ownerOfEvent=new Map(),joins=new Map();
 for(const s of sessionEvents){
  if(!s||typeof s!=='object'||Array.isArray(s))throw Error('BAD_SESSION');
  if(s.source!=='authenticated_first_party_session'||s.human_verified!==true||!requiredRef(s.source_ref)||!requiredRef(s.join_ref)||!requiredRef(s.session_ref)||!requiredRef(s.asset_id)||s.utm_content!==s.asset_id||s.utm_medium!=='organic_social'||!requiredRef(s.utm_source)||!requiredRef(s.utm_campaign)||iso(s.at)===null){reasons.push('SESSION_UNPROVEN');continue}
  const signature=JSON.stringify([s.session_ref,s.asset_id,s.utm_source,s.utm_campaign,s.at]);
  if(joins.has(s.join_ref)&&joins.get(s.join_ref)!==signature)throw Error('ATTRIBUTION_JOIN_CONFLICT');
  joins.set(s.join_ref,signature);
 }
 for(const e of providerEvents){
  if(!e||typeof e!=='object'||Array.isArray(e))throw Error('BAD_PROVIDER_ROW');
  const when=iso(e.occurred_at),observed=iso(e.observed_at);
  const common=e.source==='authenticated_jetpack_site_event'&&e.provider_ack===true&&e.site_key==='finalvestige_dispatch'&&e.new_site_subscription===true&&e.dispatch_consent===true&&e.email_delivery_eligible===true&&e.email_state==='active'&&requiredRef(e.subject_ref)&&requiredRef(e.event_ref)&&requiredRef(e.source_ref)&&when!==null&&observed!==null&&when<=observed;
  const emailRoute=e.confirmation_route==='email_link'&&e.event_kind==='email_confirmation_completed'&&e.proof_of_confirmation===true&&requiredRef(e.confirmation_ref);
  const accountRoute=e.confirmation_route==='existing_wp_account'&&e.event_kind==='site_subscription_activated'&&e.existing_wp_account_verified===true&&requiredRef(e.enrollment_ref);
  if(!common||(!emailRoute&&!accountRoute)){reasons.push('PROVIDER_SIGNUP_NOT_PROVEN');continue;}
  const signature=[e.subject_ref,e.confirmation_route,e.occurred_at].join(':');
  if(ownerOfEvent.has(e.event_ref)&&ownerOfEvent.get(e.event_ref)!==signature)throw Error('PROVIDER_EVENT_COLLISION');
  ownerOfEvent.set(e.event_ref,signature);valid.push({...e,_time:when});
 }
 const seenSubjects=new Set(),seenEvents=new Set();let confirmed=0,attributed=0,email=0,account=0;
 valid.sort((a,b)=>a._time-b._time||a.event_ref.localeCompare(b.event_ref));
 for(const e of valid){if(seenEvents.has(e.event_ref))continue;seenEvents.add(e.event_ref);
  if(seenSubjects.has(e.subject_ref)){reasons.push('DUPLICATE_OR_PRIOR_SITE_SIGNUP');continue}
  seenSubjects.add(e.subject_ref);
  if(e._time<=start||e._time>end)continue;
  confirmed++;if(e.confirmation_route==='email_link')email++;else account++;
  if(requiredRef(e.join_ref)&&joins.has(e.join_ref))attributed++;
 }
 return Object.freeze({confirmed_signup:confirmed,email_link_confirmed:email,existing_wp_account_activated:account,attributed_confirmed_signup:attributed,rejected_evidence:reasons.length,mail_actions:0,eligible_recipient_count:null,trust_boundary:'INPUTS_MUST_BE_AUTHENTICATED_PRIVATELY_NOT_LIVE_DATA'});
}
