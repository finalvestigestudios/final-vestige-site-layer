'use strict';
// Offline, fail-closed audit validator. Does not fetch/rehost images or change WordPress.
const fs = require('node:fs');
const same = (a, b) => a === b;
const hash40 = x => typeof x === 'string' && /^[a-f0-9]{40}$/.test(x);
const url = x => typeof x === 'string' && /^https:\/\/[^/?#\s]+\//.test(x);
function validate(a) {
  const errors=[];
  const req=(condition,code)=>{if(!condition) errors.push(code);};
  req(a?.schema==='fv-piri-1917-matched-first-party-candidate-v1','schema');
  req(a?.observed_on==='2026-11-23','observed_on');
  req(a?.post?.id===1917&&a.post.url==='https://finalvestige.com/2026/11/02/piri-reis-map/'&&
      a.post.wp_modified==='2026-11-18T20:47:15','post_identity_and_revision');
  req(a?.post?.stats_period_30d_end==='2026-11-22'&&a.post.views_30d===44&&a.post.views_7d===7,
      'traffic_snapshot');
  req(a?.post?.campaign_attribution_verified===false&&a.post.guest_mobile_tested===false&&
      a.post.guest_desktop_tested===false,'unverified_attribution_or_browsers');
  const s=a?.source_provenance;
  req(s?.live_guest_image_http===null&&s.mobile_lcp_ms===null&&s.mobile_cls===null&&
      s.mobile_inp_ms===null&&s.mobile_screenshot_sha256===null&&s.cold_image_transfer_bytes===null,
      'unmeasured_mobile_and_wire');
  req(Array.isArray(a?.images)&&a.images.length===2,'slot_count');
  const expected=[
    {slot:'1917:0',file:'Piri%20reis%20world%20map%2001.jpg',w:1964,h:2619,bytes:7422309,
      catalog:'https://commons.wikimedia.org/wiki/File:Piri_reis_world_map_01.jpg',sha1:'a8575fa2b790f06e2d5851680afb3178b539465b',targetH:1280},
    {slot:'1917:1',file:'Cantino%20planisphere%20%281502%29.jpg',w:10643,h:4998,bytes:37739048,
      catalog:'https://commons.wikimedia.org/wiki/File:Cantino_planisphere_(1502).jpg',sha1:'288013759c999fd32679c94db5eea5ea41861bfd',targetH:451}
  ];
  (a?.images||[]).forEach((im,i)=>{
    const x=expected[i]; if(!x) return;
    req(im.slot===x.slot&&im.current_src===`https://commons.wikimedia.org/wiki/Special:Redirect/file/${x.file}?width=1280`&&
        im.catalog===x.catalog,'exact_slot_and_origin_'+i);
    req(im.current_width_attribute===null&&im.current_height_attribute===null&&im.current_srcset===null,
        'markup_risk_not_assumed_fixed_'+i);
    req(im.catalog_original_width===x.w&&im.catalog_original_height===x.h&&
        im.catalog_original_bytes===x.bytes&&im.catalog_sha1===x.sha1&&hash40(im.catalog_sha1),
        'catalog_custody_'+i);
    req(im.proposed_max_width===960&&im.proposed_proportional_height===x.targetH&&
        Math.abs(im.proposed_proportional_height-960*x.h/x.w)<=0.5,'proportional_960_'+i);
    req(typeof im.catalog_rights==='string'&&/PDM-1\.0/.test(im.catalog_rights)&&
        im.same_binary_sha256_verified===false&&im.same_crop_and_pixels_verified===false&&
        im.item_rights_editorially_cleared===false&&im.wordpress_write_approved===false,
        'rights_identity_hold_'+i);
    if(i===0){
      req(im.wp_existing_media_id===2640&&
          im.wp_media_url==='https://finalvestige.com/wp-content/uploads/2026/11/piri-reis-world-map-01.jpg'&&
          im.wp_media_width===x.w&&im.wp_media_height===x.h&&im.wp_original_stored_bytes===x.bytes,
          'first_party_asset_custody');
      req(url(im.wp_existing_virtual_768_url)&&
          im.wp_existing_virtual_768_url==='https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/11/piri-reis-world-map-01.jpg?fit=768%2C1024&ssl=1'&&
          im.wp_existing_virtual_width===768&&im.wp_existing_virtual_height===1024&&
          im.may_reuse_existing_wp_media_only_after_verification===true,'real_virtual_variant');
    }else{
      req(im.wp_existing_media_id===null&&im.wp_media_search_cantino_count===0,
          'cantino_no_assumed_existing_asset');
    }
  });
  const r=a?.release;
  req(r?.decision==='HOLD_FOR_INDEPENDENT_MOBILE_AND_RIGHTS_REVIEW'&&
      r.status_42_reported_guest_failures_verified===false&&r.sitewide_76_percent_wire_savings_verified===false,
      'release_hold');
  req(r?.historical_posts===61&&r.historical_inline===355&&r.newer_posts===66&&r.newer_inline===361&&
      r.oversize_originals_over_1500000_bytes===20&&r.oversize_stored_total_bytes===64385752&&
      r.oversize_visitor_download_confirmed===false,'cohort_and_storage_not_network');
  req(r?.files_downloaded===0&&r.production_wp_writes===0&&r.new_wp_media_uploads===0&&
      r.homepage_visual_changes===0&&r.new_browser_collector===false&&r.draft_pr===2747&&r.site_qa_pr===154,
      'zero_writes_and_qa_ownership');
  return errors;
}
if(require.main===module){const file=process.argv[2]||require('node:path').join(__dirname,'piri_1917_existing_wp_reuse_20261123.json');
  const problems=validate(JSON.parse(fs.readFileSync(file,'utf8')));
  if(problems.length){console.error(problems.join('\n'));process.exitCode=1;}else console.log('PASS — existing Piri media reuse candidate; rights/mobile HOLD');
}
module.exports={validate};
