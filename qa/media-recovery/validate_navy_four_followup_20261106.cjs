'use strict';
function validateManifest(m) {
 const e=[];
 const fail=(x)=>e.push(x);
 const ids=['274:2','280:1','280:4','288:2'];
 const catalog={'274:2':'NH 88447','280:1':'NH 75559','280:4':'NH 68705','288:2':'UG 21-01.02'};
 const exactPostUrls={
  '274:2':'https://finalvestige.com/2026/08/19/twenty-four-feet-from-air-uss-tang/',
  '280:1':'https://finalvestige.com/2026/08/19/the-sledgehammers-broke-first-uss-pueblo/',
  '280:4':'https://finalvestige.com/2026/08/19/the-sledgehammers-broke-first-uss-pueblo/',
  '288:2':'https://finalvestige.com/2026/08/19/the-bearing-was-right-honda-point/'
 };
 const expected={
  '274:2':'/navy-torpedoes/',
  '280:1':'/pueblo-iii/',
  '280:4':'/banner-ii/',
  '288:2':'/ug-21-01-02-mare-island-naval-radio/'
 };
 if(m.schema!=='fv-media-navy-unmapped-four-v1') fail('schema');
 if(m.basis?.previous_15_row_blob_sha!=='04d63548b39a311ee43a64f72383e0d5cd099e3d') fail('pin');
 if(!Array.isArray(m.records)||m.records.length!==4) fail('count');
 if(m.summary?.page_caption_candidates!==2||m.summary?.slug_identified!==1||m.summary?.subject_only!==1||m.summary?.production_fixes!==0)fail('summary');
 if(m.catalog_review?.real_browser_capture_available!==false||m.catalog_review?.original_42_broken_proven!==false||m.catalog_review?.measured_wire_reduction_percent!==null)fail('claim');
 if(m.release?.rights_review!=='HOLD'||m.release?.binary_download!==false||m.release?.third_party_caching!==false||m.release?.wordpress_production_writes!==false||m.release?.homepage_design_changes!==false||m.release?.no_automatic_photo_swap!==true)fail('release');
 for(const key of ids){
   const rows=Array.isArray(m.records)?m.records.filter(r=>r.key===key):[];
   if(rows.length!==1){fail('key:'+key);continue;}
   const r=rows[0];
   if(r.post_id!==Number(key.split(':')[0]))fail('post_id:'+key);
   if(r.post_url!==exactPostUrls[key])fail('post_url:'+key);
   if(r.candidate_catalog_id!==catalog[key])fail('catalog_id:'+key);
   if(!r.original_src?.startsWith('https://www.history.navy.mil/')||!r.original_src.includes(expected[key]))fail('original_url:'+key);
   if(!r.candidate_catalog_url?.startsWith('https://www.history.navy.mil/'))fail('catalog_url:'+key);
   if(!r.parent_page_url?.startsWith('https://www.history.navy.mil/'))fail('parent_url:'+key);
   if(!r.post_url?.startsWith('https://finalvestige.com/')||typeof r.original_alt!=='string'||r.original_alt.length<20)fail('article_alt:'+key);
   if(r.original_origin_http_status!==null||r.original_guest_browser_http!==null||r.visitor_broken!==null||r.decoded_pixels!==null||r.cold_transfer_bytes!==null)fail('unverified_browser:'+key);
   if(r.candidate_binary_identity_verified!==false||r.rights_review!=='HOLD_ITEM_LEVEL'||r.rehost_or_cache_permission!==false||r.wordpress_upload_authorized!==false||r.wordpress_post_edit_authorized!==false)fail('rights:'+key);
   if(r.max_preview_width!==960||r.no_upscale!==true)fail('preview_policy:'+key);
   if(key==='280:4'&&(r.match_basis!=='SAME_SHIP_ONLY'||r.identity_confidence!=='SUBJECT_ALTERNATIVE_NOT_SAME_PHOTOGRAPH'))fail('subject_only');
   if(key==='288:2'&&r.match_basis!=='CATALOG_ID_IN_ORIGINAL_URL_SLUG')fail('slug_id');
   if(['274:2','280:1'].includes(key)&&r.match_basis!=='NAVY_PARENT_PAGE_CAPTION_TO_CATALOG')fail('caption:'+key);
   if(!r.catalog_master){if(r.conditional_960!==null)fail('unknown_pixels:'+key);}
   else{const {width,height}=r.catalog_master;
     if(!Number.isInteger(width)||!Number.isInteger(height)||width<=0||height<=0)fail('catalog_dimensions:'+key);
     if(!r.conditional_960||r.conditional_960.width!==Math.min(960,width)||r.conditional_960.height!==Math.round(height*Math.min(960,width)/width)||r.conditional_960.width>width)fail('output_dimensions:'+key);
   }
 }
 return {ok:e.length===0,errors:e};
}
if(typeof module!=='undefined')module.exports={validateManifest};
if(typeof require!=='undefined'&&typeof module!=='undefined'&&require.main===module) {
 const fs=require('node:fs'),path=require('node:path');
 const file=process.argv[2]||path.join(__dirname,'navy_four_catalog_followup_20261106.json');
 const result=validateManifest(JSON.parse(fs.readFileSync(file,'utf8')));
 process.stdout.write(JSON.stringify(result)+'\n');
 if(!result.ok)process.exitCode=1;
}
