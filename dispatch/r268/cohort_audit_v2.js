'use strict';
/** R268: offline acquisition-cohort integrity; no publishing, mailing or network calls.
 * This v2 intentionally does NOT modify the existing R265 prototype. All live
 * external results require independent signed/provider provenance; boolean
 * attestations and arithmetic alone NEVER establish a real sale or send rights.
 */
const SCHEMA='FV-DISPATCH-COHORT-V2';
const PLATFORMS=new Set(['youtube','tiktok','instagram','facebook','pinterest','x','bluesky']);
const CLUSTERS=new Set(['mind','mysteries','history','preparedness']);
const ATTEST=['complete_qualified_sessions','jetpack_confirmations_verified','merchant_settlements_reconciled','cohort_attribution_verified','publisher_postal_and_unsubscribe_verified','partner_email_permission_verified','founder_campaign_approval'];
const exact=(x,fields)=>x!==null && typeof x==='object' && !Array.isArray(x) &&
  JSON.stringify(Object.keys(x).sort())===JSON.stringify(fields.slice().sort());
const validDay=x=>typeof x==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(x)&&
  !Number.isNaN(Date.parse(x+'T00:00:00Z'))&&new Date(x+'T00:00:00Z').toISOString().slice(0,10)===x;
const dayNumber=x=>Date.parse(x+'T00:00:00Z')/86400000;
const nonnegative=x=>Number.isSafeInteger(x)&&x>=0;
const asset=x=>typeof x==='string'&&/^[a-z0-9][a-z0-9_-]{1,62}$/.test(x);
const campaign=x=>typeof x==='string' && /^(mind|mysteries|history|preparedness)_pilot_2026_11$/.test(x) && CLUSTERS.has(x.split('_')[0]);
const validRoute=(x,allowProfile=false)=>PLATFORMS.has(x.utm_source)&&x.utm_medium==='organic_social'&&
  campaign(x.utm_campaign)&&(
    (x.attribution_class==='tagged_asset'&&asset(x.utm_content)) ||
    (allowProfile&&x.attribution_class==='profile_unresolved'&&x.utm_content===null)
  );
