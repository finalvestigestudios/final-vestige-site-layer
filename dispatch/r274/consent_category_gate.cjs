'use strict';
/*
 * FV Dispatch R274: OFFLINE consent and delivery-category boundary specimen.
 * Never reads a real subscriber list, never produces permission to send,
 * and NEVER treats caller-supplied assertions as authenticated Jetpack proof.
 */
const SCHEMA='fv_dispatch_consent_categories_v2';
const STATES=new Set(['pending','not_confirmed','subscribed','reader_only','emails_paused','bounced','suppressed','unsubscribed','not_sending']);
const keys=(x,expected)=>x&&typeof x==='object'&&!Array.isArray(x)&&Object.keys(x).sort().join('|')===expected.slice().sort().join('|');
const opaque=s=>typeof s==='string'&&/^[a-z0-9][a-z0-9_-]{2,47}$/.test(s);
const timestamp=s=>typeof s==='string'&&/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(s)&&!Number.isNaN(Date.parse(s))&&new Date(s).toISOString().slice(0,19)+'Z'===s;
function hold(reason,detail=null,passed=false){
  return {pass:passed,reason,detail,release:'HOLD_UNSENT',
   send_authorized:false,subscribers_contacted:false,
   verified_confirmed_signups:null,verified_current_recipients:null,
   received_welcome:'NOT_VERIFIED',unsubscribe:'NOT_VERIFIED',
   publisher_postal_address:'NOT_VERIFIED',affiliate_email_permission:'NOT_VERIFIED',
   settled_paid_orders:null,realized_net_revenue:null,net_revenue_per_1000:'NOT_COMPUTABLE',
   illustration:null};
}
function evaluate(root){
  const required=['schema','mode','as_of_utc','newsletter_categories_enabled','campaign_category','events'];
  if(!keys(root,required)||root.schema!==SCHEMA||
     !['synthetic','unverified_external'].includes(root.mode)||
     !timestamp(root.as_of_utc)||typeof root.newsletter_categories_enabled!=='boolean'||
     !opaque(root.campaign_category)||!Array.isArray(root.events)||root.events.length>500)
    return hold('INVALID_ROOT');
  const idMap=new Map(),people=new Map();
  const evKeys=['source','scope','subject_ref','event_ref','at_utc','status','consent_origin','categories'];
  for(let i=0;i<root.events.length;i++){
    const e=root.events[i];
    if(!keys(e,evKeys)||e.source!=='jetpack'||e.scope!=='fv_dispatch'||
       e.consent_origin!=='fv_first_party'||!opaque(e.subject_ref)||
       !opaque(e.event_ref)||!timestamp(e.at_utc)||e.at_utc>root.as_of_utc||
       !STATES.has(e.status)||!Array.isArray(e.categories)||
       e.categories.length>20||!e.categories.every(opaque)||
       new Set(e.categories).size!==e.categories.length)
      return hold('INVALID_EVENT',i);
    const old=idMap.get(e.event_ref);
    if(old){
      if(JSON.stringify(old)!==JSON.stringify(e)) return hold('CONFLICTING_EVENT_REF',i);
      continue;
    }
    idMap.set(e.event_ref,e);
    if(!people.has(e.subject_ref))people.set(e.subject_ref,[]);
    people.get(e.subject_ref).push(e);
  }
  let confirmations=[],reactivations=[],pending_attempts=0,eligible=0,category_excluded=0;
  for(const events of people.values()){
    events.sort((a,b)=>a.at_utc.localeCompare(b.at_utc)||a.event_ref.localeCompare(b.event_ref));
    for(let j=1;j<events.length;j++){
      if(events[j].at_utc===events[j-1].at_utc&&
         (events[j].status!==events[j-1].status||
          [...events[j].categories].sort().join(',')!==[...events[j-1].categories].sort().join(',')))
         return hold('AMBIGUOUS_SAME_TIME_STATE');
    }
    let ever=false,previous=null;
    for(const e of events){
      if(e.status==='pending'||e.status==='not_confirmed')pending_attempts++;
      if(e.status==='subscribed'&&!ever){
        confirmations.push(e.at_utc);ever=true;
      }else if(e.status==='subscribed'&&previous!==null&&previous!=='subscribed')
        reactivations.push(e.at_utc);
      previous=e.status;
    }
    const last=events[events.length-1];
    if(last&&last.status==='subscribed'){
      if(!root.newsletter_categories_enabled||last.categories.includes(root.campaign_category))eligible++;
      else category_excluded++;
    }
  }
  // An external data import never authenticates provider provenance, consent or sending permission.
  if(root.mode==='unverified_external')return hold('EXTERNAL_EVIDENCE_NOT_AUTHENTICATED',null,true);
  const windows={};
  for(const [label,days] of [['7d',7],['30d',30]]){
    const since=Date.parse(root.as_of_utc)-days*86400000;
    windows[label]={hypothetical_first_signups:confirmations.filter(x=>Date.parse(x)>=since).length,
                    hypothetical_reactivations:reactivations.filter(x=>Date.parse(x)>=since).length};
  }
  const h=hold('SYNTHETIC_SCENARIO_ONLY',null,true);
  h.illustration={ALL_VALUES_HYPOTHETICAL:true,
     first_signups:confirmations.length,reactivations:reactivations.length,
     pending_attempts,current_subscribed_to_campaign:eligible,
     subscribed_but_category_excluded:category_excluded,windows};
  return h;
}
module.exports={SCHEMA,evaluate};
