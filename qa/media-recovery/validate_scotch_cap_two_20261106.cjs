'use strict';
// Offline fail-closed provenance and 960px geometry gate. NO network or WordPress access.
const TRUSTED=['https://www.history.uscg.mil/','https://media.defense.gov/','https://nationalcoastguardmuseum.org/'];
const ORIGINALS={
 '418:1':'https://media.defense.gov/2021/Mar/30/2002610812/1920/1080/0/210330-G-DE713-0002.JPG',
 '418:2':'https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg'
};
const CANDIDATES={
 '418:1':'https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/',
 '418:2':'https://nationalcoastguardmuseum.org/wp-content/uploads/2023/08/5_-Scotch_Cap_debris2_1946-600x463.jpg'
};
function validate(a){
 const errors=[],check=(b,m)=>{if(!b)errors.push(m);};
 if(!a||typeof a!=='object')return {ok:false,errors:['missing audit']};
 check(a.schema==='fv-scotch-cap-two-v1','schema');
 check(a.observed_date==='2026-11-06','date');
 check(a.post_id===418,'post');
 check(a.baseline&&a.baseline.legacy_post_count===61&&a.baseline.legacy_img_src_count===355&&a.baseline.current_post_count===66&&a.baseline.current_img_src_count===361,'post census');
 check(a.baseline&&a.baseline.alleged_broken_count===42&&a.baseline.visitor_verified_broken_count===null&&a.baseline.proposed_savings_pct===76&&a.baseline.measured_savings_pct===null,'unverified claims');
 check(a.baseline&&a.baseline.oversize_wp_originals===13&&a.baseline.oversize_storage_bytes===43522829,'storage baseline');
 check(Array.isArray(a.sources)&&a.sources.length>=3,'primary sources');
 if(Array.isArray(a.sources))for(const s of a.sources){check(typeof s.url==='string'&&s.url.startsWith('https://'),'source https');check(s.retrieved_date===a.observed_date,'source date');}
 const rows=a.targets;
 check(Array.isArray(rows)&&rows.length===2,'two exact targets');
 if(!Array.isArray(rows))return {ok:false,errors};
 check(new Set(rows.map(x=>x&&x.key)).size===2,'unique slots');
 for(const r of rows){
  if(!r||typeof r!=='object'){errors.push('missing row');continue;}
  const k=r.key, c=r.candidate||{},t=r.original_retrieval||{},rights=r.rights||{};
  check(Object.hasOwn(ORIGINALS,k),'allowed slot');
  check(r.post_id===418,'post key');
  check(r.published_src===ORIGINALS[k],'published src exact');
  check(t.tool==='web.open'&&t.observed==='wrapper_403'&&t.observed_date===a.observed_date,'retrieval evidence');
  for(const f of ['origin_http','visitor_browser_http','visitor_broken','natural_width','natural_height','cold_wire_bytes'])check(t[f]===null,'unverified browser/origin '+k+' '+f);
  check(c.url===CANDIDATES[k],'pinned candidate exact');
  check(TRUSTED.some(h=>c.url.startsWith(h)),'candidate host');
  check(c.binary_identical===null,'no invented binary match');
  check(c.max_preview_width===960&&c.no_upscale===true,'960 max no upscale');
  check(rights.item_review==='HOLD_BEFORE_COPY','rights release hold');
  if(k==='418:1'){
   check(r.archival_identifier==='VIRIN 210330-G-DE713-0002.JPG','Pettit catalog id');
   check(/Pettit/.test(r.subject)&&/NOT tsunami debris/.test(r.subject),'portrait not debris');
   check(c.same_photo_by_catalog_id===true&&c.native_dimensions===null&&c.proposed_dimensions===null,'portrait geometry unmeasured');
   check(rights.item_public_domain_notice===true,'catalog PD notice');
  }
  if(k==='418:2'){
   check(/remains/.test(r.subject)&&/NOT Anthony Pettit/.test(r.subject),'debris not portrait');
   check(c.filename_correspondence===true,'same photo filename family');
   check(c.render_test==='web image rendered from link 25 on Museum article','publisher displayed image');
   check(Array.isArray(c.available_image_dimensions)&&c.available_image_dimensions[0]===600&&c.available_image_dimensions[1]===463,'observed 600x463');
   check(Array.isArray(c.proposed_dimensions)&&c.proposed_dimensions[0]===600&&c.proposed_dimensions[1]===463,'no 600px enlargement');
   check(c.native_dimensions===null,'original master size unknown');
   check(rights.item_public_domain_notice===null,'museum derivative not automatically cleared');
  }
  const d=c.proposed_dimensions,n=c.available_image_dimensions||c.native_dimensions;
  if(d){check(d.every((z)=>Number.isInteger(z)&&z>0),'integer geometry');check(d[0]<=960,'not wider than 960');if(n)check(d[0]<=n[0]&&d[1]<=n[1],'not upscaled');}
 }
 const release=a.release||{};
 for(const f of ['wordpress_production_writes','image_downloads','image_caches','production_repairs','additional_spend_usd','homepage_changes'])check(release[f]===0,'no production action '+f);
 check(release.approval_to_publish===false&&release.site_qa_collector_duplicated===false,'no release/duplicate collector');
 return {ok:errors.length===0,errors,rows_checked:rows.length};
}
if(typeof module!=='undefined')module.exports={validate};
if(typeof require==='function'&&require.main===module){
 const fs=require('node:fs');const filename=process.argv[2];
 if(!filename){console.error('Usage: node validate_scotch_cap_two_20261106.cjs audit.json');process.exit(2)}
 const result=validate(JSON.parse(fs.readFileSync(filename,'utf8')));
 console.log(JSON.stringify(result,null,2));if(!result.ok)process.exitCode=1;
}
