'use strict';
// Offline media source/reuse gate; not a browser collector and never modifies WordPress.
const EXPECTED=[
['1484:0','https://drive.google.com/thumbnail?id=1V8rMf0ovXiJbJLLq77uLwfMHghlH7sMM&sz=w1600','google_drive_thumbnail',null,null],
['1484:1','https://upload.wikimedia.org/wikipedia/commons/9/9c/New_London_School_before_explosion.webp','commons_direct',[960,685],[960,685]],
['1484:2','https://upload.wikimedia.org/wikipedia/commons/3/3c/New_London_School_explosion.jpg','commons_direct',[760,609],[760,609]],
['1484:3','https://upload.wikimedia.org/wikipedia/commons/9/95/New_London_School_Explosion_Memorial.jpg','commons_direct',[3840,2160],[960,540]]
];
function validate(a){
 let e=[];const check=(x,m)=>{if(!x)e.push(m)};
 if(!a||typeof a!=='object'||Array.isArray(a))return ['not an object'];
 check(a.schema==='fv-podcast-1484-source-crosswalk-v1'&&a.date==='2026-11-06','schema/date');
 check(a.post_type==='page'&&a.page_id===1484&&a.page_url==='https://finalvestige.com/podcast/the-textbook-found-open-in-the-ruins/','page identity');
 check(a.source_page_census_blob==='460644e0228412b38f3e9e6e3a1508e02e47f539'&&a.article_cohort_excluded===true,'independent page cohort');
 check(a.actual_browser_available===false&&a.reported_42_visitor_broken===null&&a.measured_76_percent_transfer_reduction===null&&a.requested_width_is_transfer_bytes===false,'no unsupported browser/weight claims');
 for(const f of ['production_fixed','wordpress_writes','third_party_copies','third_party_caches','spend_usd'])check(a[f]===0,'unsafe operation '+f);
 if(!Array.isArray(a.images)||a.images.length!==4)return [...e,'four slots required'];
 let keys=new Set();
 a.images.forEach((v,i)=>{
  if(!v||typeof v!=='object'){e.push('missing image '+i);return}
  let [key,url,klass,native,preview]=EXPECTED[i];
  check(!keys.has(v.slot),'duplicate '+i);keys.add(v.slot);
  check(v.slot===key&&v.src===url&&v.source_class===klass,'exact source '+i);
  check(typeof v.alt==='string'&&v.alt.length>10,'missing contextual ALT '+i);
  check(v.width===null&&v.height===null&&v.source_html_markup_width_attribute===null&&v.source_html_markup_height_attribute===null,'HTML dimensions unknown '+i);
  check(v.browser_http===null&&v.visitor_natural_width===null&&v.visitor_wire_bytes===null&&v.visitor_broken===null,'invented visitor evidence '+i);
  check(v.rights==='HOLD_ITEM_LEVEL'&&v.rights_review_complete===false&&v.rehost_allowed===false&&v.wordpress_write_allowed===false&&v.staging_approved===false,'rights/publication hold '+i);
  check(v.same_binary_verified===false&&v.visual_parity_verified===false,'binary/visual identity unknown '+i);
  check(JSON.stringify(v.catalog_native_pixels)===JSON.stringify(native)&&JSON.stringify(v.conditional_960_no_upscale_pixels)===JSON.stringify(preview),'catalog geometry '+i);
  check(typeof v.historical_parity_note==='string'&&v.historical_parity_note.length>15,'historical identity '+i);
  if(native){let [w,h]=native,[pw,ph]=preview;check(pw<=960&&pw<=w&&ph<=h&&Math.abs(pw*h-ph*w)<=Math.max(w,h),'no-upscale/crop '+i)}
  if(i===0)check(v.source_catalog_url.startsWith('https://drive.google.com/file/d/')&&v.priority==='P1'&&v.license_reference===null&&v.rights_condition==='PROVENANCE_AND_REUSE_UNKNOWN','Drive source remains unverified');
  else check(v.source_catalog_url==='https://commons.wikimedia.org/wiki/File:'+['','New_London_School_before_explosion.webp','New_London_School_explosion.jpg','New_London_School_Explosion_Memorial.jpg'][i],'Commons catalog '+i);
  if(i===1||i===2)check(v.rights_condition.includes('PD_US')&&v.license_reference?.includes('Commons public-domain-US'),'US public-domain caveat '+i);
  if(i===3)check(v.rights_condition.includes('CC_BY_SA_2_0')&&v.license_reference==='https://creativecommons.org/licenses/by-sa/2.0/'&&v.credit_proposal?.includes('QuesterMark'),'CC BY-SA conditions');
 });
 return e;
}
if(typeof module!=='undefined')module.exports={validate,EXPECTED};
if(typeof require==='function'&&require.main===module){
 const fs=require('node:fs');if(process.argv.length!==3){console.error('Usage: node validate_podcast_1484_20261106.cjs AUDIT.json');process.exit(2)}
 const e=validate(JSON.parse(fs.readFileSync(process.argv[2],'utf8')));
 console.log(e.length?JSON.stringify({ok:false,errors:e}):'PASS: podcast source and rights gate');if(e.length)process.exitCode=1;
}
