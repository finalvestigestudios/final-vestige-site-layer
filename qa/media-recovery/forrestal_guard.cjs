'use strict';
/**
 * Guard source-specific archival suggestions, not HTTP/image availability.
 * Use: node qa/media-recovery/forrestal_guard.cjs
 * No network, WordPress writes or dependency installation.
 */
const fs=require('node:fs'),path=require('node:path');
function isSafeRecord(url){
 if(typeof url!=='string'||!/^https:\/\//.test(url)||/[\s\\]/.test(url))return false;
 const hostname=url.match(/^https:\/\/([^\/:?#]+)/)?.[1]?.toLowerCase();
 return ['commons.wikimedia.org','www.history.navy.mil','www.dvidshub.net'].includes(hostname);
}
function verifyForrestal(doc,source){
 const errors=[],bad=(msg)=>errors.push(msg);
 if(!doc||doc.schema_version!==1||doc.post_id!==289)bad('wrong manifest identity');
 if(!Array.isArray(doc?.rows)||doc.rows.length!==6)bad('require six rows');
 if(!Array.isArray(source)||source.filter(s=>s.post_id===289).length!==6)bad('source snapshot missing six Forrestal images');
 if(doc?.counts?.visitor_verified_broken!==null||doc?.counts?.savings_percent!==null)bad('unmeasured KPI must remain null');
 const seen=new Set();let exact=0,subject=0;
 for(const r of doc?.rows||[]){
  if(seen.has(r.image_key))bad('duplicate image key '+r.image_key);seen.add(r.image_key);
  const s=source?.find(v=>v.key===r.image_key);
  if(!s||s.post_id!==289||s.source_url!==r.original_source_url||s.alt!==r.stored_alt)bad('source drift '+r.image_key);
  if(r.current_browser_http_status!==null||r.current_browser_natural_width_px!==null||r.current_browser_transfer_bytes!==null||r.broken_in_real_browser!==null)bad('fabricated browser measurement '+r.image_key);
  if(r.original_image_sha256!==null||r.candidate_image_sha256!==null||r.visual_match_proven!==false)bad('no byte/visual match proved '+r.image_key);
  if(r.item_rights_cleared!==false||r.candidate_downloaded!==false||r.word_press_media_uploaded!==false||r.word_press_post_edited!==false)bad('unapproved asset mutation '+r.image_key);
  if(!isSafeRecord(r.candidate?.url)||r.candidate?.url!==r.release_plan?.clickable_primary_record)bad('invalid catalog source '+r.image_key);
  const c=r.candidate||{},l=r.release_plan||{};
  if(!/^(?:[A-Z]|File:|\d{6}-N-)/.test(c.catalog_id||''))bad('catalog identifier needed '+r.image_key);
  if(!Number.isInteger(c.photo_year)||c.photo_year<1900||c.photo_year>2026)bad('invalid historical date '+r.image_key);
  if(!Array.isArray(c.reported_dimensions)||c.reported_dimensions.length!==2||c.reported_dimensions.some(n=>!Number.isInteger(n)||n<=0))bad('unverified source dimensions '+r.image_key);
  if(l.max_width_px!==960||l.no_upscale!==true||l.preserve_aspect_ratio!==true||l.target_dimensions_px!==null||l.wordpress_media_id!==null||l.verify_real_visitor_breakage_first!==true||l.require_logged_out_before_after_wire_bytes!==true)bad('unsafe image optimization plan '+r.image_key);
  if(c.kind==='subject_only_alternative'){subject++;
   if(c.caption_revision_required!==true||l.alt_change_requires_editorial_approval!==true||c.category?.startsWith('exact_'))bad('substitute frame must require editorial review '+r.image_key);
  }else if(c.kind==='same_stored_frame_commons_catalog'||c.kind==='same_stored_frame_official_catalog_identifier'){exact++;
   if(c.caption_revision_required!==false||l.alt_change_requires_editorial_approval!==false)bad('exact catalog alt mismatch '+r.image_key);
  }else bad('unclear identity evidence tier '+r.image_key);
  if(r.image_key==='289:2'&&(!c.category?.includes('not_aerial')||c.caption_revision_required!==true))bad('do not represent deck inspection as aerial '+r.image_key);
  if(r.image_key==='289:4'&&(c.photo_year!==2021||c.catalog_id!=='210811-N-SG189-1105'||!r.original_source_url.includes(c.catalog_id)))bad('2021 VIRIN mismatch');
  if(r.image_key==='289:5'&&(c.photo_year!==2013||c.catalog_id!=='130726-N-ST310-007'||!r.original_source_url.includes('/985674/')))bad('2013 DVIDS ID mismatch');
  if(r.image_key==='289:0'&&(!c.url.endsWith('USS_Forrestal_A-4_Skyhawk_burning.png')||c.photo_year!==1967))bad('Commons title mismatch');
 }
 if(seen.size!==6||[0,1,2,3,4,5].some(n=>!seen.has('289:'+n)))bad('expected six source slots 289:0..289:5');
 if(exact!==3||subject!==3||doc?.counts?.exact_filename_or_id_matches!==exact||doc?.counts?.subject_alternative_only!==subject)bad('evidence tier count mismatch');
 return errors;
}
function loadSnapshot(){
 const dir=path.join(__dirname,'parts'),parts=Array.from({length:8},(_,i)=>JSON.parse(fs.readFileSync(path.join(dir,String(i+1).padStart(2,'0')+'.json'),'utf8')));
 return parts.flatMap(p=>p.images);
}
if(require.main===module){
 const doc=JSON.parse(fs.readFileSync(path.join(__dirname,'forrestal_primary_20261030.json'),'utf8'));
 const errors=verifyForrestal(doc,loadSnapshot());
 console.log(JSON.stringify({valid:errors.length===0,errors},null,2));
 if(errors.length)process.exitCode=1;
}
module.exports={isSafeRecord,verifyForrestal,loadSnapshot};
