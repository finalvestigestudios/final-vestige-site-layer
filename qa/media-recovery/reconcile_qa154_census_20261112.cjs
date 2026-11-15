'use strict';
/** Offline source-scope reconciliation only; does NOT discover broken browser images. */
const crypto = require('node:crypto');
const fs = require('node:fs');
const {URL} = require('node:url');
const QA_SOURCE_BLOB = '76aa63ffaa299a6e6878edc1b66e637fa6f058ab';
const MEDIA_SOURCE_BLOB = 'a9706c72ad6f17a68113aa87fc063f70d0ca0c34';
const QA_CLASSIFIER_BLOB = 'cdadab899abed4dfd222e75a5616a98390dca4ea';
const fail = (reason) => ({status:'HOLD',reason,guest_broken_images_confirmed:null,production_change_allowed:false});
function gitBlobSha(text) {
 if (typeof text !== 'string') throw Error('text required');
 return crypto.createHash('sha1').update('blob '+Buffer.byteLength(text)+'\0').update(text).digest('hex');
}
function classify(src) {
 if (src===null||!String(src).trim()) return 'missing_src';
 let u;
 try {u=new URL(String(src).trim().replace(/&amp;/gi,'&'),'https://finalvestige.com');}
 catch {return 'non_http';}
 if(!['http:','https:'].includes(u.protocol))return 'non_http';
 const h=u.hostname.toLowerCase().replace(/^www\./,'');
 if(h==='finalvestige.com')return 'first_party';
 if(/^i[012]\.wp\.com$/.test(h)&&/^\/finalvestige\.com(?:\/|$)/i.test(u.pathname))return 'jetpack_proxy';
 if(h==='drive.google.com'&&u.pathname==='/thumbnail')return 'drive_thumbnail';
 if(h==='commons.wikimedia.org'&&u.pathname.startsWith('/wiki/Special:Redirect/'))return 'redirect_image';
 return 'external';
}
function readQaCsv(text) {
 if(typeof text!=='string'||text.length>128*1024)throw Error('Invalid QA CSV');
 const lines=text.trimEnd().split(/\r?\n/);
 if(lines.shift()!=='post_id,stored_img_src_count,offsite_src_count')throw Error('Unexpected QA CSV header');
 const posts=new Map();
 for(const line of lines){
  if(!/^\d+,\d+,\d+$/.test(line))throw Error('Invalid QA CSV row');
  const [id,total,offsite]=line.split(',').map(Number);
  if(!Number.isSafeInteger(id)||id<=0||offsite>total||posts.has(id))throw Error('Duplicate or invalid QA post');
  posts.set(id,{post_id:id,image_count:total,offsite_count:offsite});
 }
 return posts;
}
function reconcile(qaCsvText,mediaAuditText,options={}){
 try {
  if(options.enforcePins!==false && (gitBlobSha(qaCsvText)!==QA_SOURCE_BLOB ||
      gitBlobSha(mediaAuditText)!==MEDIA_SOURCE_BLOB)) return fail('SOURCE_GIT_BLOB_MISMATCH');
  const qa=readQaCsv(qaCsvText),ledger=JSON.parse(mediaAuditText);
  if(!ledger||!Array.isArray(ledger.rows))return fail('BAD_MEDIA_LEDGER');
  const rows=ledger.rows,media=new Map(),seen=new Set(),classes={};
  for(const r of rows){
   if(!r||!Number.isSafeInteger(r.post_id)||r.post_id<=0||
      typeof r.slot!=='string'||r.slot.split(':')[0]!==String(r.post_id)||
      !/^\d+:\d+$/.test(r.slot)||seen.has(r.slot)||
      typeof r.source_url!=='string'||!r.source_url.startsWith('https://')||
      r.source_equal!==true||r.alt_equal!==true||
      typeof r.offsite_historical_registry!=='boolean')return fail('BAD_MEDIA_ROW_OR_SLOT');
   seen.add(r.slot);
   const kind=classify(r.source_url),isOff=['external','redirect_image','drive_thumbnail'].includes(kind);
   if(isOff!==r.offsite_historical_registry)return fail('CLASSIFIER_AND_MEDIA_FLAG_DISAGREE');
   classes[kind]=(classes[kind]||0)+1;
   if(!media.has(r.post_id))media.set(r.post_id,{post_id:r.post_id,records:[],offsite_count:0});
   const x=media.get(r.post_id);
   x.records.push({slot:r.slot,published_original_url:r.source_url,qa_classifier_kind:kind,
    actual_origin_http_status:null,actual_guest_http_status:null,guest_decode:null,
    replacement_rights_cleared:false,proposed_max_width_px:960,upscale_allowed:false});
   if(isOff)x.offsite_count++;
  }
  if(qa.size!==media.size)return fail('POST_SET_MISMATCH');
  const differences=[];
  let qaTotal=0,qaOffsite=0,mediaTotal=0,mediaOffsite=0;
  for(const [id,q] of qa){
   const m=media.get(id);
   if(!m||q.image_count!==m.records.length)return fail('POST_IMAGE_COUNT_MISMATCH');
   qaTotal+=q.image_count;qaOffsite+=q.offsite_count;
   mediaTotal+=m.records.length;mediaOffsite+=m.offsite_count;
   if(m.offsite_count!==q.offsite_count)differences.push({post_id:id,
    qa154_offsite_count:q.offsite_count,media1703_offsite_count:m.offsite_count,
    difference:m.offsite_count-q.offsite_count,
    uncertainty:'POST_AGGREGATES_ONLY; cannot attribute discrepancy to a specific slot or decide whether snapshot changed',
    source_slots_for_custody_recheck:m.records});
  }
  differences.sort((a,b)=>a.post_id-b.post_id);
  if(options.enforcePins!==false &&
     (qaTotal!==355||mediaTotal!==355||qaOffsite!==286||mediaOffsite!==288||
      qa.size!==61||ledger.counts?.historical_offsite_positions!==288||
      differences.length!==2||differences[0].post_id!==285||differences[0].difference!==1||
      differences[1].post_id!==291||differences[1].difference!==1))return fail('UNEXPECTED_PINNED_SOURCE_COUNTS');
  return {schema:'fv-media-qa154-cross-audit-20261112-v1',status:'RECONCILED_POST_LEVEL_SOURCE_COUNT_DISAGREEMENT',
   input_git_blobs:{qa154_csv:gitBlobSha(qaCsvText),media1703_ledger:gitBlobSha(mediaAuditText),qa154_classifier_source:QA_CLASSIFIER_BLOB},
   counts:{posts:qa.size,inline_image_slots:mediaTotal,qa154_offsite_source_count:qaOffsite,
    media1703_same_classifier_offsite_count:mediaOffsite,offsite_difference:mediaOffsite-qaOffsite,
    exactly_matching_image_counts:qa.size,discrepant_post_count:differences.length,
    classifier_categories_on_media1703_ledger:classes},
   differences,
   interpretation:'Applying the QA #154 source classifier to the frozen Media #1703 ledger yields 288; the QA #154 CSV reports 286. This is not caused by a different Jetpack/proxy classification rule. The discrepancy is localized to post aggregates 285 and 291; underlying original QA source-slot snapshots are needed for attribution.',
   guest_broken_images_confirmed:null,reported_broken_images:42,sitewide_76_percent_wire_savings_measured:false,
   permission_to_copy_or_rehost:false,production_change_allowed:false,
   site_qa_action:'Use existing Site QA #154 workflow to compare original per-slot source snapshot for posts 285 and 291 with frozen 355-slot ledger, then cold browser-check the six-image P0 queue. Do not count two discrepant aggregates as broken media.'};
 }catch(e){return fail('RECONCILIATION_ERROR:'+e.message);}
}
if(require.main===module){
 try{
  if(process.argv.length!==4)throw Error('usage: node reconcile_qa154_census_20261112.cjs QA_CSV FROZEN_MEDIA_JSON');
  for(const name of process.argv.slice(2))if(fs.statSync(name).size>2*1024*1024)throw Error('Input too large');
  const outcome=reconcile(fs.readFileSync(process.argv[2],'utf8'),fs.readFileSync(process.argv[3],'utf8'));
  console.log(JSON.stringify(outcome,null,2));if(outcome.status==='HOLD')process.exitCode=2;
 }catch(e){console.error(e.message);process.exitCode=2;}
}
module.exports={gitBlobSha,classify,readQaCsv,reconcile,QA_SOURCE_BLOB,MEDIA_SOURCE_BLOB};
