'use strict';
const fs=require('node:fs'),path=require('node:path');
const CATALOG=[["USAF 070125-F-0000Z-099",null,"unverified_official_image_record"],["USAF 050606-F-1234P-012","https://www.nationalmuseum.af.mil/Upcoming/Photos/igphoto/2000572755/","same_virin_official_catalog"],["USAF 050606-F-1234P-014","https://www.nationalmuseum.af.mil/Upcoming/Photos/igphoto/2000572753/","same_virin_official_catalog"],["Army QM Museum M1910 canteen 2012-09","https://qmmuseum.army.mil/explore/artifact-of-the-month/2012.html","official_artifact_not_binary_matched"],["NARA diary images 342-B-ND-075-4-163133AC and 163134AC","https://unwritten-record.blogs.archives.gov/2017/06/16/lost-and-found-the-story-of-lady-be-good-and-her-crew/","related_image_not_exact"],["NARA 111-C-17240","https://unwritten-record.blogs.archives.gov/2017/06/16/lost-and-found-the-story-of-lady-be-good-and-her-crew/111-c-17240/","same_attachment_basename_not_visual_proof"],["USAF 060530-F-1234S-041","https://www.nationalmuseum.af.mil/Upcoming/Photos/igphoto/2000554420/","same_virin_official_catalog"]];
function validate(m,inv){
 const e=[],bad=s=>e.push(s);
 if(m?.schema!=='fv-media-recovery-lady-be-good-278-v1'||m.post_id!==278||m.total_slots!==7||m.external_slots!==7)bad('scope');
 if(m?.cms_check?.status!=='publish'||m.cms_check.read_only!==true||m.cms_check.exact_src!==7||m.cms_check.exact_alt!==7)bad('CMS source');
 if(m.visitor_broken_count!==null||m.production_images_repaired!==0||m.reported_sitewide_42_broken_verified!==false||m.claimed_sitewide_76pct_reduction_verified!==false)bad('unsupported outcome');
 const originals=inv?.images?.filter(x=>x.post_id===278).sort((a,b)=>a.slot-b.slot)||[];
 if(originals.length!==7||!Array.isArray(m.records)||m.records.length!==7){bad('missing slots');return e;}
 for(let i=0;i<7;i++){
  const r=m.records[i],s=originals[i],c=CATALOG[i];if(!r){bad('missing '+i);continue;}
  if(r.key!==s.key||r.slot!==i||r.source_url!==s.source_url||r.alt!==s.alt||s.source_kind!=='external')bad('source drift '+i);
  if(r.official_id!==c[0]||r.official_record_url!==c[1]||r.evidence_level!==c[2])bad('catalog drift '+i);
  for(const p of ['evidence','credit','rights_note','editorial_note'])if(typeof r[p]!=='string'||r[p].length<30)bad('missing provenance '+i+' '+p);
  if(r.rights_status!=='HOLD'||r.original_sha256!==null||r.binary_identity_verified!==false||r.wordpress_media_write_authorized!==false)bad('unlicensed release '+i);
  for(const p of ['guest_http_status','guest_current_src','guest_natural_width','guest_image_transfer_bytes','guest_screenshot'])if(r[p]!==null)bad('fabricated browser '+i+' '+p);
  if(i===2){
   if(r.archival_dimensions?.width!==1800||r.archival_dimensions?.height!==1192||r.derivative_target?.width!==960||r.derivative_target?.height!==636||r.derivative_target.no_upscale!==true)bad('invalid verified geometry');
  }else if(r.archival_dimensions!==null||r.derivative_target!==null)bad('imaginary dimensions '+i);
  if(i===0||i===3){
   if(r.web_retriever_observation?.status!==(i===0?403:502)||!r.web_retriever_observation?.context?.includes('NOT guest browser'))bad('viewer evidence '+i);
  }else if(r.web_retriever_observation!==null)bad('invented viewer status '+i);
 }
 if(!m.records[6]?.editorial_note?.includes('C-47'))bad('lost official caption evidence');
 if(m.records[4]?.evidence_level!=='related_image_not_exact')bad('private diary image not exact');
 return e;
}
module.exports={validate};
if(require.main===module){const m=JSON.parse(fs.readFileSync(path.join(__dirname,'lady_be_good_278_primary_20261031.json'),'utf8'));const inv=JSON.parse(fs.readFileSync(path.join(__dirname,'parts/04.json'),'utf8'));const errors=validate(m,inv);if(errors.length){console.error(errors.join('\n'));process.exitCode=1;}else console.log('PASS Lady Be Good seven-image archival custody');}
