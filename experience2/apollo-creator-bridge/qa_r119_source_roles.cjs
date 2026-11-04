'use strict';
/* R119: read-only Apollo/Research Desk source-role reconciliation. Never certifies reuse, sale or release. */
const fs=require('node:fs');
const R=[
 ['01','S67-19766','https://www.nasa.gov/image-detail/apollo-1-crew-honored/'],
 ['02','S67-15717','https://www.nasa.gov/image-detail/amf-s67-15717/'],
 ['03','S66-58038','https://www.nasa.gov/image-detail/amf-s66-58038/'],
 ['04','KSC-20170124-PH_KLS01_0164','https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/'],
 ['05','S67-21294','https://www.nasa.gov/image-detail/amf-s67-21294/'],
 ['06','KSC-20170124-PH_KLS01_0090','https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/']
];
function collect(source,tag,prefix){
 const found=new Map();
 const re=new RegExp('<'+tag+'\\b[^>]*\\bid="'+prefix+'(\\d{2})"[^>]*>[\\s\\S]*?<\\/'+tag+'>','g');
 for(const m of source.matchAll(re)){if(found.has(m[1]))throw Error('DUPLICATE_ID:'+prefix+m[1]);found.set(m[1],m[0]);}
 return found;
}
function audit(apollo,desk){
 const blockers=[],flags=[],records=[];
 const row=collect(apollo,'tr','photo-source-');
 const card=collect(desk,'article','fv-ex2-ledger-apollo1-record-');
 if(row.size!==6)blockers.push('APOLLO_NOT_SIX_PHOTO_ROWS:'+row.size);
 if(card.size!==6)blockers.push('RESEARCH_DESK_NOT_SIX_RECORDS:'+card.size);
 if(!apollo.includes('data-fv-source-role-key')||
    !apollo.includes('Two kinds of evidence—not interchangeable'))
   blockers.push('MISSING_ON_PAGE_SOURCE_ROLE_EXPLANATION');
 if(!apollo.includes('INDIVIDUAL_REVIEW_REQUIRED')||!apollo.includes('(0/6)')||
    !apollo.includes('S67-19766 (provisional)'))
   blockers.push('UNRESOLVED_RIGHTS_OR_CATALOG_WARNING_MISSING');
 if(/<img\b|<iframe\b|data-(lat|lng|longitude|latitude)=/i.test(apollo))
   blockers.push('UNREVIEWED_MEDIA_OR_GEO_ADDED');
 if(/<form\b|payhip\.com|<script[^>]+src=/i.test(apollo))
   blockers.push('UNAPPROVED_CAPTURE_COMMERCE_OR_REMOTE_SCRIPT');
 if((apollo.match(/data-fv-primary-cta(?=[\s>])/g)||[]).length!==1)
   blockers.push('PRIMARY_CTA_NOT_UNIQUE');
 for(const [number,id,url] of R){
   const a=row.get(number),d=card.get(number),entry={number,catalog_id:id,photo_role:'VISUAL_CONTEXT_ONLY',rights:'INDIVIDUAL_REVIEW_REQUIRED',status:'PENDING'};
   if(!a){blockers.push('PHOTO_ROW_MISSING:'+number);records.push(entry);continue;}
   if(!d){blockers.push('DESK_RECORD_MISSING:'+number);records.push(entry);continue;}
   if(!a.includes(url)||!d.includes(url))blockers.push('PHOTO_SOURCE_URL_MISMATCH:'+number);
   if(!a.includes(id)||!d.includes(id))blockers.push('PHOTO_CATALOG_DRIFT:'+number);
   if(number==='01'&&!/S67-19766\s*\(provisional\)/.test(d))
     flags.push('DESK_CREW_ID_OVERSTATED:01');
   if(number==='02'&&d.includes('PRIMARY REVIEW BOARD RECORD'))
     flags.push('PHOTO_MISLABELED_REVIEW_BOARD:02');
   if(number==='03'&&d.includes('INSTRUMENT CHRONOLOGY'))
     flags.push('PHOTO_MISLABELED_SENSOR_EVIDENCE:03');
   if(number==='04'&&d.includes('HARDWARE AND DESIGN FINDING'))
     flags.push('RETROSPECTIVE_PHOTO_MIXED_WITH_1967_FINDING:04');
   if(number==='05'&&d.includes('EVIDENCE BOUNDARY'))
     flags.push('POST_FIRE_PHOTO_MIXED_WITH_IGNITION_ANALYSIS:05');
   if(number==='06'&&d.includes('ENGINEERING RESPONSE'))
     flags.push('RETROSPECTIVE_PHOTO_MIXED_WITH_ENGINEERING_SUMMARY:06');
   entry.status='SOURCE_URL_PRESENT_NOT_REUSE_CLEARED';records.push(entry);
 }
 return {classification:'READ_ONLY_SOURCE_ROLE_AUDIT',gate:'STAGING_HOLD',releasable:false,
         apollo_photo_rows:row.size,desk_records:card.size,records,blockers,editorial_review_flags:flags,
         reason:'Source roles and individual photo-use rights require independent review; not a NASA rights clearance or product approval.'};
}
module.exports={R,collect,audit};
if(require.main===module){
 const [apolloPath,deskPath]=process.argv.slice(2);
 if(!apolloPath||!deskPath){process.stderr.write('Usage: node qa_r119_source_roles.cjs APOLLO_HTML RESEARCH_DESK_HTML\n');process.exit(2);}
 const result=audit(fs.readFileSync(apolloPath,'utf8'),fs.readFileSync(deskPath,'utf8'));
 process.stdout.write(JSON.stringify(result,null,2)+'\n');
 process.exit(result.blockers.length?2:result.editorial_review_flags.length?3:4);
}
