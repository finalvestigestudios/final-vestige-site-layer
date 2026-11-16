'use strict';
const fs = require('node:fs');
const path = require('node:path');
function validate(a) {
  const errors = [], bad = (name) => errors.push(name);
  if (a.schema !== 'fv-archimedes-268-image-source-rights-v1') bad('schema');
  if (a.post?.id !== 268 || a.post?.contexts_equal_revision !== true || a.post?.status !== 'publish') bad('revision');
  if (a.writes !== 0 || a.media_downloads !== 0) bad('unauthorized_activity');
  if (!Array.isArray(a.rows) || a.rows.length !== 10) return { ok:false, errors:['row_count'] };
  const counts = { commons:0, project:0, conflict:0, pd:0, queryOver:0 };
  for (let i=0; i<10; i++) {
    const r = a.rows[i];
    if (r.slot !== `268:${i}`) bad('order_or_slot');
    if (!/^https:\/\//.test(r.authored_url) || !/^https:\/\//.test(r.view_url)) bad('url');
    if (r.view_has_width_height !== false || r.view_has_srcset !== false) bad('source_markup_mutated');
    if (r.guest_http_status !== null || r.guest_decoded !== null || r.guest_current_src !== null || r.guest_transfer_bytes !== null || r.original_binary_sha256 !== null) bad('invented_evidence');
    if (r.pixel_crop_match_verified !== false || r.cache_approved !== false || r.wordpress_write_approved !== false || r.release !== 'HOLD') bad('release_bypass');
    if (r.source_type === 'COMMONS_FILE_REDIRECT') {
      counts.commons++;
      if (!r.authored_url.includes('/Special:Redirect/file/') || !r.file_page?.startsWith('https://commons.wikimedia.org/wiki/File:')) bad('commons_catalog');
      const g=r.native_catalog_dimensions, p=r.proposed_review_dimensions;
      if (!g || !p || !Number.isInteger(g.width) || !Number.isInteger(g.height) || g.width<1 || g.height<1 || g.not_decoded!==true || p.calculated!==true || p.width!==Math.min(960,g.width) || p.height!==Math.round(g.height*p.width/g.width) || p.width>g.width || p.height>g.height || p.width>960) bad('geometry_or_upscale');
      if (r.requested_query_width>960) counts.queryOver++;
      if (r.rights_claim==='COMMONS_CC_BY_2_VS_PROJECT_CC_BY_3' && r.item_license==='CC-BY-2.0' && r.project_bank_license==='CC-BY-3.0') counts.conflict++;
      else if (r.rights_claim==='COMMONS_PD_US_CLAIM' && r.item_license==='PD-US' && r.project_bank_license===null) counts.pd++;
      else bad('rights_claim');
    } else if (r.source_type === 'PROJECT_SITE_IMAGE') {
      counts.project++;
      if (!r.authored_url.includes('archimedespalimpsest.org/assets/img/') || r.file_page!==null || r.native_catalog_dimensions!==null || r.proposed_review_dimensions!==null || r.rights_claim!=='UNVERIFIED_PROJECT_JPG_ITEM' || r.item_license!==null) bad('invented_project_rights');
    } else bad('source_kind');
  }
  if (counts.commons!==6 || counts.project!==4 || counts.conflict!==5 || counts.pd!==1 || counts.queryOver!==2) bad('cohort');
  const s=a.summary||{};
  if (s.slots!==10 || s.commons!==6 || s.project_site!==4 || s.dual_license_claims!==5 || s.pd_claims!==1 || s.view_missing_dimensions!==10 || s.view_missing_srcset!==10 || s.requested_width_over_960!==2) bad('summary');
  if (a.program_baseline?.reported_broken_unconfirmed!==42 || a.program_baseline?.claimed_savings_percent_unmeasured!==76) bad('unverified_claims');
  return { ok:errors.length===0, errors, counts };
}
if (require.main===module) {
  const target=process.argv[2]||path.join(__dirname,'archimedes_268_ten_image_rights_geometry_20261116.json');
  const report=validate(JSON.parse(fs.readFileSync(target,'utf8')));
  console.log(JSON.stringify(report));
  process.exitCode=report.ok?0:1;
}
module.exports={validate};
