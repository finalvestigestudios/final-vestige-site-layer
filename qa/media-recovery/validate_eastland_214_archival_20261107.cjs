'use strict';
const PIN = [
  "https://cdn.loc.gov/service/pnp/ggbain/19600/19622v.jpg",
  "https://commons.wikimedia.org/wiki/Special:Redirect/file/Wreck_of_the_Eastland,_Chicago,_1915.jpg",
  "https://commons.wikimedia.org/wiki/Special:Redirect/file/EastlandKenosha.jpg",
  "https://commons.wikimedia.org/wiki/Special:Redirect/file/Helen_Repa_Eastland_Disaster_photo.png?width=1280",
  "https://cdn.loc.gov/service/pnp/ggbain/19600/19623v.jpg",
  "https://commons.wikimedia.org/wiki/Special:Redirect/file/Photograph_of_The_Eastland_(upside_down)_on_Chicago_River,_Chicago._-_NARA_-_281841.jpg?width=1280"
];
function verify(a) {
  const errors=[];
  const fail=s=>errors.push(s);
  if (!a || a.schema_version!=='fv.media-eastland-214.v1'||a.post_id!==214) return {pass:false,errors:['schema/post mismatch']};
  if (a.wp_read?.reference_count!==6||a.wp_read?.read_only!==true||a.wp_read?.all_inline_img_tags_lack_explicit_dimensions!==true) fail('wp record');
  if (a.inventory?.historical_posts!==61||a.inventory?.historical_inline_images!==355||a.inventory?.historical_external_origin_refs!==288)fail('cohort');
  if (a.performance?.guest_browser_measured!==false||a.performance?.reduced_transfer_76_percent_measured!==false||a.performance?.reported_42_broken_guest_verified!==false||a.performance?.wire_bytes!==null||a.performance?.source_optimization_claim!==false)fail('unsubstantiated performance');
  if (a.performance?.large_wp_originals_over_1_5MiB!==13||a.performance?.large_wp_originals_storage_bytes!==43522829)fail('storage census');
  for(const k of ['wordpress_writes','image_downloads_or_copies','media_cached','home_design_changes','spend_usd'])if(a.production?.[k]!==0)fail('production side effect '+k);
  if(!Array.isArray(a.slots)||a.slots.length!==6) return {pass:false,errors:[...errors,'six slots required']};
  const keys=new Set();
  for(let i=0;i<6;i++){
    const s=a.slots[i],c=s?.authoritative_candidate||{}, b=s?.actual_browser||{},n=c.original_master_px,d=c.derivative_960_px;
    if(!s||s.key!==`214:${i}`||s.slot!==i||keys.has(s.key)||s.stored_source_url!==PIN[i]||!s.stored_source_url.startsWith('https://'))fail('slot identity '+i);
    keys.add(s?.key);
    if(!s?.stored_alt||s.stored_html_width!==null||s.stored_html_height!==null||s.wp_post_modified!=='2026-11-02T21:39:34')fail('stored HTML '+i);
    if(s?.retriever?.method!=='web.open'||s?.retriever?.observed!=='viewer_inaccessible'||s?.retriever?.origin_http_status!==null||s?.retriever?.origin_content_type!==null)fail('retriever evidence '+i);
    if(b.verified!==false||Object.keys(b).some(k=>k!=='verified'&&b[k]!==null))fail('fabricated browser '+i);
    if(!c.catalog_url?.startsWith('https://')||!c.identity||!c.credit||!c.rights_note||c.relationship!=='catalog match by identifier or Commons file title, not tested binary pixel match')fail('provenance '+i);
    if(s?.rights_review_complete!==false||s?.source_binary_verified!==false||s?.visual_parity_verified!==false||s?.can_cache!==false||s?.can_upload_wp!==false||s?.can_rewrite_block!==false)fail('unsafe publication '+i);
    if(n===null&&d!==null)fail('invented geometry '+i);
    if(n!==null){
      if(!Number.isInteger(n.width)||n.width<=0||!Number.isInteger(n.height)||n.height<=0)fail('native dimensions '+i);
      else {
        const w=Math.min(960,n.width),h=Math.round(n.height*w/n.width);
        if(!d||d.width!==w||d.height!==h||d.width>n.width||d.height>n.height+1||d.width>960||d.status!==(n.width<960?'no_upscale_keep_original':'conditional_by_catalog'))fail('unsafe resizing '+i);
      }
    }
    if(i===2&&(n?.width!==475||n?.height!==381))fail('tug native 475x381');
    if(i===5&&(n?.width!==3000||n?.height!==2402))fail('NARA native');
    if(i===4&&!c.source_note?.includes('1910'))fail('1910 chronology caution');
    if(i===3&&!c.source_note?.includes('4 August 1915'))fail('Helen Repa publication date');
    if(i===5&&!c.source_note?.includes('after the rescue/recovery'))fail('NARA chronology');
  }
  return {pass:errors.length===0,errors};
}
if(require.main===module){
 const fs=require('node:fs');
 try{const r=verify(JSON.parse(fs.readFileSync(process.argv[2],'utf8')));console.log(JSON.stringify(r));if(!r.pass)process.exitCode=1;}catch(e){console.error(e.message);process.exitCode=2;}
}
module.exports={verify};
