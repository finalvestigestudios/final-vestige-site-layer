'use strict';
const fs=require('node:fs'),path=require('node:path');
const IDS=['NH 42273','80-G-227987','NH 84498','NH 45641','80-G-344565','80-G-227991','80-G-227989'];
const TAILS=['nh-42273-uss-tang--ss-306-.html','80-g-227987-uss-tang--ss-306-.html','NH-84498.html','NH-45641.html','80-g-344565.html','80-G-227991.html','80-G-227989.html'];
function validate(m, inv) {
 const errors=[],bad=s=>errors.push(s);
 if(m?.schema!=='fv-tang-nhhc-custody-20261031-v1'||m.post_id!==274||m.total_images!==7||m.external_images!==7)bad('scope');
 if(m?.wordPress_read_only_verification?.stored_src_matches!==7||m?.wordPress_read_only_verification?.stored_alt_matches!==7||m?.wordPress_read_only_verification?.published!==true)bad('CMS source proof');
 if(m.visitor_broken_count!==null||m.reported_sitewide_42_broken_verified!==false||m.reported_sitewide_76pct_savings_verified!==false||m.production_repairs!==0||m.rights_approval!==false)bad('fabricated claims');
 const expected=inv?.images?.filter(x=>x.post_id===274).sort((a,b)=>a.slot-b.slot)||[];
 if(expected.length!==7||!Array.isArray(m.records)||m.records.length!==7){bad('missing image slots');return errors;}
 for(let i=0;i<7;i++){
  const r=m.records[i],e=expected[i];if(!r){bad('missing record '+i);continue;}
  if(r.key!==e.key||r.slot!==i||r.source_url!==e.source_url||r.alt!==e.alt||r.source_kind!==e.source_kind)bad('wrong source/ALT '+i);
  if(r.primary_catalog_id!==IDS[i]||!r.primary_catalog_url?.startsWith('https://www.history.navy.mil/')||!r.primary_catalog_url?.endsWith(TAILS[i]))bad('wrong Navy record '+i);
  if(!r.credit?.includes('U.S. Navy')||!r.credit?.includes(IDS[i]))bad('credit '+i);
  if(!r.chronology_crop_caution||r.chronology_crop_caution.length<30||!r.identity_evidence||r.identity_evidence.length<60)bad('chronology/crop/provenance '+i);
  const d=r.catalog_geometry,t=r.conditional_derivative;
  if(![d?.width,d?.height,t?.width,t?.height].every(x=>Number.isInteger(x)&&x>0)){bad('dimensions '+i);continue;}
  const w=Math.min(960,d.width),h=Math.round(w*d.height/d.width);
  if(t.width!==w||t.height!==h||t.width>960||t.no_upscale!==true||t.width>d.width||t.height>d.height)bad('upscale/distortion '+i);
  if(!d.basis||d.basis.length<15)bad('dimension basis '+i);
  if(r.rights_status!=='HOLD'||r.wordpress_upload_authorized!==false||r.original_pixels_verified!==false||r.source_sha256!==null)bad('rights/hash '+i);
  for(const k of ['guest_http_status','guest_current_src','guest_mime','guest_bytes','guest_natural_width','guest_screenshot'])if(r[k]!==null)bad('invented browser observation '+i+':'+k);
 }
 return errors;
}
module.exports={validate};
if(require.main===module){const m=JSON.parse(fs.readFileSync(path.join(__dirname,'tang_274_nhhc_20261031.json'),'utf8'));const inv=JSON.parse(fs.readFileSync(path.join(__dirname,'parts/04.json'),'utf8'));const e=validate(m,inv);if(e.length){console.error(e.join('\n'));process.exitCode=1;}else console.log('PASS Tang 274 archive and rights gates');}
