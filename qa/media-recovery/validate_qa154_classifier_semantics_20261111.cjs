'use strict';
// Offline interpretation of exact QA #154 classifier semantics for pinned absolute HTTP image URLs.
// Source census !== a logged-out guest-browser failure audit.
function classifyAbsolute(src) {
 if(typeof src!=='string'||!src.trim())return 'missing_src';
 const m=src.trim().replace(/&amp;/gi,'&').match(/^https?:\/\/([^/?#]+)(\/[^?#]*)?/i);
 if(!m)return 'non_http';
 const h=m[1].toLowerCase().replace(/^www\./,''),p=m[2]||'/';
 if(h==='finalvestige.com')return 'first_party';
 if(/^i[012]\.wp\.com$/.test(h)&&/^\/finalvestige\.com(?:\/|$)/i.test(p))return 'jetpack_proxy';
 if(h==='drive.google.com'&&p==='/thumbnail')return 'drive_thumbnail';
 if(h==='commons.wikimedia.org'&&p.startsWith('/wiki/Special:Redirect/'))return 'redirect_image';
 return 'external';
}
const SOURCE_BLOBS=[
 '948bc1b65b42799aa40cfdb810ddf6ffd80886b6',
 '48e1ebf07207e948ba5802e714eb39659d2e1c1d',
 '49183f66f880f7c4dfd363acca906876877f2e5e',
 '6df3251e5a67a971d87a516a1ba4a0cc32f51f96',
 '9b16b828342a9ac338f3e65610fd3d8d508355e9',
 '0f3dfe398a76838049cebba7cb773d5c5a0c8c69',
 '21095161e633aba093b74c0ead9936c9f6186d00',
 '5659ec243c188928be3f89c0f96354b660608ca2'
];
function verify(a) {
 const hold=code=>({status:'HOLD',reason:code,production_write_allowed:false,visitor_failures_established:false});
 if(!a||a.schema!=='fv-media-qa154-source-classifier-replay-v1'||!Array.isArray(a.rows)||a.rows.length!==61||
    a.sources?.QA_classifier_blob!=='cdadab899abed4dfd222e75a5616a98390dca4ea'||
    a.sources?.QA_csv_blob!=='76aa63ffaa299a6e6878edc1b66e637fa6f058ab'||
    JSON.stringify(a.sources?.source_parts_blobs)!==JSON.stringify(SOURCE_BLOBS)||
    a.counts?.posts!==61||a.counts?.inline!==355||
    a.counts?.qa_reported_offsite!==286||a.counts?.current_QA_classifier_replay_offsite!==288||
    a.counts?.source_kinds?.first_party!==60||a.counts?.source_kinds?.jetpack_proxy!==7||
    a.counts?.source_kinds?.external!==170||a.counts?.source_kinds?.redirect_image!==118)
    return hold('SOURCE_BLOB_OR_COHORT_MISMATCH');
 const ids=new Set();let sumTotal=0,sumQA=0,sumReplay=0;const diff=[];
 for(const row of a.rows){
  if(!row||!Number.isSafeInteger(row.post_id)||row.post_id<=0||ids.has(row.post_id)||
     !Number.isSafeInteger(row.qa_inline)||row.qa_inline<1||
     row.replay_inline!==row.qa_inline||
     !Number.isSafeInteger(row.qa_offsite)||row.qa_offsite<0||row.qa_offsite>row.qa_inline||
     !Number.isSafeInteger(row.replay_offsite)||row.replay_offsite<0||row.replay_offsite>row.replay_inline)
    return hold('INVALID_POST_ROW');
  ids.add(row.post_id);sumTotal+=row.qa_inline;sumQA+=row.qa_offsite;sumReplay+=row.replay_offsite;
  if(row.qa_offsite!==row.replay_offsite)diff.push([row.post_id,row.replay_offsite-row.qa_offsite]);
 }
 if(sumTotal!==355||sumQA!==286||sumReplay!==288||
    JSON.stringify(diff.sort((a,b)=>a[0]-b[0]))!=='[[285,1],[291,1]]')
    return hold('REPLAY_DIVERGENCE');
 const original={
  '285:1':['www.squawkpoint.com','https://i0.wp.com/www.squawkpoint.com/wp-content/uploads/2019/02/Three-Mile-Island-Control-Centre.jpg?ssl=1'],
  '291:0':['text-message.blogs.archives.gov','https://i0.wp.com/text-message.blogs.archives.gov/wp-content/uploads/sites/5/2016/05/teton_failing_fourth-scaled.jpg?ssl=1']
 };
 if(!Array.isArray(a.exceptions)||a.exceptions.length!==2)return hold('EXCEPTION_ROW_COUNT');
 const seen=new Set();
 for(const e of a.exceptions){
  if(!e||seen.has(e.slot)||!original[e.slot]||e.post_id!==Number(e.slot.split(':')[0])||
     e.source_url!==original[e.slot][1]||e.upstream_host!==original[e.slot][0]||
     e.delivery_host!=='i0.wp.com'||classifyAbsolute(e.source_url)!=='external'||
     e.classification_from_current_QA_rules!=='external'||e.visitor_http!==null||
     e.visitor_decode!==null||e.network_bytes!==null||e.native_dimensions!==null||
     e.rights_approved!==false||e.wordPress_write_approved!==false||
     e.caching_allowed!==false||e.max_derivative_width_px!==960||e.upscaling_allowed!==false)
    return hold('EXCEPTION_URL_CLASSIFICATION_RIGHTS_OR_BROWSER');
  seen.add(e.slot);
 }
 if(a.conclusion?.third_party_jetpack_exclusion_by_current_classifier!==false||
    a.conclusion?.historical_root_cause_proven!==false||
    a.conclusion?.qa_original_snapshot_not_retained!==true||
    a.performance?.historical_reported_broken!==42||
    a.performance?.guest_confirmed_broken!==0||
    a.performance?.proposed_76_percent_measured!==false||
    a.performance?.oversized_wp_originals!==15||
    a.performance?.oversized_stored_original_bytes!==47096779||
    a.performance?.visitor_wire_bytes!==null||
    a.restrictions?.no_wp_writes!==true||a.restrictions?.no_cache!==true||
    a.restrictions?.no_binary_download!==true)
    return hold('INVENTED_CAUSE_GUEST_STATUS_OR_RELEASE_PERMISSION');
 return {status:'SOURCE_ONLY_REPLAY_PASS',posts:61,inline:355,qa_offsite:286,replayed_offsite:288,
  differing_posts:[285,291],historical_cause_established:false,
  third_party_jetpack_excluded_by_QA_classifier:false,
  visitor_failures_established:false,network_saving_76_percent_verified:false,
  production_write_allowed:false};
}
if(typeof require!=='undefined'&&require.main===module){
 const fs=require('node:fs');
 if(process.argv.length!==3)throw Error('usage: node validate_qa154_classifier_semantics_20261111.cjs <replay.json>');
 const result=verify(JSON.parse(fs.readFileSync(process.argv[2],'utf8')));
 console.log(JSON.stringify(result,null,2));
 if(result.status!=='SOURCE_ONLY_REPLAY_PASS')process.exitCode=2;
}
if(typeof module!=='undefined')module.exports={classifyAbsolute,verify};
