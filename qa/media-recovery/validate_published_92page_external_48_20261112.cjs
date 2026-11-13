'use strict';
// Offline evidence integrity only — never performs network/WordPress writes.
function classify(u){const m=/^https:\/\/([^/?#]+)/i.exec(u);if(!m)return null;const h=m[1].toLowerCase();return h==="i.ytimg.com"?"youtube_thumbnails":h==="www.awin1.com"?"affiliate_creatives":h==="drive.google.com"?"google_drive_podcast_art":h==="upload.wikimedia.org"?"commons_archive":h==="us.suunto.com"?"merchant_product_photo":null;}
function validate(a){const errors=[],add=x=>errors.push(x),s=a.page_scan||{};
if(a.schema!=="fv-media-published-page-nonpost-source-exposure-20261112-v1")add("schema");
if(a.count_scope!=="PUBLISHED_WORDPRESS_PAGES_NOT_66_POSTS")add("cohort");
if(s.published_pages_read!==92||s.published_pages_read_errors!==0)add("page_scan");
if(s.literal_html_img_tags!==60||s.offsite_img_src_references!==48||s.first_party_or_jetpack_src_references!==12||s.external_page_count!==5)add("census");
if(!Array.isArray(a.rows)||a.rows.length!==48)add("row_count");
let found={},seen=new Set(),pg=new Set();
for(const r of(a.rows||[])){if(!r||typeof r!=="object"){add("bad_row");continue}const k=classify(r.source_url);
if(!k||k!==r.kind)add("url_host_kind");if(!r.raw_img_src_attribute||r.raw_img_src_attribute.replace(/&amp;/g,"&")!==r.source_url)add("literal_src");
if(seen.has(r.slot))add("slot_unique");seen.add(r.slot);pg.add(r.page_id);if(r.slot?.split(":")[0]!==String(r.page_id))add("slot_page");
if(!r.page_url?.startsWith("https://finalvestige.com/"))add("page_origin");
if(!r.source_url?.startsWith("https://"))add("http_scheme");
if(r.browser_http_status!==null||r.origin_http_status!==null||r.wire_transfer_bytes!==null||r.decoded_natural_width!==null||r.decoded_natural_height!==null)add("guest_unknown");
if(r.visual_failure_confirmed!==false||r.rehost_approved!==false||r.cache_approved!==false||r.candidate_rights_clearance!==false||r.exact_same_photo_verified!==false||r.candidate_replacement_local_url!==null)add("rights_hold");
if(r.max_derivative_width_px!==960||r.no_upscale!==true)add("960_no_upscale");
if(r.decision!=="HOLD_READONLY_NOT_CLEARED")add("release_hold");
if(k==="youtube_thumbnails"&&(!/^https:\/\/i\.ytimg\.com\/vi\/[A-Za-z0-9_-]+\/hqdefault\.jpg$/.test(r.source_url)||r.width_attribute_px!==480||r.height_attribute_px!==360||r.loading!=="lazy"))add("youtube_geometry");
found[k]=(found[k]||0)+1;
}
const expected={youtube_thumbnails:40,affiliate_creatives:3,google_drive_podcast_art:1,commons_archive:3,merchant_product_photo:1};
for(const k of Object.keys(expected))if(found[k]!==expected[k]||s.external_source_kinds?.[k]!==expected[k])add("kind_count_"+k);
if(pg.size!==5||!Array.isArray(a.external_page_summary)||a.external_page_summary.filter(x=>x.external_img_tags>0).length!==5||a.external_page_summary.reduce((n,x)=>n+x.external_img_tags,0)!==48)add("page_coverage");
const o=a.oversized_media_reference||{};if(o.media_id!==293||o.original_stored_bytes!==2090327||o.referenced_by_published_page_id!==234||o.jsonld_reference_verified!==true||o.guest_transfer_bytes!==null||o.media_http_status!==null||o.not_safe_to_delete!==true)add("profile_293");
const h=a.historical_context||{};if(h.alleged_42_broken_guest_confirmed!==false||h.alleged_76_percent_network_savings_measured!==false||h.oversize_original_stored_bytes!==47096779)add("historical_limits");
const p=a.policy||{};if(p.site_qa_guest_collector_pr!==154||p.media_recovery_draft_pr!==1703||p.no_wordpress_writes!==true||p.no_external_binaries_fetched!==true||p.no_auto_caching!==true||p.no_unauthorized_rehosting!==true||p.no_subscription_spending!==true)add("scope_safety");
return errors}
module.exports={classify,validate};
if(require.main===module){const fs=require('node:fs');const a=JSON.parse(fs.readFileSync(process.argv[2]||__dirname+'/published_92page_external_48_and_profile_293_20261112.json','utf8'));const e=validate(a);if(e.length){console.error(e.join('\n'));process.exitCode=1}else console.log('48 source references pass integrity checks; browser verification still required');}
