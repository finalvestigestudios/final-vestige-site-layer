'use strict';
/* Source-only, fail-closed reconciliation. Does not request URLs, download media, or write WordPress. */
const fs = require('node:fs');
const path = require('node:path');
const VALID_POST_IDS = [218,217,216,215,214,213,211,190];
function validate(a, registry) {
  const errors = [], fail = (message) => errors.push(message);
  if (!a || a.schema !== 'fv-media-live-part06-49-v1') return {ok:false,errors:['invalid_schema']};
  if (!registry || !Array.isArray(registry.rows)) return {ok:false,errors:['missing_source_registry']};
  if (a.provenance?.frozen_part_blob !== '0f3dfe398a76838049cebba7cb773d5c5a0c8c69') fail('frozen_provenance_changed');
  if (a.provenance?.registry_blob !== '4965a862f7de7de46c1f4a1e26f3ca70a8c38805') fail('registry_provenance_changed');
  const stats={posts:0,images:0,source_equal:0,alt_equal:0,missing_both_dimensions:0,both_dimensions:0,partial_dimensions:0,srcset_count:0,commons_redirects:0,other_external:0,first_party:0,catalog_candidates:0,conditional_960_candidates:0,guest_http_statuses_confirmed:0};
  const registryMap = new Map(registry.rows.map(x => [x.slot,x]));
  const seen = new Set();
  if (!Array.isArray(a.posts)) fail('posts_missing');
  else {
    stats.posts=a.posts.length;
    const ids=a.posts.map(x=>x.post_id);
    if (ids.join(',') !== VALID_POST_IDS.join(',')) fail('post_cohort_or_order_changed');
    a.posts.forEach(p=>{
      if(p.status!=='publish'||p.live_image_count!==p.frozen_image_count||p.live_url!==p.post_url) fail('post_invalid:'+p.post_id);
      if(!String(p.post_url).startsWith('https://finalvestige.com/'))fail('post_url_invalid:'+p.post_id);
    });
  }
  if (!Array.isArray(a.rows)) fail('rows_missing');
  else {
    stats.images=a.rows.length;
    for(const x of a.rows) {
      if(seen.has(x.slot)) fail('duplicate_slot:'+x.slot);seen.add(x.slot);
      if(!VALID_POST_IDS.includes(x.post_id)||!x.slot.startsWith(String(x.post_id)+':'))fail('foreign_post_slot:'+x.slot);
      const ref=registryMap.get(x.slot);
      if(!ref||ref.stored_url!==x.source_url)fail('frozen_registry_src_mismatch:'+x.slot);
      if(x.source_url!==x.live_source_url||x.source_equal!==true)fail('live_src_mismatch:'+x.slot);
      else stats.source_equal++;
      if(x.original_alt!==x.live_alt||x.alt_equal!==true)fail('live_alt_mismatch:'+x.slot);
      else stats.alt_equal++;
      if(x.host!==ref?.origin_host) fail('origin_host_mismatch:'+x.slot);
      try {
        const u=new URL(x.source_url);
        if(u.protocol!=='https:'||!u.hostname)fail('source_url_not_https:'+x.slot);
      } catch {fail('invalid_src_url:'+x.slot);}
      const w=x.html_width_px,h=x.html_height_px;
      if(w===null&&h===null)stats.missing_both_dimensions++;
      else if(Number.isSafeInteger(w)&&w>0&&Number.isSafeInteger(h)&&h>0)stats.both_dimensions++;
      else {stats.partial_dimensions++;fail('invalid_dimension_pair:'+x.slot);}
      if(x.literal_srcset!==false){stats.srcset_count++;fail('unverified_srcset:'+x.slot);}
      const kind=x.source_url.includes('Special:Redirect/file')?'commons_redirect':
        x.source_url.startsWith('https://finalvestige.com/')?'first_party':'offsite_external';
      if(x.origin_kind!==kind) fail('source_kind_mismatch:'+x.slot);
      if(kind==='commons_redirect')stats.commons_redirects++;
      else if(kind==='first_party')stats.first_party++;
      else stats.other_external++;
      if(!Array.isArray(x.archive_candidates))fail('candidate_array_missing:'+x.slot);
      else {
        if(x.archive_candidates.length)stats.catalog_candidates++;
        if(x.archive_candidates.some(c=>Array.isArray(c.conditional_960px)))stats.conditional_960_candidates++;
        for(const c of x.archive_candidates) {
          if(c.item_rights_cleared===true||c.rights_cleared===true||c.exact_image_match_verified===true)fail('candidate_unapproved_release:'+x.slot);
          if(c.conditional_960px!=null) {
            const d=c.conditional_960px;
            if(!Array.isArray(d)||d.length!==2||!d.every(v=>Number.isSafeInteger(v)&&v>0)||d[0]>960)
              fail('unsafe_960_derivative:'+x.slot);
          }
        }
      }
      if(!Array.isArray(x.historical_retriever_wrappers))fail('wrapper_evidence_missing:'+x.slot);
      if(x.guest_origin_http_status!==null||x.guest_current_src!==null||x.guest_decoded_px!==null||x.guest_transferred_bytes!==null||x.guest_image_failure_confirmed!==null||x.guest_CLS!==null)fail('fabricated_guest_evidence:'+x.slot);
      if(x.rights_cleared!==false||x.exact_image_match_verified!==false||x.cache_authorized!==false||x.wordpress_upload_authorized!==false||x.post_rewrite_authorized!==false||x.conditional_960px_variants_only!==true)fail('unsafe_release_flag:'+x.slot);
    }
  }
  if(seen.size!==49||stats.images!==49||stats.posts!==8||stats.source_equal!==49||stats.alt_equal!==49)fail('frozen_count_invariant');
  for(const [k,v] of Object.entries(stats)){if(a.counts?.[k]!==v)fail('count_mismatch:'+k);}
  if(a.policy?.historical_42_broken_browser_verified!==false||a.policy?.claimed_76_percent_network_weight_saving_measured!==false||a.policy?.no_wordpress_changes!==true||a.policy?.no_binary_downloads!==true||a.policy?.site_qa_collector_owned_by_pr!==154)fail('scope_or_claim_invariant');
  return {ok:errors.length===0,errors,counts:stats};
}
if(require.main===module){
  const auditPath=process.argv[2]||path.join(__dirname,'live_part06_8posts_49_images_20261112.json');
  const registryPath=process.argv[3]||path.join(__dirname,'coverage_288_exact_pr1703_20261110.json');
  const result=validate(JSON.parse(fs.readFileSync(auditPath,'utf8')),JSON.parse(fs.readFileSync(registryPath,'utf8')));
  console.log(JSON.stringify(result,null,2));
  if(!result.ok)process.exitCode=1;
}
module.exports={validate};
