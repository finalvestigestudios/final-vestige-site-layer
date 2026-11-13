/** R319 evidence adapter prototype: no I/O, no sending, NO authentication of input.
 * Real provider provenance must be authenticated separately by Claude/Focus. */
const keyPII=/(^|_)(email|phone|address|name|ip|recipient|contact)(_|$)|subscriberemail|emailaddress/i;
const statuses=new Set(["unconfirmed","active","unsubscribed","paused","reader_only"]);
const ref=x=>typeof x==="string"&&/^[A-Za-z0-9:_-]{3,96}$/.test(x);
const timestamp=x=>typeof x==="string"&&/^\d{4}-\d\d-\d\dT/.test(x)&&Number.isFinite(Date.parse(x))?Date.parse(x):null;
function guard(obj){if(Array.isArray(obj)){obj.forEach(guard);return}if(obj&&typeof obj==="object")for(const [k,v] of Object.entries(obj)){if(!["email_state","email_delivery_eligible"].includes(k)&&keyPII.test(k))throw Error("PII_FIELD_REJECTED");if(v&&typeof v==="object")guard(v)}}
export function confirmedTransitions(providerRows,sessionRows=[],cohort={}){
 if(!Array.isArray(providerRows)||!Array.isArray(sessionRows))throw Error("ARRAY_REQUIRED");guard(providerRows);guard(sessionRows);
 const begin=cohort.start?timestamp(cohort.start):-Infinity,end=cohort.end?timestamp(cohort.end):Infinity;if(begin===null||end===null||begin>end)throw Error("BAD_COHORT");
 const bySubscriber=new Map(),ids=new Set(),reject=[];
 for(const p of providerRows){
  if(!p||typeof p!=="object"||Array.isArray(p))throw Error("BAD_PROVIDER_ROW");
  const at=timestamp(p.at);
  if(p.origin!=="jetpack_private_verified"||p.provider_ack!==true||!ref(p.subject_ref)||!ref(p.observation_ref)||!ref(p.source_ref)||at===null||!statuses.has(p.email_state)){reject.push("INVALID_PROVIDER_EVIDENCE");continue}
  if(ids.has(p.observation_ref))continue;ids.add(p.observation_ref);
  if(!bySubscriber.has(p.subject_ref))bySubscriber.set(p.subject_ref,[]);
  bySubscriber.get(p.subject_ref).push({...p,_ts:at});
 }
 const verifiedJoins=new Map();
 for(const s of sessionRows){
  if(!s||typeof s!=="object"||Array.isArray(s))throw Error("BAD_SESSION");
  if(s.origin!=="first_party_server_verified"||s.human_verified!==true||!ref(s.join_ref)||!ref(s.session_ref)||!ref(s.asset_id)||s.utm_content!==s.asset_id||s.utm_medium!=="organic_social"||!ref(s.source_ref)||timestamp(s.at)===null){reject.push("UNVERIFIED_FIRST_PARTY_SESSION");continue}
  const sign=JSON.stringify([s.asset_id,s.utm_source,s.utm_campaign,s.session_ref]);
  if(verifiedJoins.has(s.join_ref)&&verifiedJoins.get(s.join_ref)!==sign)throw Error("ATTRIBUTION_JOIN_CONFLICT");
  verifiedJoins.set(s.join_ref,sign);
 }
 let confirmed=0,attributed=0,firstActive=0;const confirmationIds=new Set();
 for(const observations of bySubscriber.values()){
  observations.sort((a,b)=>a._ts-b._ts||a.observation_ref.localeCompare(b.observation_ref));
  let prev=null,everConfirmed=false;
  for(const now of observations){
   if(now.email_state==="active"&&!prev)firstActive++;
   if(now.email_state==="active"&&prev?.email_state==="unconfirmed"&&!everConfirmed){
    const proof=now.dispatch_consent===true&&now.email_delivery_eligible===true&&ref(now.confirmation_event_ref);
    if(proof){everConfirmed=true;
     if(now._ts>begin&&now._ts<=end&&!confirmationIds.has(now.confirmation_event_ref)){confirmationIds.add(now.confirmation_event_ref);confirmed++;if(ref(now.join_ref)&&verifiedJoins.has(now.join_ref))attributed++}
    }else reject.push("MISSING_CONSENT_OR_CONFIRMATION");
   }
   prev=now;
  }
 }
 return Object.freeze({confirmed_signup:confirmed,attributed_confirmed_signup:attributed,first_seen_active_not_counted:firstActive,rejected_evidence:reject.length,eligible_recipient_count:null,mail_actions:0,source_level:"SYNTHETIC_CONTRACT_NOT_LIVE_VERIFIED"});
}