const empty=errors=>({pass:false,errors,state:'HOLD_UNSENT',send_authorized:false,cohorts:null});
function inspect(input){
 const errors=[];const add=x=>{if(!errors.includes(x))errors.push(x);};
 if(!exact(input,['schema','mode','as_of_day','attestations','sessions','confirmations','settlements']))return empty(['invalid_top_level']);
 if(input.schema!==SCHEMA||!['synthetic','external_aggregate'].includes(input.mode)||!validDay(input.as_of_day))return empty(['invalid_schema_mode_date']);
 const at=input.attestations;
 if(!exact(at,ATTEST)||ATTEST.some(k=>typeof at[k]!=='boolean'))add('invalid_attestation_shape');
 if(at?.publisher_postal_and_unsubscribe_verified!==false||at?.partner_email_permission_verified!==false||at?.founder_campaign_approval!==false)add('improper_release_assertion');
 if(!Array.isArray(input.sessions)||!Array.isArray(input.confirmations)||!Array.isArray(input.settlements))return empty([...errors,'event_lists_required']);
 const sessions=[];const confirmations=[];const orders=[];
 const seenSession=new Set(),seenConfirmation=new Map(),seenOrder=new Set();
 const sessionFields=['day','utm_source','utm_medium','utm_campaign','utm_content','attribution_class','qualified_human_sessions'];
 const confirmFields=['day','provider','event_ref','status','consent_scope'];
 const settlementFields=['acquisition_day','settled_day','merchant','order_ref','utm_source','utm_medium','utm_campaign','utm_content','attribution_class','status','gross_cents','refund_cents','fee_cents'];
 input.sessions.forEach((s,i)=>{
  if(!exact(s,sessionFields)||!validDay(s.day)||s.day>input.as_of_day||!validRoute(s,true)||!nonnegative(s.qualified_human_sessions))return add('invalid_session_'+i);
  const key=[s.day,s.utm_source,s.utm_medium,s.utm_campaign,s.utm_content,s.attribution_class].join('|');
  if(seenSession.has(key))return add('duplicate_daily_session_'+i);
  seenSession.add(key);sessions.push(s);
 });
 input.confirmations.forEach((c,i)=>{
  if(!exact(c,confirmFields)||!validDay(c.day)||c.day>input.as_of_day||c.provider!=='jetpack'||!asset(c.event_ref)||!['confirmed','pending','suppressed'].includes(c.status)||c.consent_scope!=='fv_dispatch')return add('invalid_confirmation_'+i);
  const prev=seenConfirmation.get(c.event_ref);
  if(prev){if(JSON.stringify(prev)!==JSON.stringify(c))add('conflicting_confirmation_ref_'+i);return;}
  seenConfirmation.set(c.event_ref,c);
  if(c.status==='confirmed')confirmations.push(c);
 });
 input.settlements.forEach((o,i)=>{
  if(!exact(o,settlementFields)||!validDay(o.acquisition_day)||!validDay(o.settled_day)||o.acquisition_day>o.settled_day||o.settled_day>input.as_of_day||o.merchant!=='inspire3'||!asset(o.order_ref)||!validRoute(o)||!['settled','refunded','pending'].includes(o.status)||![o.gross_cents,o.refund_cents,o.fee_cents].every(nonnegative)||o.refund_cents>o.gross_cents)return add('invalid_settlement_'+i);
  if(seenOrder.has(o.order_ref))return add('duplicate_order_'+i);
  seenOrder.add(o.order_ref); if(o.status!=='pending')orders.push(o);
 });
 if(errors.length)return empty(errors);
 const confirmed=at.complete_qualified_sessions&&at.jetpack_confirmations_verified&&at.merchant_settlements_reconciled&&at.cohort_attribution_verified;
 const cohorts={};const now=dayNumber(input.as_of_day);
 for(const n of [7,30]){
  const start=now-n+1,inPeriod=d=>dayNumber(d)>=start&&dayNumber(d)<=now;
  const inSessions=sessions.filter(s=>inPeriod(s.day));
  const tagged=inSessions.filter(s=>s.attribution_class==='tagged_asset');
  const profile=inSessions.filter(s=>s.attribution_class==='profile_unresolved');
  const routeDay=new Set(tagged.filter(s=>s.qualified_human_sessions>0).map(s=>[s.day,s.utm_source,s.utm_medium,s.utm_campaign,s.utm_content].join('|')));
  const attributable=orders.filter(o=>inPeriod(o.acquisition_day)&&routeDay.has([o.acquisition_day,o.utm_source,o.utm_medium,o.utm_campaign,o.utm_content].join('|')));
  const unmatched=orders.filter(o=>inPeriod(o.acquisition_day)&&!routeDay.has([o.acquisition_day,o.utm_source,o.utm_medium,o.utm_campaign,o.utm_content].join('|')));
  const sum=(rows,key)=>rows.reduce((a,b)=>a+b[key],0);
  const visits=sum(tagged,'qualified_human_sessions'), unassigned=sum(profile,'qualified_human_sessions');
  const gross=sum(attributable,'gross_cents'),refunds=sum(attributable,'refund_cents'),fees=sum(attributable,'fee_cents');
  if(![visits,unassigned,gross,refunds,fees].every(Number.isSafeInteger))return empty(['aggregate_overflow']);
  const ordersKnown=at.merchant_settlements_reconciled&&at.cohort_attribution_verified;
  const money=confirmed&&visits>0;
  cohorts[n+'d']={start_day:new Date(start*86400000).toISOString().slice(0,10),end_day:input.as_of_day,
   qualified_tagged_asset_sessions:at.complete_qualified_sessions?visits:null,
   qualified_profile_sessions_without_asset:at.complete_qualified_sessions?unassigned:null,
   confirmed_signups_unjoined:at.jetpack_confirmations_verified?confirmations.filter(c=>inPeriod(c.day)).length:null,
   independently_attributable_sales:'NOT_VERIFIED_BY_THIS_TOOL',
   matched_reported_orders:ordersKnown?attributable.length:null,
   unmatched_reported_orders:ordersKnown?unmatched.length:null,
   gross_cents:ordersKnown?gross:null,refund_cents:ordersKnown?refunds:null,fees_cents:ordersKnown?fees:null,
   net_cents:ordersKnown?gross-refunds-fees:null,
   net_cents_per_1000_qualified_tagged_sessions:money?Math.round((gross-refunds-fees)*1000/visits):null,
   lead_to_customer_rate:null,
   tiny_sample_warning:visits<1000,
   qualification:'Route/day agreement is NOT a person-level link, merchant verification or independent proof of a sale.'};
 }
 return{pass:true,errors:[],schema:SCHEMA,state:'HOLD_UNSENT',send_authorized:false,affiliate_activation_authorized:false,
  evidence_class:input.mode==='synthetic'?'SYNTHETIC_EXAMPLE':'UNVERIFIED_EXTERNAL_ATTESTATION',cohorts,
  warnings:['CAN-SPAM footer, opt-out, list consent, actual welcome delivery and founder campaign approval remain blocked.',
   'Only independently reconciled merchant settlements can establish paid sales. Asset/day match is insufficient.',
   'No subscriber identity, mail send, import, tracking script, payment API or WordPress write.']};
}
module.exports={inspect,SCHEMA};
