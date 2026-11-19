'use strict';
// Read-only audit of captured WordPress rendered-page social image metadata.
// Does not fetch, rewrite, download, crawl or publish media.
const SCHEMA='fv-live-social-card-image-census-v1';
const EXPECTED=new Map([[274,"https://finalvestige.com/2026/08/19/twenty-four-feet-from-air-uss-tang/"],[287,"https://finalvestige.com/2026/08/19/the-warning-was-a-man-waving-sunshine-skyway/"],[285,"https://finalvestige.com/2026/08/19/the-light-said-closed-three-mile-island/"],[291,"https://finalvestige.com/2026/08/19/one-bulldozer-never-came-back-teton-dam/"],[418,"https://finalvestige.com/2026/08/20/the-lighthouse-was-gone-at-dawn-1946-tsunami/"],[407,"https://finalvestige.com/2026/08/20/the-lake-wasnt-there-yesterday-hebgen/"],[299,"https://finalvestige.com/2026/08/19/thirty-men-were-enough-vasa/"],[1917,"https://finalvestige.com/2026/11/02/piri-reis-map/"],[621,"https://finalvestige.com/2026/08/23/six-miles-an-hour-malbone-street-wreck/"],[268,"https://finalvestige.com/2026/08/18/they-painted-over-archimedes/"],[432,"https://finalvestige.com/2026/08/20/they-buried-the-dead-apart-okeechobee-1928/"],[434,"https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"]]);
const validUrl=s=>typeof s==='string'&&/^https:\/\/[^\s/?#]+(?:[/?#]|$)/i.test(s);
const host=s=>(/^https:\/\/([^/?#]+)/i.exec(s)||[])[1]?.toLowerCase()||'';
const firstParty=s=>{const h=host(s); if(h==='finalvestige.com')return true;
 if(/^i[0-9]\.wp\.com$/.test(h))return /^https:\/\/i\d\.wp\.com\/finalvestige\.com(?:\/|$)/i.test(s);
 return false;};
function classify(p,probes){
 const fallback=/\/fv-site-icon-512\.png(?:[?#]|$)/.test(p.og_image);
 const brokenOrigin=(probes||[]).some(q=>q.post_id===p.post_id&&q.url===p.og_image&&q.observed_http===404&&q.observed_by==='PUBLIC_WEB_RETRIEVER');
 return fallback?'GENERIC_BRAND_ICON':brokenOrigin?'ORIGINAL_404_SHARE_CARD_RISK':firstParty(p.og_image)?'FIRST_PARTY_OR_JETPACK':'EXTERNAL_DEPENDENCY';
}
function audit(s){
 const errors=[];const add=x=>errors.push(x);
 if(!s||s.schema!==SCHEMA||!Array.isArray(s.pages)||s.pages.length!==EXPECTED.size)return {gate:'HOLD',errors:['schema_or_coverage']};
 if(s.network_measurements!==false||s.production_writes!==0||s.verified_broken_visitor_images!==null||s.verified_image_wire_saving_percent!==null)add('unsupported_verification_claim');
 const seen=new Set(),result=[],counts={GENERIC_BRAND_ICON:0,ORIGINAL_404_SHARE_CARD_RISK:0,FIRST_PARTY_OR_JETPACK:0,EXTERNAL_DEPENDENCY:0};
 for(const p of s.pages){
  if(!p||!EXPECTED.has(p.post_id)||p.page_url!==EXPECTED.get(p.post_id)||seen.has(p.post_id)||p.page_http!==200)add('post_identity_or_status');
  if(p&&Number.isSafeInteger(p.post_id))seen.add(p.post_id);
  if(!p||!validUrl(p.og_image)||!validUrl(p.twitter_image)||!Number.isSafeInteger(p.og_image_width_declared)||p.og_image_width_declared<1||!Number.isSafeInteger(p.og_image_height_declared)||p.og_image_height_declared<1||typeof p.og_alt!=='string'||!p.og_alt.trim()||p.image_response_http!==null||p.image_decode!==null||p.image_network_transfer_bytes!==null){add('social_image_or_unproven_image_status');continue;}
  const kind=classify(p,s.external_origin_probes);
  const width=Math.min(960,p.og_image_width_declared);
  result.push({post_id:p.post_id,kind,og_image:p.og_image,editorial_max_width_no_upscale_px:width,editorial_height_from_declared_ratio_px:Math.max(1,Math.round(width*p.og_image_height_declared/p.og_image_width_declared)),verified_guest_image:false});
  counts[kind]++;
 }
 if(seen.size!==EXPECTED.size)add('missing_posts');
 for(const q of s.external_origin_probes||[]){
  if(!q||!EXPECTED.has(q.post_id)||!validUrl(q.url)||!['PUBLIC_WEB_RETRIEVER','EARLIER_PUBLIC_WEB_RETRIEVER'].includes(q.observed_by)||q.observed_http!==404||q.guest_browser_http!==null||q.observed_date!=='2026-11-18')add('unsupported_origin_probe');
  const p=s.pages.find(p=>p.post_id===q.post_id);
  if(p&&q.origin_same_as_og_image!==(p.og_image===q.url))add('og_origin_confusion');
 }
 for(const c of s.recovery_candidates||[]){
  if(!c||!EXPECTED.has(c.post_id)||!validUrl(c.catalog)||c.approved_to_replace!==false||c.same_crop_verified!==false||!String(c.rights).startsWith('HOLD'))add('unapproved_replacement_candidate');
 }
 if(!s.cache_and_wp_plan||s.cache_and_wp_plan.production_wordpress_write!==false||s.cache_and_wp_plan.automated_mirror!==false||s.cache_and_wp_plan.proportional_no_upscale_max_width_px!==960)add('unsafe_staging_plan');
 return {gate:errors.length?'HOLD':'REVIEW_REQUIRED_NO_AUTOMATED_FIX',errors,counts,results:result,guest_broken_verified:false,bandwidth_76_verified:false};
}
module.exports={audit,classify};
if(require.main===module){
 const fs=require('node:fs'); const filename=process.argv[2];
 if(!filename){console.error('Usage: node social_card_source_integrity_20261118_1930.cjs audit.json');process.exitCode=2;}
 else{const r=audit(JSON.parse(fs.readFileSync(filename,'utf8')));console.log(JSON.stringify(r,null,2));if(r.gate==='HOLD')process.exitCode=1;}
}
