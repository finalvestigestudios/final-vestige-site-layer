'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const data=require('./scotch_cap_418_catalog_date_conflict_20261108.json');
const clean=()=>JSON.parse(JSON.stringify(data));
function safe(d){
 const c=d.candidate_records;
 return d.schema==='fv-scotch-cap-418-chronology-conflict-v1'&&d.image_key==='418:2'&&
  d.exact_published_original_src==='https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg'&&
  d.direct_original_origin_http_status===null&&d.direct_original_guest_browser_http_status===null&&
  d.earlier_external_retriever_wrapper_status===403&&d.earlier_wrapper_is_origin_http===false&&
  d.earlier_wrapper_is_guest_browser===false&&d.visitor_source_broken===null&&
  Array.isArray(c)&&c.length===2&&
  c.every(x=>x.original_pixel_width===null&&x.original_pixel_height===null&&
   x.origin_image_http_status===null&&x.exact_same_image_proven===false&&
   x.rights_review==='HOLD'&&x.reproduction_or_cache_authorized===false)&&
  d.conflict.status==='UNRESOLVED_CROSS_CATALOG_EVENT_DATE'&&d.conflict.noaa_year===1964&&
  d.conflict.uscg_museum_year===1946&&d.conflict.noaa_exact_image_identity_unknown===true&&
  d.conditional_derivative.max_width_px===960&&d.conditional_derivative.no_upscale===true&&
  d.conditional_derivative.output_width_px===null&&d.conditional_derivative.output_height_px===null&&
  Object.values(d.permission).every(x=>x===false)&&d.production_repairs===0;
}
test('unaltered archival conflict record is safe',()=>assert.equal(safe(clean()),true));
for(const [label,mut] of [
 ['invented visitor 404',d=>d.direct_original_guest_browser_http_status=404],
 ['wrapper 403 called origin',d=>d.earlier_wrapper_is_origin_http=true],
 ['wrapper 403 called browser',d=>d.earlier_wrapper_is_guest_browser=true],
 ['fake identical photograph proof',d=>d.candidate_records[0].exact_same_image_proven=true],
 ['invented original dimensions',d=>d.candidate_records[0].original_pixel_width=960],
 ['rights cleared without review',d=>d.candidate_records[1].rights_review='APPROVED'],
 ['automatic cache',d=>d.candidate_records[0].reproduction_or_cache_authorized=true],
 ['date discrepancy hidden',d=>d.conflict.status='RESOLVED'],
 ['NOAA 1964 silently changed',d=>d.conflict.noaa_year=1946],
 ['unsafe upscale geometry',d=>d.conditional_derivative.no_upscale=false],
 ['invented derivative output',d=>d.conditional_derivative.output_width_px=960],
 ['unapproved CMS write',d=>d.permission.published_post_edit=true],
 ['unexpected repair claim',d=>d.production_repairs=1],
 ['original image drift',d=>d.exact_published_original_src='https://example.org/other.jpg']
])test(label+' must fail closed',()=>{
 const d=clean();mut(d);assert.equal(safe(d),false);
});
