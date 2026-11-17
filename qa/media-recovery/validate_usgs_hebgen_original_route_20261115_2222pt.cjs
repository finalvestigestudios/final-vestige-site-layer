'use strict';
// Read-only, offline evidence verifier. DOES NOT make requests or modify WordPress.
const EXPECTED = Object.freeze({
  slot:'407:1',
  catalog:'https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959',
  official:'https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/img7535.jpg',
  origin:'https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg',
  jetpack:'https://i0.wp.com/d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg?ssl=1'
});
const hold=(s)=>{throw Error('HOLD: '+s);};
function validate(d) {
  if(!d || d.schema!=='fv-media-p0-official-original-route-v1' || d.audit_date_pt!=='2026-11-15') hold('schema/date');
  const w=d.wordpress, a=d.official, r=d.review_derivative, b=d.baselines, g=d.guardrails;
  if(!w || w.post_id!==407 || w.slot!==EXPECTED.slot ||
    w.post_url!=='https://finalvestige.com/2026/08/20/the-lake-wasnt-there-yesterday-hebgen/' ||
    w.alt!=='Fresh fault scarp near Hebgen Lake produced by the August 1959 earthquake.' ||
    w.view_src!==EXPECTED.jetpack || w.authored_origin!==EXPECTED.origin) hold('authored/view exact image identity');
  for(const field of ['guest_http_status','guest_current_src','guest_decode_ok','guest_natural_width','guest_natural_height','guest_transfer_bytes','confirmed_broken'])
    if(w[field]!==null) hold('unverified guest image '+field);
  if(!a || a.agency!=='US Geological Survey' || a.catalog!==EXPECTED.catalog ||
    a.original!==EXPECTED.official || a.photographer!=='J. R. Stacy' ||
    a.rights_catalog_statement!=='Public Domain.' || a.filename_match!==true ||
    a.same_pixel_hash_proven!==false || a.same_frame_review_complete!==false ||
    a.native_width!==null || a.native_height!==null || a.rights_review_complete!==false) hold('USGS provenance/rights/pixel identity');
  if(!Array.isArray(d.route_observations) || d.route_observations.length!==4) hold('route coverage');
  const truth=[
    ['official_catalog',EXPECTED.catalog,'public-web-text-reader','catalog_visible'],
    ['official_original',EXPECTED.official,'public-web-image-reader','image_rendered'],
    ['authored_origin',EXPECTED.origin,'public-web-document-reader','unsupported_binary_octet_stream'],
    ['wordpress_jetpack_view',EXPECTED.jetpack,'public-web-document-reader','tool_inaccessible']
  ];
  for(let i=0;i<4;i++){const v=d.route_observations[i],t=truth[i];
    if(!v||v.route!==t[0]||v.url!==t[1]||v.method!==t[2]||v.outcome!==t[3]||
      v.http_status!==null||v.guest_browser_status!==null) hold('invented status/route '+i);
  }
  if(!r || r.target_max_width!==960 || r.no_upscaling!==true ||
    r.native_dimensions_verified!==false || r.output_width!==null || r.output_height!==null ||
    r.formula!=='width=min(960,nativeWidth);height=round(nativeHeight*width/nativeWidth)' ||
    r.cache_approved!==false || r.upload_approved!==false || r.production_change_approved!==false ||
    r.cache_location!=='WordPress Media Library staging only after explicit approval') hold('geometry/rehosting safeguards');
  if(!b||b.historical_published_posts!==61||b.historical_image_tags!==355||
    b.current_published_posts!==66||b.current_image_tags!==361||
    b.reported_broken_count!==42||b.guest_confirmed_broken_count!==null||
    b.claimed_wire_reduction_percent!==76||b.measured_wire_reduction_percent!==null||
    b.oversized_wp_originals!==20||b.oversized_storage_bytes!==64385752) hold('unproved claim/baselines');
  if(!g || Object.values(g).length!==7 || Object.values(g).some(n=>n!==0)) hold('unsafe production modification');
  if(typeof d.next_action!=='string'||!d.next_action.includes('Site QA #154 existing collector')) hold('collector ownership');
  return {status:'HOLD_GUEST_BROWSER_AND_PIXEL_RIGHTS',slot:w.slot,official_catalog:a.catalog,
    source_route:a.original,guest_broken:null,guest_http_status:null,upload_approved:false};
}
if(require.main===module){
  try {const fs=require('node:fs');const d=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
    process.stdout.write(JSON.stringify(validate(d))+'\n');
  } catch(e){process.stderr.write(e.message+'\n');process.exitCode=2;}
}
module.exports={validate};
