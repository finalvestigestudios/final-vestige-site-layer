'use strict';
/**
 * Offline, fail-closed paired comparison of existing FV guest-browser probe JSON.
 * No network access, media downloads, WordPress writes, or third-party dependencies.
 * A result is a single laboratory CDP transfer-byte delta, never a field or 76% site-wide claim.
 */
const fs = require('node:fs');
const {createHash}=require('node:crypto');
const positive = v => Number.isSafeInteger(v) && v > 0;
const validId = v => typeof v === 'string' && v.length > 0 && v.length <= 128 && !/\s/.test(v);
const url = v => { try { const u = new URL(v); return u.protocol === 'https:' && u.hostname === 'finalvestige.com' ? u.href : null; } catch { return null; } };
const netUrl = v => { try { const u = new URL(v); return ['https:', 'http:'].includes(u.protocol) ? u.href : null; } catch { return null; } };
const unique = a => [...new Set(a)];
const add = (reasons, s) => reasons.push(s);
function inspectRun(run, label, reasons) {
  const out = new Map();
  if (!run || typeof run !== 'object' || Array.isArray(run)) { add(reasons, label+':missing_run'); return out; }
  if (run.status !== 'complete_browser_image_census' || run.image_census_coverage?.complete !== true ||
      run.image_census_coverage?.confirmed_broken_count !== 0 ||
      run.confirmed_broken_count !== 0) add(reasons, label+':census_or_image_failure_unverified');
  if (!Array.isArray(run.pages) || !positive(run.requested_pages) ||
      run.pages.length !== run.requested_pages || run.verified_pages !== run.requested_pages)
    add(reasons, label+':page_count_incomplete');
  if (!['390x844', '1440x900'].includes(run.viewport) || !['priority', 'all'].includes(run.mode))
    add(reasons, label+':probe_configuration_unverified');
  if (!run.run_profile || run.run_profile.cache_disabled !== true ||
      run.run_profile.service_worker_bypassed !== true)
    add(reasons, label+':uncached_run_not_proven');
  if (!validId(run.browser_product)) add(reasons, label+':browser_version_missing');
  for (const p of Array.isArray(run.pages) ? run.pages : []) {
    const id = p?.post_id;
    if (!positive(id) || out.has(id)) { add(reasons, label+':duplicate_or_invalid_post'); continue; }
    out.set(id, { page:p, keys:new Set(), computed:null });
    const row = out.get(id);
    if (!url(p.url) || p.page_result !== 'inspected_browser' ||
        p.scroll_coverage?.complete !== true || p.scroll_coverage?.state !== 'full_height_scanned' ||
        p.image_census?.complete !== true || p.image_census?.confirmed_broken_count !== 0 ||
        p.confirmed_broken_count !== 0)
      add(reasons, label+':page_or_scroll_unverified:'+id);
    if (p.article_wire_evidence_complete !== true ||
        (Array.isArray(p.article_wire_evidence_errors) && p.article_wire_evidence_errors.length) ||
        p.article_wire_attribution_mode !== 'strict_cdp_request_id')
      add(reasons, label+':article_wire_evidence_unverified:'+id);
    if (!Array.isArray(p.stored_images) || !positive(p.stored_image_count) ||
        p.stored_images.length !== p.stored_image_count || !Array.isArray(p.network_images)) {
      add(reasons, label+':missing_image_slots_or_network:'+id);continue;
    }
    const byId = new Map(), bound = new Set(); let sum = 0;
    for (const n of p.network_images) {
      if (!validId(n?.request_id) || byId.has(n.request_id)) {
        add(reasons, label+':duplicate_or_missing_cdp_request_id:'+id);continue;
      }
      byId.set(n.request_id,n);
    }
    for (const slot of p.stored_images) {
      const key=slot?.image_key;
      if (typeof key !== 'string' || !new RegExp('^'+id+':\\d+$').test(key) || row.keys.has(key)) {
        add(reasons, label+':duplicate_or_invalid_slot_key:'+id); continue;
      }
      row.keys.add(key);
      if (slot.result !== 'loaded_in_probe_browser' || slot.verified_broken_in_browser !== false ||
          !['exact_url_or_jetpack_origin','exact_url_unique_alt'].includes(slot.match) ||
          slot.current_src_identity_verified !== true || slot.network_final_identity_verified !== true ||
          slot.loaded_network_proof_verified !== true || slot.redirected_image_identity_unverified === true ||
          slot.complete !== true || !positive(slot.natural_width) || !positive(slot.natural_height) || slot.http_status !== 200 ||
          !/^image\//i.test(slot.response_mime_type||'') || !positive(slot.transfer_bytes) ||
          !netUrl(slot.stored_url) || !netUrl(slot.current_src) || !netUrl(slot.request_url)) {
        add(reasons, label+':unverified_or_broken_image:'+key);continue;
      }
      const n = byId.get(slot.request_id);
      if (!validId(slot.request_id) || !n || netUrl(slot.request_url) !== netUrl(n.url) ||
          n.status !== 200 || !/^image\//i.test(n.mime_type||'') ||
          !positive(n.encoded_data_length) || n.encoded_data_length !== slot.transfer_bytes ||
          n.error || n.was_cached !== false || n.from_disk_cache !== false || n.from_service_worker !== false) {
        add(reasons, label+':uncached_cdp_request_mismatch:'+key);continue;
      }
      if (!bound.has(slot.request_id)) {bound.add(slot.request_id);sum += n.encoded_data_length;}
    }
    // The same image URL could have a preloaded/retried transfer. Unbound duplicate
    // transfers must not be silently excluded from an 'article-only' byte claim.
    const sources = new Set(p.stored_images.flatMap(s => [netUrl(s?.request_url),netUrl(s?.current_src)].filter(Boolean)));
    for (const n of p.network_images) {
      if (bound.has(n?.request_id)) continue;
      if ([n?.url,...(Array.isArray(n?.url_aliases)?n.url_aliases:[])].some(v => sources.has(netUrl(v))))
        add(reasons, label+':unbound_same_photo_request:'+id);
    }
    if (bound.size !== p.matched_article_network_requests ||
        !positive(sum) || sum !== p.article_image_wire_bytes_total)
      add(reasons, label+':article_byte_total_not_reconciled:'+id);
    row.computed=sum;
  }
  return out;
}
function compareColdImageWire(before, after) {
  const reasons=[];
  const b=inspectRun(before,'baseline',reasons),a=inspectRun(after,'candidate',reasons);
  if (before?.viewport !== after?.viewport || before?.mode !== after?.mode ||
      before?.browser_product !== after?.browser_product ||
      JSON.stringify(before?.run_profile) !== JSON.stringify(after?.run_profile))
    add(reasons,'unmatched_browser_viewport_or_cache_configuration');
  if (b.size !== a.size) add(reasons,'paired_post_set_incomplete');
  let baseline=0,candidate=0;
  const paired=[];
  for (const [id, br] of b) {
    const ar=a.get(id);
    if (!ar) {add(reasons,'candidate_post_missing:'+id);continue;}
    const bkeys=[...br.keys].sort(),akeys=[...ar.keys].sort();
    const pairedSourceSetMatches=url(br.page.url) === url(ar.page.url) &&
      JSON.stringify(bkeys)===JSON.stringify(akeys);
    if (!pairedSourceSetMatches) add(reasons,'post_url_or_image_slot_set_changed:'+id);
    if (!positive(br.computed) || !positive(ar.computed))add(reasons,'paired_bytes_unknown:'+id);
    baseline+=br.computed||0;candidate+=ar.computed||0;
    if (!pairedSourceSetMatches) continue;
    const bs=new Map(br.page.stored_images.map(s=>[s.image_key,s]));
    const as=new Map(ar.page.stored_images.map(s=>[s.image_key,s]));
    // This is only a geometry and caption guard, NOT visual/historical equivalence.
    for (const k of bkeys) {
      const x=bs.get(k), y=as.get(k);
      if (typeof x.rendered_alt !== 'string' || typeof y.rendered_alt !== 'string' ||
          x.rendered_alt !== y.rendered_alt)
        add(reasons,'rendered_alt_changed_or_missing:'+k);
      if (!positive(x.natural_width) || !positive(x.natural_height) ||
          !positive(y.natural_width) || !positive(y.natural_height)) {
        add(reasons,'intrinsic_geometry_missing:'+k);continue;
      }
      const ratioDrift=Math.abs(x.natural_width*y.natural_height-y.natural_width*x.natural_height)/
        (x.natural_width*y.natural_height);
      if(ratioDrift>0.01)add(reasons,'image_crop_or_aspect_changed:'+k);
      if(y.natural_width>x.natural_width || y.natural_height>x.natural_height)
        add(reasons,'candidate_intrinsic_upscale_requires_review:'+k);
      if(y.natural_width<Math.min(320,x.natural_width) ||
          y.natural_height<Math.min(160,x.natural_height))
        add(reasons,'candidate_intrinsic_too_small:'+k);
    }
    paired.push({post_id:id,image_slots:bkeys.length,baseline_cdp_bytes:br.computed,candidate_cdp_bytes:ar.computed,
      sources:bkeys.map(k=>({image_key:k,baseline_stored_url:bs.get(k).stored_url,
        candidate_stored_url:as.get(k).stored_url,baseline_current_src:bs.get(k).current_src,
        candidate_current_src:as.get(k).current_src,baseline_http_status:bs.get(k).http_status,
        candidate_http_status:as.get(k).http_status,baseline_request_id:bs.get(k).request_id,
        candidate_request_id:as.get(k).request_id,baseline_encoded_bytes:bs.get(k).transfer_bytes,
        candidate_encoded_bytes:as.get(k).transfer_bytes,
        per_slot_bytes_not_additive_when_request_ids_shared:true}))});
  }
  const errors=unique(reasons);
  if (errors.length) return {schema:'fv-cold-image-wire-pair-v1',state:'HOLD',reasons:errors,
    paired_post_count:null,baseline_cdp_bytes:null,candidate_cdp_bytes:null,
    reduction_percent:null,at_least_76_percent_in_this_pair:null,
    sitewide_76_percent_claim_permitted:false,production_repair_claim_permitted:false,visual_parity_verified:false};
  const reduction=(baseline-candidate)*100/baseline;
  return {schema:'fv-cold-image-wire-pair-v1',state:'LAB_PAIR_MEASURED',reasons:[],
    viewport:before.viewport,mode:before.mode,post_count:paired.length,
    paired_post_count:paired.length,paired,baseline_cdp_bytes:baseline,
    candidate_cdp_bytes:candidate,reduction_percent:Math.round(reduction*100)/100,
    at_least_76_percent_in_this_pair:reduction>=76,
    sitewide_76_percent_claim_permitted:false,production_repair_claim_permitted:false,visual_parity_verified:false,
    limitations:'One cold lab CDP pair, not field traffic or a validated 61-post multi-run site-wide result. Geometry and ALT checks are only a safety screen: pixel-level scene/caption/rights review and any WordPress release require separate approval.'};
}
if (require.main===module) {
 const files=process.argv.slice(2);
 if (files.length!==2) {console.error('Usage: node compare_cold_image_wire_v1.cjs BEFORE.json AFTER.json');process.exitCode=2;}
 else try {
  const raw=files.map(f=>fs.readFileSync(f));
  const result=compareColdImageWire(JSON.parse(raw[0].toString('utf8')),JSON.parse(raw[1].toString('utf8')));
  result.input_sha256={baseline:createHash('sha256').update(raw[0]).digest('hex'),
    candidate:createHash('sha256').update(raw[1]).digest('hex')};
  process.stdout.write(JSON.stringify(result,null,2)+'\n');
  if(result.state!=='LAB_PAIR_MEASURED')process.exitCode=2;
 } catch(e) {console.error('INPUT_ERROR '+String(e.message||e));process.exitCode=2;}
}
module.exports={compareColdImageWire};
