'use strict';
// Offline derivation only: no HTTP, image download, WordPress edit, or bandwidth claim.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const crypto = require('node:crypto');
const path = require('node:path');
const SOURCE_BLOB='66aa70b1982237015b87b1901ea0100fe9e64181';
const isInt=n=>Number.isSafeInteger(n)&&n>=0;
const gitBlob=t=>{const b=Buffer.from(t,'utf8');return crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex');};
const hold=m=>{throw Error('HOLD: '+m)};
function derive(src){
  if(!src||src.schema!=='fv-oversized-current-66-inline-crosswalk-v1')hold('unknown crosswalk schema');
  if(!Array.isArray(src.items)||src.items.length!==20||!src.summary||src.summary.total_stored_bytes!==64385752)hold('source coverage/total drift');
  let slots=new Set(), ids=new Set();
  const rows=src.items.map(i=>{
    if(!isInt(i.id)||ids.has(i.id)||typeof i.filename!=='string'||!/^2026\/(08|10|11)\/[a-zA-Z0-9_.-]+$/.test(i.filename)||!isInt(i.original_bytes)||i.original_bytes<=1500000||!Array.isArray(i.inline_exact_origin_slots))hold('invalid/duplicate media item');
    ids.add(i.id);
    const exact=i.inline_exact_origin_slots.map(s=>{
      if(!/^\d+:\d+$/.test(s.slot_id)||slots.has(s.slot_id)||s.has_srcset!==true&&s.has_srcset!==false||s.has_sizes!==true&&s.has_sizes!==false)hold('invalid/duplicate slot');
      slots.add(s.slot_id);
      const u=new URL(s.view_img_src);
      if(u.protocol!=='https:'||!/^i[0-3]\.wp\.com$/.test(u.hostname)||u.pathname!=='/finalvestige.com/wp-content/uploads/'+i.filename)hold('non-matching inline image origin');
      const p=new URL(s.post_url);
      if(p.hostname!=='finalvestige.com'||p.protocol!=='https:')hold('non-site post');
      const mode=u.searchParams.has('resize')?'resize':u.searchParams.has('fit')?'fit':null;
      const match=mode&&/^(\d+),(\d+)$/.exec(u.searchParams.get(mode));
      if(!match||Number(match[1])<1||Number(match[2])<1||Number(match[1])>10000||Number(match[2])>10000)hold('missing/invalid published size hint');
      return {slot:s.slot_id,post_url:s.post_url,authored_img_url:s.view_img_src,query_width_px:Number(match[1]),query_height_px:Number(match[2]),has_srcset:s.has_srcset,guest_http:null,guest_current_src:null,guest_wire_bytes:null,guest_decoded:null};
    });
    if(exact.length>1)hold('unreviewed multi-slot media original');
    const lane=exact.length?(exact.some(s=>!s.has_srcset)?'P0_INLINE_NO_SRCSET':'P1_INLINE_RESPONSIVE'):'P2_NOT_FOUND_INLINE_66_POSTS';
    return {media_id:i.id,filename:i.filename,original_stored_bytes:i.original_bytes,original_over_1_5_MiB:i.original_bytes>1572864,lane,exact_inline_slots:exact,other_page_uses_unknown:true,asset_rights:'HOLD',derivative_limit_width_px:960,derivative_width_px:null,native_raster_verified:false,allow_upscale:false,allow_rehost:false,allow_wp_write:false};
  });
  rows.sort((a,b)=>b.original_stored_bytes-a.original_stored_bytes||a.media_id-b.media_id);
  const sum=(predicate)=>rows.filter(predicate).reduce((n,r)=>n+r.original_stored_bytes,0);
  const inline=rows.filter(r=>r.exact_inline_slots.length);
  const summary={originals_gt_1_5_MB_decimal:rows.length,originals_gt_1_5_MiB_binary:rows.filter(r=>r.original_over_1_5_MiB).length,stored_original_bytes:sum(()=>true),exact_inline_media: inline.length,exact_inline_slots:inline.reduce((n,r)=>n+r.exact_inline_slots.length,0),exact_inline_stored_original_bytes:sum(r=>r.exact_inline_slots.length>0),not_matched_inline_media:rows.length-inline.length,not_matched_inline_stored_original_bytes:sum(r=>r.exact_inline_slots.length===0),no_srcset_inline_media:rows.filter(r=>r.lane==='P0_INLINE_NO_SRCSET').length,no_srcset_inline_original_stored_bytes:sum(r=>r.lane==='P0_INLINE_NO_SRCSET'),original_total_is_not_wire_bytes:true,guest_42_broken_confirmed:null,wire_76_percent_savings_verified:false, measured_before_bytes:null,measured_after_bytes:null};
  if(JSON.stringify([summary.stored_original_bytes,summary.exact_inline_media,summary.exact_inline_stored_original_bytes,summary.no_srcset_inline_media,summary.no_srcset_inline_original_stored_bytes,summary.originals_gt_1_5_MiB_binary])!==JSON.stringify([64385752,11,38480915,5,13267538,19]))hold('crosswalk summary drift');
  return {schema:'fv-media-oversized-20-inline-priority-20261118-v1',basis:{source_blob:SOURCE_BLOB,census_posts:66,census_date:'2026-11-17',source:'WordPress media originals + 66-post inline exact-origin crosswalk; no browser transfer'},summary,rows,release:{status:'HOLD',siteqa_owner:'PR #154',guest_chromium_pending:true,rehosts:0,wp_writes:0,homepage_design_changes:0,cost_usd:0}};
}
function check(ledger,raw){if(gitBlob(raw)!==SOURCE_BLOB)hold('pinned Git crosswalk mismatch');const expected=derive(JSON.parse(raw));assert.deepStrictEqual(ledger,expected);return expected.summary;}
module.exports={SOURCE_BLOB,gitBlob,derive,check};
if(require.main===module){try{const raw=fs.readFileSync(path.join(__dirname,'live_20_oversized_to_66_post_inline_crosswalk_20261117.json'),'utf8');const f=process.argv[2]||path.join(__dirname,'oversize_20_inline_priority_20261118.json');console.log(JSON.stringify(check(JSON.parse(fs.readFileSync(f,'utf8')),raw),null,2));}catch(e){console.error(e.message);process.exitCode=1;}}
