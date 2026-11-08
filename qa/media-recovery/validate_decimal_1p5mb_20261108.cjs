'use strict';
/**
 * Offline source-metadata validation only: neither media size nor WordPress subsize
 * metadata establishes HTTP status, visitor transfer weight, copyright or permission.
 */
function validate(a) {
  const problems=[];
  const bad=(condition,reason)=>{if(condition)problems.push(reason);};
  bad(a?.schema!=='fv-wp-originals-decimal-threshold-v1','invalid_schema');
  bad(a?.wordpress_image_media_count!==119,'incomplete_wordpress_media_inventory');
  bad(a?.decimal_threshold_bytes!==1500000||a?.binary_threshold_bytes!==1572864,'threshold_definition_changed');
  bad(a?.decimal_large_original_count!==15||a?.decimal_large_original_storage_bytes!==47096779,'decimal_count_or_bytes_wrong');
  bad(a?.binary_large_original_count!==14||a?.binary_large_original_storage_bytes!==45553777,'binary_count_or_bytes_wrong');
  bad(JSON.stringify(a?.decimal_only_media_ids)!=='[1714]','single_threshold_gap_not_preserved');
  bad(a?.reported_42_broken_guest_verified!==false||a?.reported_76_percent_wire_savings_measured!==false||
      a?.measured_reduction!==null,'unverified_broken_or_transfer_claim');
  bad(a?.production_repairs!==0||a?.wordpress_writes!==0||a?.media_binary_downloads!==0||a?.spend_usd!==0,'production_or_spend_claim');
  const rows=Array.isArray(a?.rows)?a.rows:[];
  bad(rows.length!==15,'wrong_number_of_large_originals');
  const ids=new Set();let decSum=0,binSum=0,binCount=0,gapCount=0;
  for(const x of rows){
    bad(!Number.isSafeInteger(x?.media_id)||ids.has(x.media_id),'duplicate_or_invalid_media_id');
    ids.add(x.media_id);
    bad(!Number.isSafeInteger(x.original_bytes)||x.original_bytes<=1500000,'below_decimal_threshold');
    bad(x.over_1p5_decimal_MB!==true||x.over_1p5_binary_MiB!==(x.original_bytes>1572864),'misclassified_threshold');
    bad(!Number.isSafeInteger(x.width)||x.width<1||!Number.isSafeInteger(x.height)||x.height<1,'bad_original_dimensions');
    const w=Math.min(960,x.width),h=Math.round(x.height*w/x.width);
    bad(x.conditional_preview_max_width!==w||x.conditional_preview_height!==h,'bad_960_max_dimensions_or_upscale');
    bad(typeof x.original_url!=='string'||!/^https:\/\/finalvestige\.com\/wp-content\/uploads\/[^?#]+$/.test(x.original_url),'unverified_source_url');
    bad(!['image/png','image/jpeg'].includes(x.mime_type),'invalid_media_mime');
    bad(x.original_http_status!==null||x.guest_http_status!==null||x.guest_decode!==null||
        x.guest_wire_bytes!==null,'fabricated_network_observation');
    bad(x.rights_review!=='HOLD'||x.download_authorized!==false||
        x.derivative_authorized!==false||x.wp_write_authorized!==false,'rights_or_write_hold_bypassed');
    decSum+=x.original_bytes;
    if(x.original_bytes>1572864){binSum+=x.original_bytes;binCount++;}
    else gapCount++;
  }
  bad(decSum!==a?.decimal_large_original_storage_bytes||binSum!==a?.binary_large_original_storage_bytes||
      binCount!==a?.binary_large_original_count||gapCount!==1,'derived_aggregate_mismatch');
  const m=rows.find(x=>x.media_id===1714),h=a?.halifax;
  bad(!m||m.original_bytes!==1543002||m.width!==1280||m.height!==1280||
      m.original_url!=='https://finalvestige.com/wp-content/uploads/2026/10/halifax-explosion-map.png',
      'halifax_map_identity_changed');
  bad(h?.media_id!==1714||h?.post_id!==269||h?.post_status!=='publish'||
      h?.post_url!=='https://finalvestige.com/2026/08/18/the-watch-lost-its-hands-halifax-explosion/'||
      h?.posted_original_src!==m?.original_url||h?.exact_raw_gutenberg_img_src!==true||
      h?.wordpress_image_block_id_matches!==true||h?.stored_size_slug_large!==true,
      'halifax_post_and_stored_block_mismatch');
  bad(h?.media_list_1024_proxy_url!=='https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/10/halifax-explosion-map.png?fit=1024%2C1024&ssl=1'||
      h?.media_get_1024_variant_url!=='https://finalvestige.com/wp-content/uploads/2026/10/halifax-explosion-map-1024x1024.png'||
      h?.metadata_urls_disagree!==true||h?.confirmed_binary_subsize_exists!==false,
      'wordpress_subsize_metadata_ambiguity_lost');
  bad(h?.independent_copyright_permission!=='HOLD'||h?.labels_legibility!=='UNVERIFIED'||
      h?.conditional_preview!=='960x960 no crop; visual/rights check before derivative',
      'halifax_rights_or_legibility_hold');
  return {pass:problems.length===0,problems:[...new Set(problems)]};
}
if(require.main===module){
 const fs=require('node:fs'),filename=process.argv[2];
 if(!filename){console.error('Usage: node validate_decimal_1p5mb_20261108.cjs AUDIT.json');process.exitCode=2;}
 else try{const v=validate(JSON.parse(fs.readFileSync(filename,'utf8')));console.log(JSON.stringify(v));if(!v.pass)process.exitCode=2;}
 catch(e){console.error('INVALID_AUDIT '+e.message);process.exitCode=2;}
}
module.exports={validate};
