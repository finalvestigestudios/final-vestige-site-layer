'use strict';
// Offline schema/custody gate for the independently fetched, 61-post source snapshot comparison.
// Deliberately neither requests URLs nor claims that any visitor image has failed.
const fs = require('node:fs');
const path = require('node:path');
const FAIL = message => { throw new Error(message); };
function verify(x) {
  if (!x || x.schema !== 'fv-media-census-delta-v1') FAIL('schema');
  const p = x.provenance;
  if (!p || p.media_ref !== '4366489a68620d26592d8438b4402feb453c3166' ||
      p.qa_ref !== 'b64dc8673aec299192686d37296a4e1f0db56fa9' ||
      !/^[a-f0-9]{40}$/.test(p.qa_csv_blob) || !Array.isArray(p.media_parts) || p.media_parts.length !== 8 ||
      new Set(p.media_parts.map(z=>z.path)).size !== 8 ||
      p.media_parts.some((z,i)=>z.path !== 'qa/media-recovery/parts/' + String(i+1).padStart(2,'0') + '.json' || !/^[a-f0-9]{40}$/.test(z.blob))) FAIL('provenance');
  if (!Array.isArray(x.rows) || x.rows.length !== 61) FAIL('post census');
  const ids = new Set(); let images=0, qa=0, recovery=0, mismatches=0;
  for (const r of x.rows) {
    if (!Number.isSafeInteger(r.post_id) || ids.has(r.post_id)) FAIL('duplicate/invalid ID');
    ids.add(r.post_id);
    if (![r.image_count,r.qa_offsite,r.recovery_offsite].every(Number.isSafeInteger) ||
        r.image_count < 0 || r.qa_offsite < 0 || r.recovery_offsite < 0 ||
        r.qa_offsite > r.image_count || r.recovery_offsite > r.image_count) FAIL('invalid post counts');
    if (r.recovery_offsite - r.qa_offsite !== r.delta) FAIL('arithmetic drift');
    if (r.delta) { mismatches++; if (![285,291].includes(r.post_id) || r.delta !== 1 || r.image_count !== 6) FAIL('unexpected delta'); }
    images+=r.image_count; qa+=r.qa_offsite; recovery+=r.recovery_offsite;
  }
  if (images !== 355 || qa !== 286 || recovery !== 288 || mismatches !== 2 || !ids.has(285) || !ids.has(291)) FAIL('61-post reconciliation totals');
  const slots=x.suspected_origin_classification_slots;
  if (!Array.isArray(slots) || slots.length !== 2 || slots.map(s=>s.key).sort().join(',') !== '285:1,291:0') FAIL('mismatch slot keys');
  const expected={'285:1':'www.squawkpoint.com','291:0':'text-message.blogs.archives.gov'};
  for(const s of slots){
    if (s.post_id !== Number(s.key.split(':')[0]) || s.upstream_host !== expected[s.key] || s.upstream_host === 'finalvestige.com' ||
      s.source_kind !== 'external' || s.guest_http_status !== null || s.guest_decoded !== null || s.actual_transfer_bytes !== null ||
      s.rights_status !== 'HOLD' || s.cached_to_wordpress !== false || s.master_hash_sha256 !== null ||
      s.native_dimensions_px !== null || s.max_derivative_width_px !== 960 || s.browser_failure_proven !== false) FAIL('unsafe slot assertion');
    const u=new URL(s.source_url);
    if (u.hostname !== 'i0.wp.com' || !u.pathname.startsWith('/'+s.upstream_host+'/')) FAIL('not an external-origin Jetpack URL');
  }
  if(x.reported_42_broken_confirmed !== false || x.measured_76_percent_reduction !== null ||
     x.oversized_wp_originals?.count !== 20 || x.oversized_wp_originals?.stored_bytes !== 64385752 ||
     x.oversized_wp_originals?.network_transfer_bytes !== null ||
     x.qa_collector_owner !== 'Site QA #154' ||
     x.production_writes !== 0 || x.rights_clearances !== 0 || x.replacements_installed !== 0 ||
     x.cause !== 'UNDETERMINED: possible Jetpack classification or different source snapshots') FAIL('unsupported verification claim');
  return {pass:true,posts:61,images:355,qa_offsite:286,recovery_offsite:288,delta:2,offsite_disagreement_posts:[285,291],confirmed_guest_failures:0,guest_statuses_observed:0,production_writes:0};
}
if(require.main===module){
  try {const file=path.resolve(process.argv[2] || path.join(__dirname,'source_census_delta_61posts_20261116.json'));
    if(fs.statSync(file).size>128*1024) FAIL('oversized evidence');
    process.stdout.write(JSON.stringify(verify(JSON.parse(fs.readFileSync(file,'utf8'))),null,2)+'\n');
  } catch(e) {console.error('MEDIA_RECONCILIATION_HOLD:',e.message);process.exitCode=2;}
}
module.exports={verify};
