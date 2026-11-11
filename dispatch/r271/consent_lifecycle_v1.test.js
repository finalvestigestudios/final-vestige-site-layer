'use strict';
const {test}=require('node:test');
const a=require('node:assert/strict');
const {inspect,SCHEMA}=require('./consent_lifecycle_v1.js');
const E=(id,ref,status,at='2026-11-10T00:00:00Z')=>({provider:'jetpack',scope:'fv_dispatch',subject_ref:id,event_ref:ref,at_utc:at,status});
const I=(events,mode='synthetic')=>({schema:SCHEMA,mode,as_of_utc:'2026-11-11T03:00:00Z',events});
const hold=x=>{a.equal(x.release,'HOLD_UNSENT');a.equal(x.send_authorized,false);a.equal(x.currently_eligible_recipients,null);a.equal(x.confirmed_signup_count,null);a.equal(x.net_revenue,'NOT_COMPUTABLE');a(!JSON.stringify(x).includes('person_001'));};
test('pending is never a confirmed lead',()=>{const r=inspect(I([E('person_001','evt_001','pending')]));hold(r);a.equal(r.illustration.first_time_confirmations,0);});
test('first confirmed event is a hypothetical lead only',()=>{const r=inspect(I([E('person_001','evt_001','subscribed')]));hold(r);a.equal(r.illustration.first_time_confirmations,1);});
test('paused bounced unsubscribed suppressed reader-only not eligible',()=>{
 for(const s of ['emails_paused','bounced','unsubscribed','suppressed','reader_only']){
 const r=inspect(I([E('person_001','evt_001','subscribed','2026-11-09T00:00:00Z'),E('person_001','evt_002',s)]));
 hold(r);a.equal(r.illustration.first_time_confirmations,1);a.equal(r.illustration.current_eligible_in_example,0);
 }});
test('reactivation is not another first-time lead',()=>{
 const r=inspect(I([E('person_001','evt_001','subscribed','2026-11-08T00:00:00Z'),E('person_001','evt_002','unsubscribed','2026-11-09T00:00:00Z'),E('person_001','evt_003','subscribed')]));hold(r);
 a.equal(r.illustration.first_time_confirmations,1);a.equal(r.illustration.windows['7d'].reactivations,1);
});
test('identical duplicate event deduplicates, conflicting duplicate rejects',()=>{
 const e=E('person_001','evt_001','subscribed');
 a.equal(inspect(I([e,e])).illustration.first_time_confirmations,1);
 a.equal(inspect(I([e,{...e,status:'pending'}])).pass,false);
});
test('conflicting concurrent states reject',()=>{
 a.equal(inspect(I([E('person_001','evt_001','subscribed'),E('person_001','evt_002','unsubscribed')])).pass,false);
});
test('out of order event arrival uses timestamp',()=>{
 const r=inspect(I([E('person_001','evt_002','unsubscribed'),E('person_001','evt_001','subscribed','2026-11-09T00:00:00Z')]));
 hold(r);a.equal(r.illustration.current_eligible_in_example,0);
});
test('merchant consent cannot become first-party consent',()=>{
 for(const field of ['provider','scope']){const e=E('person_001','evt_001','subscribed');e[field]='zen12';a.equal(inspect(I([e])).pass,false);}
});
test('disallow PII, extra booleans and fake live mode',()=>{
 for(const field of ['email','name','ip','approved']){const e=E('person_001','evt_001','subscribed');e[field]='x';a.equal(inspect(I([e])).pass,false);}
 a.equal(inspect({...I([]),send_authorized:true}).pass,false);
 a.equal(inspect(I([],'verified_live')).pass,false);
});
test('external events cannot prove any count',()=>{
 const r=inspect(I([E('person_001','evt_001','subscribed')],'unverified_external'));hold(r);a.equal(r.illustration,null);
});
test('future and malformed timestamp reject',()=>{
 for(const d of ['2026-11-31T00:00:00Z','2026-12-10T00:00:00Z','yesterday'])a.equal(inspect(I([E('person_001','evt_001','subscribed',d)])).pass,false);
});
