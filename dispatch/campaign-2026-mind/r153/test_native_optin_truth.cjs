'use strict';
const {classify,aggregate,piiFree}=require('./native_optin_truth.cjs');
let checks=0;
function eq(a,b,label){checks++;if(a!==b)throw Error('FAIL '+checks+' '+label+' expected='+b+' got='+a)}
function ok(v,label){eq(!!v,true,label)}
const base={
 provider:'jetpack_native',email_subscription_status:'Subscribed',
 provider_subscriber_ref:'subscriber_001',consent_scope:'finalvestige_dispatch_editorial',
 consent_observed:true,provider_event_ref:'nativeevt_001',
 provider_transition:'new_subscription',verification_route:'email_confirmation_completed',
 provider_transition_at:'2026-11-05T21:15:20Z',confirmation_result:'completed'
};
const c=(changes)=>classify({...base,...changes});
function run(){
 const cases=[
 [{},'CONFIRMED_SIGNUP_CANDIDATE_ONLY','complete confirmation path'],
 [{verification_route:'preverified_wpcom_account',confirmation_result:null,existing_account_preverified:true},'CONFIRMED_SIGNUP_CANDIDATE_ONLY','preverified WP.com path'],
 [{verification_route:'preverified_wpcom_account',existing_account_preverified:false},'ELIGIBLE_SNAPSHOT_CANDIDATE','preverified evidence required'],
 [{confirmation_result:'sent'},'ELIGIBLE_SNAPSHOT_CANDIDATE','sent is not confirmed'],
 [{confirmation_result:'pending'},'ELIGIBLE_SNAPSHOT_CANDIDATE','pending confirmation'],
 [{confirmation_result:null},'ELIGIBLE_SNAPSHOT_CANDIDATE','no confirmation'],
 [{verification_route:'unknown'},'ELIGIBLE_SNAPSHOT_CANDIDATE','unknown route'],
 [{provider:'external_email'},'REJECTED','no imported list'],
 [{provider:'wordpress_reader_only'},'REJECTED','reader-only not provider'],
 [{consent_scope:'other_brand'},'SNAPSHOT_ONLY','wrong consent'],
 [{consent_observed:false},'SNAPSHOT_ONLY','no consent'],
 [{consent_observed:1},'REJECTED','no numeric truthy'],
 [{provider_transition:'old_subscription'},'ELIGIBLE_SNAPSHOT_CANDIDATE','no new join'],
 [{provider_event_ref:'bad'},'ELIGIBLE_SNAPSHOT_CANDIDATE','opaque event required'],
 [{provider_event_ref:null},'ELIGIBLE_SNAPSHOT_CANDIDATE','event absent'],
 [{provider_subscriber_ref:'bad'},'SNAPSHOT_ONLY','provider reference'],
 [{provider_transition_at:'2026-11-05T12:00:00-08:00'},'ELIGIBLE_SNAPSHOT_CANDIDATE','timezone normalized'],
 [{provider_transition_at:'2026-02-30T21:15:20Z'},'ELIGIBLE_SNAPSHOT_CANDIDATE','invalid date'],
 [{provider_transition_at:'2026-11-05'},'ELIGIBLE_SNAPSHOT_CANDIDATE','date-only rejected'],
 [{email_subscription_status:'Unknown'},'REJECTED','unknown status'],
 [{email_subscription_status:'confirmed'},'REJECTED','aggregate not subscriber status'],
 [{email_subscription_status:null},'REJECTED','missing status'],
 [{email:'private@example.com'},'REJECTED','email field'],
 [{full_name:'Example Person'},'REJECTED','name field'],
 [{email_address_hash:'sha256'},'REJECTED','no hashed email'],
 [{raw_query:'utm_content=x'},'REJECTED','no raw query'],
 [{provider_event_ref:'test@example.com'},'REJECTED','email in field'],
 [{ip_address:'1.1.1.1'},'REJECTED','no IP'],
 [{session_tracking:1},'REJECTED','no session field'],
 [{existing_account_preverified:{x:'y'}},'REJECTED','nested value'],
 ];
 for(const [changes,want,label] of cases)eq(c(changes).classification,want,label);
 for(const status of ['Not confirmed','Not subscribed','Bounced','Emails paused','Not sending'])
  eq(c({email_subscription_status:status}).classification,'NOT_EMAIL_ELIGIBLE',status+' ineligible');
 eq(classify(null).classification,'REJECTED','null');
 eq(classify([]).classification,'REJECTED','array');
 ok(piiFree({provider:'jetpack_native',email_subscription_status:'Subscribed'}),'known status fields');
 eq(piiFree({email:'x@y.com'}),false,'PII not accepted');
 const a=aggregate([base,base,{...base,provider_event_ref:'nativeevt_002'},
 {...base,provider_subscriber_ref:'subscriber_002',provider_event_ref:'nativeevt_003'}]);
 eq(a.candidate_count,2,'dedup by native subscriber and event');
 eq(a.duplicate_candidates,2,'duplicate count');
 eq(a.verified_confirmed_signup_count,null,'no self-attested real signups');
 eq(a.independently_eligible_recipient_count,null,'no self-attested eligible count');
 eq(a.received_welcome_count,null,'no inferred welcome');
 eq(a.net_revenue_per_1000_qualified_sessions,null,'no inferred revenue');
 eq(a.classes.length,4,'output classes');
 const other=aggregate([c({email_subscription_status:'Bounced'}),{...base,consent_observed:false},{...base,email:'x@y.com'}]);
 eq(other.rejected_records,2,'derived summaries not native evidence');
 eq(other.snapshot_only_records,1,'native nonconsent snapshot');
 eq(aggregate([]).candidate_count,0,'empty input');
 let threw=false;try{aggregate({})}catch(_){threw=true}ok(threw,'nonarray bounded');
 threw=false;try{aggregate(Array(10001).fill({}))}catch(_){threw=true}ok(threw,'large array refused');
 return {checks,result:'PASS',source:'synthetic only',live_signups_verified:0};
}
if(require.main===module)console.log(JSON.stringify(run()));
module.exports={run};
