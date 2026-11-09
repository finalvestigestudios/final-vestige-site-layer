const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(__dirname+'/source_gate.cjs','utf8');
const original=fs.readFileSync(__dirname+'/contract.json','utf8');
function check(obj){
 const ctx={require:(id)=>id==='node:fs'?{readFileSync:()=>JSON.stringify(obj)}:require(id),__dirname,console:{log:()=>{}}};
 try{vm.runInNewContext(source,ctx);return true}catch{return false}
}
const base=JSON.parse(original);assert.equal(check(base),true);let rejected=0;
for(const [k,v] of [['all_six_release_state','READY'],['send_new_posts_default',true],['postal_address_verified',true],['real_unsubscribe_verified',true],['real_jetpack_preview_verified',true],['native_preheader_control_verified',true],['actual_email_eligible_recipients',3],['realized_net_revenue_per_1000_humans',0]]){let a=structuredClone(base);a[k]=v;assert.equal(check(a),false);rejected++;}
for(let i=0;i<6;i++)for(const [k,v] of [['send_authorized',true],['post_created',true],['native_preheader_verified',true],['affiliate_earning_url','https://example.org/?affiliate=1'],['realized_net_revenue',123],['source_sha','bad']]){let a=structuredClone(base);a.issues[i][k]=v;assert.equal(check(a),false);rejected++;}
for(let i of [2,4])for(const [k,v] of [['cta','https://zen12.com/hnp'],['cta_status','LIVE'],['affiliate_permission_verified',true]]){let a=structuredClone(base);a.issues[i][k]=v;assert.equal(check(a),false);rejected++;}
console.log('PASS baseline + '+rejected+' synthetic release/merchant false-positives rejected');
