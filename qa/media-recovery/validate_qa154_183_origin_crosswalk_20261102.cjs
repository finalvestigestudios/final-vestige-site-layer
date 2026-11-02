'use strict';
/**
 * Cross-branch, offline source-count reconciliation for media QA #154/#183.
 * No network, CMS, image fetching, file mutation, or URL rewriting.
 * The Site QA raw per-slot input is NOT in this branch; its historical CSV
 * aggregates are pinned in the ledger with their Git blob SHA.
 */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const EXPECTED = Object.freeze({posts:61, images:355, qaOffsite:286, mediaOffsite:288});
const EXPECTED_QA_CSV_BLOB = '76aa63ffaa299a6e6878edc1b66e637fa6f058ab';
const EXPECTED_DISPUTES = Object.freeze({'291':'291:0','285':'285:1'});
const fail = (errors, condition, reason) => {if (!condition) errors.push(reason);};
function offsiteByStoredUrl(raw) {
  if (typeof raw !== 'string') return null;
  const m = /^https?:\/\/([^/?#]+)(?:\/([^?#]*))?/i.exec(raw);
  if (!m) return null;
  const host = m[1].toLowerCase().replace(/^www\./, '');
  const pathname = m[2] || '';
  if (host === 'finalvestige.com') return false;
  // Jetpack serving a DIFFERENT publisher does not create a first-party asset.
  if (/^i[012]\.wp\.com$/.test(host) && /^finalvestige\.com(?:\/|$)/i.test(pathname)) return false;
  return true;
}
function validateCrosswalk(ledger, parts) {
  const errors = [];
  if (!ledger || !Array.isArray(ledger.rows) || !Array.isArray(ledger.discrepancies)
       || !Array.isArray(parts) || parts.length !== 8) return {ok:false, errors:['invalid_inputs']};
  fail(errors, ledger.schema_version === 1, 'schema_version');
  fail(errors, ledger.kind === 'offline_cross_branch_snapshot_reconciliation_not_live_image_or_browser_audit', 'audit_kind');
  fail(errors, ledger.sources?.site_qa_pr === 154, 'site_qa_pr');
  fail(errors, ledger.sources?.site_qa_aggregate_csv_blob_sha === EXPECTED_QA_CSV_BLOB, 'site_qa_blob_changed');
  fail(errors, ledger.sources?.site_qa_per_image_source_markup_available_here === false, 'per_slot_site_qa_unknown');
  fail(errors, Array.isArray(ledger.sources?.media_recovery_source_part_blob_shas)
       && ledger.sources.media_recovery_source_part_blob_shas.length === 8, 'part_sha_manifest');
  const posts = new Map(), images = new Map();
  for (let index=0; index<parts.length; index++) {
    const batch=parts[index];
    if (!batch || !Array.isArray(batch.posts) || !Array.isArray(batch.images)) {
      errors.push('invalid_part:'+index); continue;
    }
    fail(errors,batch.batch===index+1,'batch_number:'+index);
    for (const p of batch.posts) {
      fail(errors,!posts.has(p.id),'duplicate_post:'+p.id);
      posts.set(p.id,p);
    }
    for (const im of batch.images) {
      fail(errors,!images.has(im.key),'duplicate_image:'+im.key);
      fail(errors,im.key===im.post_id+':'+im.slot,'slot_key:'+im.key);
      const offsite=offsiteByStoredUrl(im.source_url);
      fail(errors,offsite!==null && offsite===['external','wikimedia_redirect'].includes(im.source_kind),'source_kind:'+im.key);
      fail(errors,im.actual_http_status===null && im.broken_in_browser===null,'invented_browser_status:'+im.key);
      images.set(im.key,im);
    }
  }
  fail(errors,posts.size===EXPECTED.posts && images.size===EXPECTED.images,'source_corpus_size');
  fail(errors,ledger.rows.length===EXPECTED.posts,'ledger_post_count');
  const rowIds=new Set();
  let allQaImages=0, allQaOffsite=0, allMediaOffsite=0, allMediaImages=0, delta=0;
  const actualDiff=[];
  for (const row of ledger.rows) {
    fail(errors,!rowIds.has(row.post_id),'duplicate_row:'+row.post_id);rowIds.add(row.post_id);
    const post=posts.get(row.post_id);
    if (!post) {errors.push('unknown_post:'+row.post_id);continue;}
    const matches=[...images.values()].filter(x=>x.post_id===row.post_id);
    const count=matches.length, offsite=matches.filter(x=>offsiteByStoredUrl(x.source_url)).length;
    const qaCount=row.stored_img_src_count_site_qa, qaOffsite=row.offsite_count_site_qa;
    fail(errors,row.post_url===post.url,'row_url:'+row.post_id);
    fail(errors,row.stored_img_src_count_media_recovery===count && count===qaCount,'row_image_count:'+row.post_id);
    fail(errors,Number.isSafeInteger(qaOffsite) && qaOffsite>=0 && qaOffsite<=qaCount,'row_qa_offsite:'+row.post_id);
    fail(errors,row.offsite_count_media_recovery===offsite,'row_offsite:'+row.post_id);
    fail(errors,row.delta_media_minus_qa===offsite-qaOffsite,'row_delta:'+row.post_id);
    if (row.delta_media_minus_qa!==0) actualDiff.push(row);
    allQaImages+=qaCount;allQaOffsite+=qaOffsite;allMediaOffsite+=offsite;allMediaImages+=count;
    delta+=offsite-qaOffsite;
  }
  fail(errors,rowIds.size===posts.size && [...posts.keys()].every(id=>rowIds.has(id)),'post_ids_incomplete');
  const metrics={posts:posts.size,image_slots_media_recovery:allMediaImages,image_slots_site_qa:allQaImages,
    offsite_media_recovery:allMediaOffsite,offsite_site_qa:allQaOffsite,offsite_delta:delta,
    posts_with_mismatch:actualDiff.length,mismatching_external_proxy_slots:2};
  fail(errors,JSON.stringify(metrics)===JSON.stringify(ledger.summary),'summary_recomputed');
  fail(errors,allMediaImages===EXPECTED.images && allQaImages===EXPECTED.images
    && allQaOffsite===EXPECTED.qaOffsite && allMediaOffsite===EXPECTED.mediaOffsite
    && delta===2,'expected_reconciliation');
  fail(errors,actualDiff.length===2 && actualDiff.every(x=>EXPECTED_DISPUTES[x.post_id]),'unexpected_mismatch_posts');
  const disputeIds=new Set();
  for (const dispute of ledger.discrepancies) {
    fail(errors,!disputeIds.has(dispute.post_id),'duplicate_dispute:'+dispute.post_id);
    disputeIds.add(dispute.post_id);
    const row=actualDiff.find(x=>x.post_id===dispute.post_id);
    fail(errors,!!row && dispute.offsite_delta===row.delta_media_minus_qa
      && dispute.media_offsite===row.offsite_count_media_recovery
      && dispute.site_qa_offsite===row.offsite_count_site_qa,'dispute_delta:'+dispute.post_id);
    const candidates=dispute.candidate_slots || [];
    fail(errors,candidates.length===1 && candidates[0]?.image_key===EXPECTED_DISPUTES[dispute.post_id],
      'dispute_slot:'+dispute.post_id);
    for (const c of candidates) {
      const im=images.get(c.image_key);
      fail(errors,!!im && im.post_id===dispute.post_id && im.source_url===c.source_url
        && im.alt===c.stored_alt && im.source_kind===c.source_kind,'dispute_source:'+c.image_key);
      fail(errors,/^https?:\/\/i[012]\.wp\.com\//i.test(c.source_url)
        && !/^https?:\/\/i[012]\.wp\.com\/finalvestige\.com(?:\/|$)/i.test(c.source_url)
        && c.is_first_party_jetpack_proxy===false,'externally_proxied_origin:'+c.image_key);
      fail(errors,c.site_qa_per_slot_classification===null && c.visitor_browser_status===null
        && c.rights_to_cache_confirmed===false && c.automatic_replacement_authorized===false,
        'source_rights_or_browser_overclaim:'+c.image_key);
    }
  }
  fail(errors,disputeIds.size===2,'dispute_count');
  fail(errors,ledger.decision?.status==='UNRESOLVED_RAW_MARKUP_AND_BROWSER_REQUIRED'
    && ledger.decision.prior_42_broken_images_confirmed===false
    && ledger.decision.claimed_76pct_image_weight_reduction_measured===false
    && ledger.decision.production_replacements_applied===0
    && ledger.decision.wordpress_write_authorized===false
    && ledger.decision.caching_authorized===false,'unsafe_recovery_claim');
  return {ok:errors.length===0,errors:[...new Set(errors)],metrics};
}
function loadRepo(root=__dirname) {
  const raw=fs.readFileSync(path.join(root,'qa154_183_origin_count_crosswalk_20261102.json'),'utf8');
  const ledger=JSON.parse(raw),parts=[];
  for (let i=1; i<=8; i++) {
    const data=fs.readFileSync(path.join(root,'parts',String(i).padStart(2,'0')+'.json'));
    const gitBlob=crypto.createHash('sha1').update('blob '+data.length+'\0').update(data).digest('hex');
    if (gitBlob!==ledger.sources.media_recovery_source_part_blob_shas[i-1])
      throw Error('source_part_blob_changed:'+i);
    parts.push(JSON.parse(data.toString('utf8')));
  }
  return {ledger,parts};
}
if (require.main===module) {
  try {const result=validateCrosswalk(...Object.values(loadRepo()));console.log(JSON.stringify(result,null,2));if(!result.ok)process.exitCode=1;}
  catch(e){console.error('MEDIA_CROSSWALK_INPUT_ERROR '+e.message);process.exitCode=2;}
}
module.exports={validateCrosswalk,offsiteByStoredUrl,loadRepo};
