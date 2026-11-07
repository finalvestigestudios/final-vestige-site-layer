'use strict';
// Offline read-only safety gate; no network, asset downloads or WordPress writes.
const fs=require('node:fs');
const { URL }=require('node:url');
function validate(d){
  const e=[];
  if(d?.schema!=='fv.media.hebgen407.source_and_catalog.v1'||d.post_id!==407) e.push('identity');
  if(!Array.isArray(d.images)||d.images.length!==8) return ['eight_rows_required'];
  const s=d.status_summary||{},p=d.performance||{},r=d.restrictions||{};
  if(s.source_urls_checked!==8||s.viewer_rendered_eventually!==7||s.retriever_unsupported_type!==1) e.push('counts');
  if(s.confirmed_guest_browser_broken!==null||s.claimed_42_broken_verified!==false||s.claim_76_percent_measured!==false) e.push('browser_claims');
  if(p.historic_post_cohort!==61||p.historic_source_image_refs!==355||p.later_post_cohort!==66||p.later_source_image_refs!==361||p.oversized_wp_originals_stored_bytes!==43522829||p.visitor_image_transfer_bytes!==null||p.measured_savings_pct!==null) e.push('performance_claims');
  if(!r.no_wordpress_writes||!r.no_media_downloads_or_cache||!r.no_image_derivatives_generated||!r.no_production_release||!r.no_rights_assumptions||r.max_preview_width_px!==960||!r.no_upscale) e.push('release_controls');
  const slots=new Set(),urls=new Set();let rend=0,unsupported=0;
  for(const [i,x] of d.images.entries()){
    if(x.slot!=='407:'+i||slots.has(x.slot))e.push('slot_'+i);
    slots.add(x.slot);
    try {const u=new URL(x.source_url);if(u.protocol!=='https:'||u.hostname!=='d9-wret.s3.us-west-2.amazonaws.com'||!u.pathname.startsWith('/assets/palladium/production/s3fs-public/'))e.push('source_host_'+i)}catch{e.push('bad_url_'+i)}
    if(urls.has(x.source_url))e.push('duplicate_url_'+i);urls.add(x.source_url);
    try {const u=new URL(x.primary_record_url);if(u.protocol!=='https:'||u.hostname!=='www.usgs.gov'||!u.pathname.startsWith('/media/images/'))e.push('catalog_'+i)}catch{e.push('catalog_'+i)}
    if(x.source_inventory_blob!=='48e1ebf07207e948ba5802e714eb39659d2e1c1d')e.push('unpinned_'+i);
    const v=x.viewer||{};
    if(v.date!=='2026-11-07'||!v.viewer_ref||v.origin_http_status!==null||v.guest_browser_http_status!==null||v.guest_decode_ok!==null||v.wire_bytes!==null)e.push('viewer_scope_'+i);
    if(v.observation==='unsupported_content_type'){
      unsupported++;if(i!==1||v.retriever_wrapper_error_code!==400)e.push('wrapper_mismatch_'+i)
    }else if(['rendered_image','rendered_on_official_catalog_retry'].includes(v.observation)){
      rend++;if(v.retriever_wrapper_error_code!==null)e.push('fake_wrapper_'+i);
    }else e.push('invalid_observation_'+i);
    if(x.rights_gate!=='HOLD'||x.exact_binary_identity_confirmed!==false||x.allowed_to_download_or_cache!==false||x.wp_media_id!==null||x.native_source_geometry_px!==null||x.approved_960px_derivative_px!==null)e.push('rights_or_pixels_'+i);
    if(!x.catalog_rights_note?.startsWith('catalog_public_domain;'))e.push('rights_source_'+i);
    const st=x.stored_declared_geometry_px,prev=x.provisional_resize_from_stored_geometry_px;
    if(st===null){if(prev!==null)e.push('invented_geometry_'+i)}
    else if(!Array.isArray(st)||st.length!==2||st[0]!==1024||!Number.isInteger(st[1])||st[1]<1||!Array.isArray(prev)||prev[0]!==960||prev[1]!==Math.round(st[1]*960/1024))e.push('preview_arithmetic_'+i);
  }
  if(rend!==7||unsupported!==1)e.push('outcomes');
  if(d.images[2].catalog_rights_note.indexOf('W_B_Hall')===-1||d.images[3].catalog_rights_note.indexOf('Mrs_Steven_W_Nile')===-1||d.images[7].catalog_rights_note.indexOf('Mike_Poland_USGS')===-1)e.push('credits');
  if(d.images[6].note.indexOf('1970')===-1||d.images[7].note.indexOf('2023')===-1)e.push('chronology');
  return e;
}
if(require.main===module){const p=process.argv[2]; if(!p){process.stderr.write('usage: node validate_hebgen_407_20261107.cjs audit.json\n');process.exit(2)}const e=validate(JSON.parse(fs.readFileSync(p,'utf8')));process.stdout.write(JSON.stringify({ok:e.length===0,errors:e})+'\n');if(e.length)process.exit(1)}
module.exports={validate};
