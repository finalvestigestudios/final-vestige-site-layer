'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {auditRoutes}=require('../route_audit.cjs');
const root=path.resolve(__dirname,'../..');
const m=JSON.parse(fs.readFileSync(path.join(root,'manifest.json'),'utf8'));
const x=JSON.parse(fs.readFileSync(path.join(root,'delivery/wordpress_excerpt_copy.json'),'utf8'));
const s=JSON.parse(fs.readFileSync(path.join(__dirname,'../SITE_SNAPSHOT.json'),'utf8'));
let count=0,mutations=0;
const ok=(v,msg)=>{assert.ok(v,msg);count++};
const copy=v=>JSON.parse(JSON.stringify(v));
const r=auditRoutes(m,x,s);
ok(r.errors.length===0,'source-controlled six-edition baseline');
ok(r.routes.length===6,'six route rows');
ok(r.routes.every(q=>q.total_reader_hops_to_manifest_cta===2&&q.newsletter_post_url===null),'do not invent campaign-post URLs');
ok(r.routes.every(q=>!q.approved_to_send&&!q.native_email_received),'all unsent');
ok(r.routes.filter(q=>q.status==='HOLD_UNSENT_AND_HOLD_MERCHANT').length===2,'4:2 split');
ok(r.warnings.length>=3,'read cue ambiguity should be detected');
for(const q of r.routes){ok(q.legal_postal_footer_verified===false,'address not verified');ok(q.functional_unsubscribe_verified===false,'unsub not verified');ok(q.preheader_native_verified===false,'preheader not verified');}
const attacks=[
 ['send status',(a)=>a.status='READY',0],['wrong mix',(a)=>a.mix.editorial=5,0],
 ['merchant URL',(a)=>a.issues[2].editorial_cta='https://zen12.com',0],
 ['affiliate click',(a)=>a.issues[4].merchant_affiliate_url='https://bad.test',0],
 ['offsite editorial',(a)=>a.issues[0].editorial_cta='https://elsewhere.com',0],
 ['wrong edition',(a)=>a.issues[2].number=9,0],['live post',(a)=>a.issues[0].publish_state='publish',0],
 ['missing issue',(a)=>a.issues.pop(),0],['lost disclosure',(a)=>a.entries[2].excerpt='Buy it.',1],
 ['affiliate editorial',(a)=>a.entries[0].excerpt+=' Affiliate commission.',1],
 ['excerpt URL',(a)=>a.entries[0].excerpt+=' https://bad.test/',1],
 ['premature excerpt',(a)=>a.status='APPROVED',1],
 ['changed format',(a)=>a.email_content_format='full',2],
 ['auto send',(a)=>a.email_new_posts_by_default=true,2],
 ['newsletter disabled',(a)=>a.newsletter_enabled=false,2]
];
for(const [name,fn,target] of attacks){
 const args=[copy(m),copy(x),copy(s)];fn(args[target]);
 ok(auditRoutes(...args).errors.length>0,'must block '+name);mutations++;
}
console.log(JSON.stringify({result:'PASS',assertions:count,adversarial_mutations_rejected:mutations,real_wordpress_email_test:false,emails_sent:0}));
