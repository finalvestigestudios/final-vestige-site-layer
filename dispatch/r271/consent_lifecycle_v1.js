'use strict';
/** Offline consent lifecycle specimen. NEVER verifies actual Jetpack consent or authorizes sending. */
const SCHEMA='FV-DISPATCH-CONSENT-LIFECYCLE-V1';
const statuses=new Set(['pending','subscribed','unsubscribed','emails_paused','bounced','suppressed','reader_only']);
const exact=(o,keys)=>!!o&&typeof o==='object'&&!Array.isArray(o)&&JSON.stringify(Object.keys(o).sort())===JSON.stringify(keys.slice().sort());
const ref=s=>typeof s==='string'&&/^[a-z0-9][a-z0-9_-]{2,47}$/.test(s);
const utc=s=>typeof s==='string'&&/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(s)&&!Number.isNaN(Date.parse(s))&&new Date(s).toISOString().slice(0,19)+'Z'===s;
const hold=()=>({release:'HOLD_UNSENT',send_authorized:false,authenticated_confirmation:false,currently_eligible_recipients:null,confirmed_signup_count:null,merchant_sale:'NOT_VERIFIED',net_revenue:'NOT_COMPUTABLE',welcome_delivery:'NOT_VERIFIED',postal:'NOT_VERIFIED',unsubscribe:'NOT_VERIFIED'});
function inspect(input){
 const base=hold(), errors=[];
 if(!exact(input,['schema','mode','as_of_utc','events'])||input.schema!==SCHEMA||!['synthetic','unverified_external'].includes(input.mode)||!utc(input.as_of_utc)||!Array.isArray(input.events))
 return {...base,pass:false,errors:['INVALID_ROOT'],illustration:null};
 const ids=new Map(),persons=new Map();
 for(let i=0;i<input.events.length;i++){
  const e=input.events[i];
  if(!exact(e,['provider','scope','subject_ref','event_ref','at_utc','status'])||e.provider!=='jetpack'||e.scope!=='fv_dispatch'||!ref(e.subject_ref)||!ref(e.event_ref)||!utc(e.at_utc)||e.at_utc>input.as_of_utc||!statuses.has(e.status)){errors.push('INVALID_EVENT_'+i);continue;}
  const prior=ids.get(e.event_ref);
  if(prior){if(JSON.stringify(prior)!==JSON.stringify(e))errors.push('CONFLICTING_EVENT_REF_'+i);continue;}
  ids.set(e.event_ref,e);
  if(!persons.has(e.subject_ref))persons.set(e.subject_ref,[]);
  persons.get(e.subject_ref).push(e);
 }
 if(errors.length)return {...base,pass:false,errors,illustration:null};
 let first=[],reactivations=[],current=0,pending=0;
 for(const evs of persons.values()){
  evs.sort((a,b)=>a.at_utc.localeCompare(b.at_utc)||a.event_ref.localeCompare(b.event_ref));
  for(let j=1;j<evs.length;j++)if(evs[j].at_utc===evs[j-1].at_utc&&evs[j].status!==evs[j-1].status)errors.push('AMBIGUOUS_SIMULTANEOUS_STATUS');
  let previouslyConfirmed=false,last=null;
  for(const e of evs){
   if(e.status==='pending')pending++;
   if(e.status==='subscribed'&&!previouslyConfirmed){previouslyConfirmed=true;first.push(e.at_utc);}
   else if(e.status==='subscribed'&&last!==null&&last!=='subscribed')reactivations.push(e.at_utc);
   last=e.status;
  }
  if(last==='subscribed')current++;
 }
 if(errors.length)return {...base,pass:false,errors:[...new Set(errors)],illustration:null};
 if(input.mode==='unverified_external')return {...base,pass:true,errors:[],evidence:'UNVERIFIED_EXTERNAL',illustration:null};
 const asof=Date.parse(input.as_of_utc),windows={};
 for(const [key,days] of [['7d',7],['30d',30]]){
  const cutoff=asof-days*86400000;
  windows[key]={first_confirmations:first.filter(x=>Date.parse(x)>=cutoff).length,reactivations:reactivations.filter(x=>Date.parse(x)>=cutoff).length};
 }
 return {...base,pass:true,errors:[],evidence:'SYNTHETIC_ONLY',
 illustration:{ALL_VALUES_HYPOTHETICAL:true,pending_attempts:pending,first_time_confirmations:first.length,current_eligible_in_example:current,windows}};
}
module.exports={inspect,SCHEMA};
