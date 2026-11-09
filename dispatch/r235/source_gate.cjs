const fs=require('node:fs'),assert=require('node:assert/strict');
const d=JSON.parse(fs.readFileSync(__dirname+'/contract.json','utf8'));
let problems=[];
const expected=['2a573f6b7043c101ece49703f2dd1262ec2b0ee6','fb8cf1503acb2338a4884cac58b7c3b2cec95af7','b86572c15d05316801a007c00e9a2689a5de27c3','7de77ccdc312e5bdf77a9aaa355c3a9ba4efa2c8','a62a74c6cc2a3722048ff801ccba6212a6cdb397','94b2e31594f0cdea1ec49f654429fa5f3a7b89c6'];
if(d.partner_email_rights_verified!==false||d.received_welcome_verified!==false||d.verified_paid_orders!==null||d.qualified_human_sessions!==null)problems.push('false consent/revenue claim');

if(d.all_six_release_state!=='HOLD_UNSENT'||d.send_new_posts_default!==false)problems.push('send state');
if(d.actual_email_eligible_recipients!==null||d.realized_net_revenue_per_1000_humans!==null)problems.push('invented metrics');
if(d.postal_address_verified!==false||d.real_unsubscribe_verified!==false||d.real_jetpack_preview_verified!==false||d.native_preheader_control_verified!==false)problems.push('false legal/preview proof');
if(!Array.isArray(d.issues)||d.issues.length!==6)problems.push('six issues');
else {
  const kinds=d.issues.map(x=>x.kind);
  if(kinds.filter(x=>x==='editorial').length!==4||kinds.filter(x=>x==='commercial-review-pending').length!==2)problems.push('mix');
  for(let k=0;k<6;k++){
    const e=d.issues[k],c=[3,5].includes(k+1);
    if(e.number!==k+1||e.source_sha!==expected[k]||!/^[0-9a-f]{40}$/.test(e.source_sha))problems.push('identity '+k);
    if(!e.subject||!e.preheader||e.native_preheader_verified!==false||e.send_authorized!==false||e.post_created!==false||e.affiliate_earning_url!==null||e.realized_net_revenue!==null)problems.push('unauthorized '+k);
    if(c && (!e.cta.startsWith('[[APPROVED_')||e.cta_status!=='NOT_LIVE'||e.affiliate_permission_verified!==false))problems.push('merchant '+k);
    if(!c && (!e.cta.startsWith('https://finalvestige.com/')||e.cta_status!=='WORDPRESS_PUBLISHED_READONLY'))problems.push('editorial '+k);
  }
}
if(problems.length)throw Error(problems.join(', '));
console.log('PASS: six source-bound unsent post intents; no affiliate activation, native email or revenue attested');
