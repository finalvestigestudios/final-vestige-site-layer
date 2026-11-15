'use strict';
const EXPECTED = {
  "283:0": [
    "https://2.bp.blogspot.com/-vFf9zOG42QU/W2shS055U-I/AAAAAAAACc0/uHswGJB19E4OgUANkDatBX7LSCIEswfZgCLcBGAs/s1600/Fire%2BEscape%2BDoors%2BPortrait%2BMode.jpg",
    "Fire-damaged exit doors inside Chicago's Iroquois Theatre after the December 30, 1903 fire."
  ],
  "283:1": [
    "https://miro.medium.com/v2/resize:fit:1400/1*IcflN4VAkB2zIyMzIbcmyQ.jpeg",
    "The new Iroquois Theatre on Randolph Street in Chicago shortly before the 1903 fire."
  ],
  "283:2": [
    "https://chicagology.com/wp-content/themes/revolution-20/chicagoimages2/iroquoispromenade.jpg",
    "Contemporary drawing of the ornate Iroquois Theatre foyer and promenade before the fire."
  ],
  "283:3": [
    "https://bloximages.chicago2.vip.townnews.com/enidnews.com/content/tncms/assets/v3/editorial/b/4e/b4e59e84-74da-5f9e-b24f-5e9e3658fd34/54716e12ac97b.image.jpg?resize=1200%2C804",
    "Charred seating and stage area inside the Iroquois Theatre after the 1903 fire."
  ],
  "283:4": [
    "https://www.wttw.com/sites/default/files/csdd-investigators_02.jpg",
    "Investigators inside the damaged Iroquois Theatre after the 1903 fire."
  ],
  "283:5": [
    "https://images2.minutemediacdn.com/image/upload/c_fill,w_720,ar_16:9,f_auto,q_auto,g_auto/shape/cover/sport/627134-wikimedia-iroquois-fire-66b8dccd06d18b8b1200a566c6d50b53.jpg",
    "Historical Iroquois Theatre exit and fire-escape area after the disaster."
  ],
  "283:6": [
    "https://florencekelley.northwestern.edu/img/galleries/historical/iroquois/i36009aa.jpg",
    "Crowd and street scene outside the Iroquois Theatre after the 1903 fire."
  ]
};
const BAD = new Set(['CONFIRMED_BROKEN','GUEST_HTTP_VERIFIED']);
function validate(a) {
 const failures=[];
 if(!a||a.schema!=='fv-media-iroquois-283-visual-v1') return ['schema'];
 const b=a.historical_baseline||{};
 if(b.posts!==61||b.image_positions!==355||b.external_positions!==288||b.reported_broken_42_confirmed_by_guest_browser!==false||b.proposed_transfer_reduction_76pct_measured!==false)failures.push('baseline');
 if(a.post?.id!==283||a.post?.inventory_blob_sha!=='49183f66f880f7c4dfd363acca906876877f2e5e')failures.push('fixture');
 const rows=a.source_rows;
 if(!Array.isArray(rows)||rows.length!==7)return failures.concat('row count');
 const keys=new Set(),rendered={DISPLAYED:0,TOOL_INACCESSIBLE:0},mismatches=[],reviewFlags=[];
 for(const x of rows) {
  if(!x||!EXPECTED[x.key]||keys.has(x.key)){failures.push('duplicate/unexpected key');continue}keys.add(x.key);
  if(x.stored_source_url!==EXPECTED[x.key][0]||x.published_alt!==EXPECTED[x.key][1]||x.post_id!==283||x.post_url!==a.post.url)failures.push('original source/alt/identity '+x.key);
  const v=x.retriever||{};
  if(v.method!=='WEB_IMAGE_RETRIEVER_VISUAL_NOT_HTTP'||!Object.prototype.hasOwnProperty.call(rendered,v.observation)||BAD.has(v.observation)) failures.push('observation '+x.key);
  else rendered[v.observation]++;
  for(const field of ['origin_http_status','guest_http_status','visitor_current_src','mime','natural_width_px','natural_height_px','wire_transfer_bytes','guest_broken']) if(v[field]!==null)failures.push('fabricated guest evidence '+x.key+':'+field);
  const s=x.visual||{},c=x.candidate||{},rel=x.release||{};
  if(['MISMATCH','SCENE_NOT_CATALOG_IDENTIFIED','CHRONOLOGY_UNSUPPORTED'].includes(s.assessment)){reviewFlags.push(x.key);if(!s.proposed_alt_review_only)failures.push('missing editorial proposal '+x.key)}
  if(s.assessment==='MISMATCH')mismatches.push(x.key);
  if(s.editorial_change_applied!==false)failures.push('editorial write '+x.key);
  if(typeof c.catalog_url!=='string'||!c.catalog_url.startsWith('https://'))failures.push('catalog '+x.key);
  if(c.maximum_target_width_px!==960||c.exact_pixel_and_crop_identity_proven!==false||c.rehosting_rights_cleared!==false||c.cached_or_downloaded!==false)failures.push('rights/crop '+x.key);
  if(c.conditional_target_px!==null){
   const z=c.conditional_target_px, native=c.catalog_native_px;
   if(!Array.isArray(z)||!Array.isArray(native)||z.length!==2||native.length!==2||z.some(q=>!Number.isInteger(q)||q<=0)||z[0]>960||z[0]>native[0]||z[1]>native[1]||Math.abs((z[0]/z[1])-(native[0]/native[1]))>0.004)failures.push('geometry '+x.key);
  }
  for(const k of ['wordpress_upload_allowed','post_rewrite_allowed','cache_allowed','source_swap_allowed','homepage_change_allowed'])if(rel[k]!==false)failures.push('unapproved release '+x.key+':'+k);
 }
 if(keys.size!==7||rendered.DISPLAYED!==6||rendered.TOOL_INACCESSIBLE!==1)failures.push('source verification');
 if(mismatches.sort().join(',')!=='283:0'||reviewFlags.sort().join(',')!=='283:0,283:5,283:6')failures.push('caption discrepancy ledger');
 if(a.counts?.guest_confirmed_broken!==0||a.counts?.caption_mismatches!==1||a.counts?.editorial_review_flags!==3||a.counts?.tool_rendered!==6||a.counts?.tool_inaccessible!==1)failures.push('counts');
 if(a.acceptance_plan?.owner!=='Site QA PR #154 existing collector')failures.push('collector ownership');
 return failures;
}
module.exports={validate};
if(require.main===module){const fs=require('node:fs');const a=JSON.parse(fs.readFileSync(process.argv[2]||'qa/media-recovery/iroquois_283_seven_visual_20261109.json','utf8'));const issues=validate(a);if(issues.length){console.error(issues.join('\n'));process.exitCode=1}else console.log('IROQUOIS_PASS: 7 pinned images, 3 caption mismatches, no invented browser evidence or unapproved release')}
