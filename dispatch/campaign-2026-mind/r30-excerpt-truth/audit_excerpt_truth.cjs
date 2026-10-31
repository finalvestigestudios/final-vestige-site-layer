'use strict';
// R30: source-grounded proof of OPTIONAL, UNSENT Jetpack custom excerpt copy.
// Pure function: no network, WP writes, subscriber access, email or metric recording.
const anchors=[
 {excerpt:['1998','door','half','photograph'],source:['1998','Simons','Levin']},
 {excerpt:['1784','Puységur','royal commission'],source:['May 4, 1784','Puységur','commission']},
 {excerpt:['Zen12','Beginner','Premium','Advanced'],source:['Zen12','Beginner','Premium','Advanced']},
 {excerpt:['Apollo','17.1','fire','hatch'],source:['17.1','fire','hatch']},
 {excerpt:['Total Focus','33-minute','seller assertions'],source:['Total Focus','33','seller claims']},
 {excerpt:['2002','diaries','Fieldbook'],source:['2002','diaries','Fieldbook']}
];
function audit(excerptData,manifest,sources){
 const errors=[],rows=[];
 if(excerptData.status!=='DRAFT_FOR_WORDPRESS_EDITOR_REVIEW_ONLY')errors.push('excerpt-status');
 if(!/NOT direct affiliate/i.test(excerptData.delivery_mode||''))errors.push('excerpt-mode');
 if(manifest.status!=='DRAFT_UNSENT_NO_SCHEDULING')errors.push('campaign-status');
 if(manifest.mix?.editorial!==4||manifest.mix?.commercial_review_pending!==2)errors.push('campaign-ratio');
 if(excerptData.entries?.length!==6||manifest.issues?.length!==6||sources?.length!==6)errors.push('six-edition-count');
 for(let n=1;n<=6;n++){
  const e=excerptData.entries?.[n-1],m=manifest.issues?.[n-1],source=sources?.[n-1];
  if(!e||!m||typeof source!=='string'){errors.push(n+':missing');continue}
  const s=e.excerpt||'',commercial=n===3||n===5,words=s.trim().split(/\s+/).length;
  if(e.number!==n||e.subject!==m.subject)errors.push(n+':subject-order');
  if(m.publish_state!=='hold'||m.merchant_affiliate_url!==null)errors.push(n+':merchant-activation');
  if((m.kind==='commercial-review-pending')!==commercial)errors.push(n+':role-drift');
  if(words<45||words>100||s.length>350)errors.push(n+':excerpt-budget');
  if(/\[\[|https?:\/\/|<a\b|utm_|aff_id=|clickbank|guaranteed|miracle|clinically proven|cures\b/i.test(s))errors.push(n+':unsafe-text');
  if(!source.includes('**Subject:** '+m.subject)||!source.includes(m.editorial_cta))errors.push(n+':source-drift');
  for(const t of anchors[n-1].excerpt)if(!s.toLowerCase().includes(t.toLowerCase()))errors.push(n+':excerpt-anchor-'+t);
  for(const t of anchors[n-1].source)if(!source.toLowerCase().includes(t.toLowerCase()))errors.push(n+':source-anchor-'+t);
  if(commercial){
   if(!/affiliate evaluation/i.test(s)||!s.includes('may earn a commission')||s.indexOf('may earn a commission')+21>350)errors.push(n+':commission-not-visible');
   if(!m.editorial_cta.startsWith('[[')||!/Commercial disclosure:/.test(source))errors.push(n+':offer-hold-drift');
  }else if(/affiliate|earn a commission|commission-earning|purchase through/i.test(s)||!m.editorial_cta.startsWith('https://finalvestige.com/'))errors.push(n+':editorial-commercial-drift');
  if(n===1&&/eighteenth.c.century|18th.century|1784|Puységur/i.test(s))errors.push('1:wrong-era');
  if(n===4&&(/first indication|fire started|ignition happened|ignition instant was/i.test(s)||!s.includes('first recorded crew report of fire')))errors.push('4:timeline-overclaim');
  if(n===6&&/guarantees improved concentration|proved attention gains|clinically proven to improve/i.test(s))errors.push('6:unproven-outcome');
  rows.push({number:n,subject:m.subject,kind:m.kind,words,characters:s.length,commercial_disclosure_within_first_350:commercial? s.indexOf('may earn a commission')+21<=350:null,source_matched:true,excerpt_approved:false,received_jetpack_email_proven:false,release_status:commercial?'HOLD_UNSENT_AND_MERCHANT':'HOLD_UNSENT'});
 }
 return {schema:'fv-dispatch-r30-custom-excerpt-truth',input_revision:'source-controlled drafts; not native email',errors,rows,ready_to_send:false,live_wp_changes:false};
}
module.exports={audit,anchors};
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path'),root=path.resolve(__dirname,'..');
 const data=JSON.parse(fs.readFileSync(path.join(root,'delivery/wordpress_excerpt_copy.json'),'utf8'));
 const manifest=JSON.parse(fs.readFileSync(path.join(root,'manifest.json'),'utf8'));
 const sources=manifest.issues.map(x=>fs.readFileSync(path.join(root,'issues',String(x.number).padStart(2,'0')+'-'+x.slug+'.md'),'utf8'));
 const report=audit(data,manifest,sources);
 console.log(JSON.stringify(report,null,2));
 if(report.errors.length)process.exitCode=1;
}
