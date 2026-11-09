'use strict';
function validate(a, census, parts) {
 const fail=x=>{throw Error(x)};
 if(!a||a.schema!=='fv-mann-gulch-source-audit-v1'||a.post_id!==213||!Array.isArray(a.rows)||a.rows.length!==7)fail('schema/rows');
 if(a.pinned_sources?.sitewide_288_blob!=='92a904c8da1ace1f972b2f00adf1a4847dde2b99'||a.pinned_sources?.post_snapshot_part06_blob!=='0f3dfe398a76838049cebba7cb773d5c5a0c8c69')fail('source pins');
 const truth=census?.rows?.filter(x=>x.post_id===213).sort((x,y)=>x.slot.localeCompare(y.slot));
 const p=parts?.images?.filter(x=>x.post_id===213).sort((x,y)=>x.key.localeCompare(y.key));
 if(truth?.length!==7||p?.length!==7)fail('frozen sources missing');
 const expectedViews=['IMAGE_DISPLAYED','IMAGE_DISPLAYED','IMAGE_DISPLAYED','VIEWER_INTERNAL_ERROR','IMAGE_DISPLAYED','IMAGE_DISPLAYED','IMAGE_DISPLAYED'];
 const r=[...a.rows].sort((x,y)=>x.slot.localeCompare(y.slot));
 for(let i=0;i<7;i++){
   const z=r[i],key='213:'+i;
   if(z.slot!==key||truth[i].slot!==key||p[i].key!==key||z.stored_url!==truth[i].stored_url||z.stored_url!==p[i].source_url||z.post_url!==p[i].post_url||z.source_host!==truth[i].origin_host)fail('source identity');
   if(z.frozen_alt!==p[i].alt||z.frozen_html_width_px!==p[i].width_px||z.frozen_html_height_px!==p[i].height_px)fail('frozen ALT/geometry');
   if(z.external_viewer_observation!==expectedViews[i])fail('web tool status');
   if([z.origin_http_status,z.guest_browser_http_status,z.guest_current_src,z.guest_natural_dimensions,z.guest_wire_bytes,z.visitor_broken].some(x=>x!==null))fail('fabricated browser evidence');
   if(z.duplicate_exact_stored_url_of!==(i===6?'213:2':null))fail('duplicate annotation');
   if(z.binary_identity_verified!==false||z.republication_rights_cleared!==false||!z.release||Object.values(z.release).length!==4||Object.values(z.release).some(x=>x!==false))fail('unauthorized media change');
   if(!z.authoritative_source_or_catalog_url?.startsWith('https://')||!z.rights_caveat||!z.visual_integrity)fail('provenance');
   if(i===3){if(JSON.stringify(z.catalog_native_px)!=='[1457,972]'||JSON.stringify(z.conditional_960px_size)!=='[960,640]')fail('Commons catalog geometry')}
   else if(z.catalog_native_px!==null||z.conditional_960px_size!==null)fail('invented geometry');
 }
 if(r[2].stored_url!==r[6].stored_url||new Set(r.map(x=>x.stored_url)).size!==6)fail('duplicate/source count');
 if(!r[5].rights_caveat.includes('STOP:')||!r[5].rights_caveat.includes('newyorktimes'))fail('NYT rights gate');
 if(JSON.stringify(a.counts)!==JSON.stringify({external_slots:7,unique_external_urls:6,viewer_rendered_slots:6,viewer_error_slots:1,guest_confirmed_broken:0}))fail('counts');
 if(a.sitewide_baseline?.percent_76_wire_reduction_measured!==false||a.sitewide_baseline?.oversized_originals_storage_bytes!==47096779||a.sitewide_baseline?.unverified_claim_broken!==42)fail('false savings');
 return {pass:true,slots:7,unique_urls:6,guest_statuses_verified:0};
}
module.exports={validate};
