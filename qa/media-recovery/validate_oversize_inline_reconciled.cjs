'use strict';
// Offline source-level crosswalk. Browser statuses and WordPress mutations are OUT OF SCOPE.
function parseImageURL(raw) {
  if (typeof raw !== 'string') return null;
  const m = /^https:\/\/([^/?#]+)(\/[^?#]*)(?:\?([^#]*))?$/.exec(raw);
  if (!m) return null;
  const host = m[1].toLowerCase(), path = m[2], qs = m[3] || '';
  if (host === 'finalvestige.com' && path.startsWith('/wp-content/uploads/') && !qs)
    return {path, method:'exact_first_party_path', source_kind:'first_party'};
  if (host !== 'i0.wp.com' || !path.startsWith('/finalvestige.com/wp-content/uploads/')) return null;
  const fields=qs.split('&').map(s=>s.split('=')), keys=fields.map(x=>x[0]).sort();
  if (fields.length !== 2 || keys.join(',') !== 'fit,ssl') return null;
  const fit=fields.find(x=>x[0]==='fit')?.[1], ssl=fields.find(x=>x[0]==='ssl')?.[1];
  if (!fit || ssl !== '1' || !/^\d{1,4}%2[cC]\d{1,4}$/.test(fit)) return null;
  const parts=decodeURIComponent(fit).split(',').map(Number);
  if (parts.some(n=>n<1 || n>4096)) return null;
  return {path:path.slice('/finalvestige.com'.length),method:'verified_same_origin_jetpack_proxy',source_kind:'jetpack_proxy'};
}
function validate(m, originals, census) {
  const errors=[];
  if(!m || m.schema_version!==1 || !Array.isArray(m.rows) || m.rows.length!==13 ||
     !Array.isArray(originals) || originals.length!==13 || !Array.isArray(census) || census.length!==355 ||
     m.source_census_image_count!==355 || m.source_census_post_count!==61 || m.source_original_count!==13)
    errors.push('invalid_census_or_schema');
  if(!m?.rows || !originals || !census) return {ok:false,errors};
  const orig=new Map(originals.map(r=>[r.media_id,r])), idx=new Map(census.map(i=>[i.key,i]));
  if(orig.size!==13 || idx.size!==355 || new Set(m.rows.map(r=>r.media_id)).size!==13) errors.push('duplicate_identity');
  let total=0,direct=0,jetpack=0,none=0,noSizes=0,heroTotal=0,vasaTotal=0,malboneTotal=0,otherTotal=0;
  const requiredHeroes={39:'34:0',40:'35:0',41:'36:0',42:'37:0',43:'38:0'};
  const requiredVasa={388:'299:1',389:'299:0',382:'299:7'};
  for(const row of m.rows) {
    const o=orig.get(row.media_id);
    if(!o) {errors.push('unknown_media:'+row.media_id);continue;}
    total+=row.original_storage_bytes;
    if(row.original_url!==o.url || row.original_storage_bytes!==o.original_bytes ||
       row.original_width_px!==o.original_width_px || row.original_height_px!==o.original_height_px ||
       row.known_1024_variant_url!==o.existing_wp_1024_variant ||
       JSON.stringify(row.legacy_direct_only_slots)!==JSON.stringify(o.referenced_inline_positions))
       errors.push('original_snapshot:'+row.media_id);
    if(row.wordpress_media_details_verified_20261031!==true) errors.push('missing_cms_readback:'+row.media_id);
    const hero=Object.hasOwn(requiredHeroes,row.media_id), vasa=Object.hasOwn(requiredVasa,row.media_id);
    if(row.wordpress_registered_subsizes===false) noSizes++;
    if(row.wordpress_registered_subsizes!==!hero) errors.push('subsize_record:'+row.media_id);
    const w=Math.min(960,o.original_width_px),h=Math.round(w*o.original_height_px/o.original_width_px);
    if(row.proposed_width_px!==w || row.proposed_height_px!==h ||
       row.no_upscale!==true || row.preserve_aspect_ratio!==true) errors.push('dimensions:'+row.media_id);
    if(row.actual_image_http_status!==null || row.actual_image_transfer_bytes!==null ||
       row.decoded_browser_width_px!==null || row.browser_failed_image!==null ||
       row.original_sha256!==null || row.rights_clearance!==false ||
       row.wordpress_upload_authorized!==false || row.production_post_change_authorized!==false ||
       row.production_write_made!==false) errors.push('unverified_or_unauthorized:'+row.media_id);
    const expected=census.filter(i=> {
      const a=parseImageURL(i.source_url),b=parseImageURL(o.url);
      return a && b && a.path===b.path && a.source_kind===i.source_kind;
    });
    const hits=row.inline_matches;
    if(!Array.isArray(hits) || hits.length!==expected.length) {errors.push('missing_inline:'+row.media_id);continue;}
    for(const hit of hits) {
      const actual=idx.get(hit.image_key), parsed=parseImageURL(hit.stored_url);
      if(!actual || !parsed || hit.stored_url!==actual.source_url ||
         hit.post_id!==actual.post_id || hit.post_url!==actual.post_url ||
         hit.post_title!==actual.post_title || hit.source_kind!==actual.source_kind ||
         hit.match_method!==parsed.method ||
         !expected.some(i=>i.key===hit.image_key)) errors.push('false_alias:'+row.media_id);
    }
    if(new Set(hits.map(h=>h.image_key)).size!==hits.length) errors.push('duplicate_slot:'+row.media_id);
    if(hero) {
      heroTotal+=row.original_storage_bytes;
      if(hits.length!==1 || hits[0].image_key!==requiredHeroes[row.media_id] ||
         row.featured_post_verified!==Number(requiredHeroes[row.media_id].split(':')[0]) ||
         row.source_editor_html_width_px!==1024 || row.source_editor_html_height_px!==576 ||
         row.review_priority!=='P1_featured_source_only_no_registered_sizes')
        errors.push('featured_hero:'+row.media_id);
    } else if(vasa) {
      vasaTotal+=row.original_storage_bytes;
      if(hits.length!==1 || hits[0].image_key!==requiredVasa[row.media_id] ||
         hits[0].match_method!=='verified_same_origin_jetpack_proxy' ||
         row.review_priority!=='P2_inline_variant_catalogued_no_browser_evidence' ||
         row.featured_post_verified!==(row.media_id===389?299:null))
        errors.push('vasa_proxy:'+row.media_id);
    } else if(row.media_id===1257 || row.media_id===1258) malboneTotal+=row.original_storage_bytes;
    else otherTotal+=row.original_storage_bytes;
    if(!hero && !vasa && row.featured_post_verified!==null) errors.push('unverified_featured:'+row.media_id);
    if(!hero && !vasa && (row.source_editor_html_width_px!==null || row.source_editor_html_height_px!==null))
      errors.push('invented_editor_size:'+row.media_id);
    if(hits.length) {
      if(row.review_priority!==(hero?'P1_featured_source_only_no_registered_sizes':'P2_inline_variant_catalogued_no_browser_evidence'))
        errors.push('wrong_priority:'+row.media_id);
      if(hits[0].match_method==='verified_same_origin_jetpack_proxy') jetpack++;
      else direct++;
    } else {
      none++;
      if(row.review_priority!=='P3_no_inline_match_in_61_post_snapshot') errors.push('wrong_non_inline:'+row.media_id);
    }
  }
  const s=m.summary||{};
  if(total!==43522829 || total!==m.source_original_storage_bytes ||
     direct!==7 || jetpack!==3 || none!==3 || noSizes!==5 ||
     heroTotal!==13267538 || vasaTotal!==13318311 || malboneTotal!==10352064 || otherTotal!==6584916 ||
     s.originals_gt_1_5mib!==13 || s.inline_media_records!==10 || s.inline_exact_first_party!==7 ||
     s.inline_same_origin_jetpack_proxy!==3 || s.no_inline_match_in_61_post_census!==3 ||
     s.featured_5_no_registered_sizes!==5 || s.featured_5_original_storage_bytes!==heroTotal ||
     s.vasa_3_original_storage_bytes!==vasaTotal || s.malbone_2_original_storage_bytes!==malboneTotal ||
     s.non_inline_3_original_storage_bytes!==otherTotal) errors.push('counts_or_bytes');
  if(s.visitor_transfer_bytes!==null || s.confirmed_browser_broken_images!==null ||
     s.measured_weight_reduction_percent!==null || m.reported_broken_images_42_browser_verified!==false ||
     m.reported_76pct_weight_saving_measured!==false) errors.push('fabricated_claim');
  const evidence=m.featured_post_evidence;
  if(!Array.isArray(evidence) || evidence.length!==6 || new Set(evidence.map(x=>x.media_id)).size!==6)
    errors.push('post_readback_evidence');
  else for(const item of evidence) {
    if(item.status!=='publish' || !String(item.permalink).startsWith('https://finalvestige.com/') ||
       (item.media_id===389 ? (item.post_id!==299 || item.uses_jetpack_proxy!==true) :
        (item.post_id!==Number(requiredHeroes[item.media_id]?.split(':')[0]) ||
         item.media_sizes_empty!==true || item.source_img_html_width_px!==1024 ||
         item.source_img_html_height_px!==576 || item.editor_html_src_matches_original!==true)))
      errors.push('post_readback_evidence:'+item.media_id);
  }
  return {ok:errors.length===0,errors,source_census:census.length,media_originals:originals.length,
          matched_inline_media:direct+jetpack,exact_inline:direct,jetpack_inline:jetpack,not_inline:none,
          unsized_featured_media:noSizes,original_storage_bytes:total};
}
if(typeof require!=='undefined' && typeof module!=='undefined' && require.main===module){
  const fs=require('node:fs'),path=require('node:path');
  const load=f=>JSON.parse(fs.readFileSync(path.join(__dirname,f),'utf8'));
  const result=validate(load('oversize_inline_reconciled_20261031.json'),
      load('oversize_originals_20261030.json'),
      Array.from({length:8},(_,i)=>load('parts/'+String(i+1).padStart(2,'0')+'.json')).flatMap(x=>x.images));
  console.log(JSON.stringify(result,null,2)); if(!result.ok) process.exitCode=1;
}
if(typeof module!=='undefined') module.exports={parseImageURL,validate};
