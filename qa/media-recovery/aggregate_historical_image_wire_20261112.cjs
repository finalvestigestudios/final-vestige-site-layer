'use strict';
/**
 * Historical cohort-only image-wire rollup. Consumes Site QA's existing CDP
 * pairs; does not initiate a browser, download, rewrite, upload, or publish.
 * A 61-post sample is NOT the currently expanded 66-post site.
 */
const {compareColdPairVisualParity}=require('./compare_cold_pair_visual_parity_20261111.cjs');
const {bindExactHistoricalAudit}=require('./bind_exact_historical_audit_20261112.cjs');
const AUDIT_BLOB='a9706c72ad6f17a68113aa87fc063f70d0ca0c34';
const AUDIT_SCHEMA='fv-media-complete-historical-61-355-live-src-alt-20261112-v1';
const hold=(reason,slot=null)=>({status:'HOLD',reason,slot,
 historical_cohort_transfer_before_bytes:null,
 historical_cohort_transfer_after_bytes:null,
 historical_cohort_image_wire_reduction_percent:null,
 historical_cohort_target_76_met:null,
 current_sitewide_76_percent_verified:false,
 production_change_allowed:false});
const listEqual=(a,b)=>Array.isArray(a)&&Array.isArray(b)&&a.length===b.length&&
 a.every((v,i)=>v===b[i]);
function aggregateHistoricalImageWire(auditBytes,pairs,blobSha){
 const bound=bindExactHistoricalAudit(auditBytes,blobSha,AUDIT_BLOB);
 if(!bound.ok)return hold('FROZEN_COHORT_SOURCE_UNVERIFIED:'+bound.reason);
 const audit=bound.audit;
 if(audit?.schema!==AUDIT_SCHEMA||
    !Array.isArray(audit.rows)||audit.rows.length!==355||
    audit.counts?.frozen_posts!==61||
    audit.counts?.verified_image_positions!==355||
    audit.counts?.historical_offsite_positions!==288||
    audit.counts?.historical_first_party_positions!==67||
    audit.policy?.visitor_browser_confirmed_42_broken!==false||
    audit.policy?.claimed_76_percent_network_byte_reduction_verified!==false)
   return hold('FROZEN_COHORT_SOURCE_UNVERIFIED');
 const byPost=new Map(),slots=new Set();
 for(const row of audit.rows){
   if(!row||typeof row!=='object'||!Number.isSafeInteger(row.post_id)||row.post_id<=0||
      typeof row.slot!=='string'||!/^\d+:\d+$/.test(row.slot)||
      row.slot.split(':')[0]!==String(row.post_id)||slots.has(row.slot)||
      row.source_equal!==true||row.alt_equal!==true||
      typeof row.source_url!=='string'||!row.source_url.startsWith('https://')||
      typeof row.alt!=='string'||
      typeof row.post_url!=='string'||!row.post_url.startsWith('https://finalvestige.com/')||
      row.rights_cleared!==false||row.wordpress_write_authorized!==false)
     return hold('CORRUPT_FROZEN_IMAGE_RECORD',row.slot);
   slots.add(row.slot);
   if(!byPost.has(row.post_id))byPost.set(row.post_id,[]);
   byPost.get(row.post_id).push(row);
 }
 if(byPost.size!==61||!Array.isArray(pairs)||pairs.length!==61)
   return hold('INCOMPLETE_61_POST_COVERAGE');
 const seenPost=new Set();
 let before=0,after=0,uniqueRequestsBefore=0,uniqueRequestsAfter=0;
 for(const pair of pairs){
   const rows=byPost.get(pair?.post_id);
   if(!rows||seenPost.has(pair.post_id))
     return hold('DUPLICATE_OR_UNRELATED_POST',String(pair?.post_id));
   seenPost.add(pair.post_id);
   const required=rows.map(r=>r.slot).sort();
   if(!listEqual([...new Set(pair.expected_slots||[])].sort(),required)||
      pair.expected_slots?.length!==required.length)
     return hold('INCOMPLETE_OR_FOREIGN_FROZEN_SLOTS',String(pair.post_id));
   const targetUrl=rows[0].post_url;
   if(rows.some(r=>r.post_url!==targetUrl)||
      pair.before?.page_url!==targetUrl||pair.after?.page_url!==targetUrl)
     return hold('POST_URL_CHANGED',String(pair.post_id));
   for(const capture of [pair.before,pair.after]){
     if(!Array.isArray(capture?.images)||capture.images.length!==rows.length)
       return hold('INCOMPLETE_IMAGE_CAPTURE',String(pair.post_id));
     const items=new Map(capture.images.map(x=>[x.slot,x]));
     if(items.size!==rows.length)
       return hold('DUPLICATE_IMAGE_SLOT',String(pair.post_id));
     for(const r of rows){
       const item=items.get(r.slot);
       if(!item||item.published_original_src!==r.source_url||
          item.published_alt!==r.alt||
          item.published_source_provenance!=='WP_EDIT_SOURCE_MATCHED_FROZEN')
         return hold('UNBOUND_STORED_IMAGE_IDENTITY',r.slot);
     }
   }
   const verdict=compareColdPairVisualParity(pair);
   if(verdict.status!=='VERIFIED_SINGLE_POST_COLD_PAIR_WITH_VISUAL_PARITY'||
      verdict.quality_preserved!==true||verdict.production_change_allowed!==false||
      verdict.sitewide_transfer_savings_verified!==false)
     return hold('UNVERIFIED_PER_POST_COLD_PAIR:'+verdict.reason,
       verdict.slot||String(pair.post_id));
   if(!Number.isSafeInteger(verdict.image_network_before_bytes)||
      !Number.isSafeInteger(verdict.image_network_after_bytes)||
      verdict.image_network_before_bytes<=0||verdict.image_network_after_bytes<=0)
     return hold('INVALID_IMAGE_NETWORK_BYTES',String(pair.post_id));
   before+=verdict.image_network_before_bytes;
   after+=verdict.image_network_after_bytes;
   uniqueRequestsBefore+=verdict.unique_completed_requests_before;
   uniqueRequestsAfter+=verdict.unique_completed_requests_after;
   if(!Number.isSafeInteger(before)||!Number.isSafeInteger(after))
     return hold('NETWORK_TOTAL_OVERFLOW');
 }
 if(seenPost.size!==61)return hold('INCOMPLETE_61_POST_COVERAGE');
 const percent=Math.round((before-after)*10000/before)/100;
 return {
   status:'VERIFIED_HISTORICAL_61_POST_INLINE_IMAGE_COHORT_ONLY',
   frozen_source_git_blob_sha:AUDIT_BLOB,
   observed_post_count:61,observed_img_slots:355,
   unique_requests_before:uniqueRequestsBefore,
   unique_requests_after:uniqueRequestsAfter,
   historical_cohort_transfer_before_bytes:before,
   historical_cohort_transfer_after_bytes:after,
   historical_cohort_image_wire_reduction_percent:percent,
   historical_cohort_target_76_met:(before-after)*100>=76*before,
   current_sitewide_76_percent_verified:false,
   production_change_allowed:false,
   scope:'Equal one cold guest visit per each of 61 historical posts, inline Image requests only; NOT 66 currently published posts, CSS/background images, traffic-weighted savings, total page weight or authorization to publish',
   next_evidence:'Obtain independently matched cold captures on newer published posts and other image classes before any current-sitewide or overall-page-weight claim'
 };
}
module.exports={aggregateHistoricalImageWire,AUDIT_BLOB};
