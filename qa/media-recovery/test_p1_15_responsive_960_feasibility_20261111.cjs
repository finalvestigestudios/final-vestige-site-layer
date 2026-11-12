'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const base=require('./p1_15_responsive_960_feasibility_20261111.json');
const {inspect}=require('./validate_p1_15_responsive_960_feasibility_20261111.cjs');
const copy=()=>JSON.parse(JSON.stringify(base));
const change=(description,fn)=>test(description,()=>{const x=copy();fn(x);assert.equal(inspect(x).pass,false)});
test('exact 15 original rows and 11 inline subset validate',()=>assert.equal(inspect().pass,true));
test('pinned original 15 store 47096779 B, 11 inline store 38480915 B',()=>{
 assert.equal(base.counts.original_bytes_total,47096779);assert.equal(base.counts.inline_exposed_original_bytes,38480915);
});
test('five 1672x941 PNGs have no registered subsizes and exceed conditional width',()=>{
 const five=base.rows.filter(r=>[39,40,41,42,43].includes(r.media_id));
 assert.equal(five.length,5);for(const r of five){assert.equal(r.generated_wp_subsize_count,0);assert.equal(r.html_width_attribute_hint_px,1024);assert.equal(r.conditional_no_upscale_960px[0],960);assert.equal(r.conditional_max_css_width_px_at_dpr_2,480)}
});
test('15 output width and height stay within native and preserve original ratio',()=>{
 for(const r of base.rows){const [w,h]=r.conditional_no_upscale_960px;assert.ok(w<=960&&w<=r.native_px[0]);assert.equal(h,Math.round(r.native_px[1]*w/r.native_px[0]));}
});
test('P0 recovery order cannot be replaced with a P1 performance sprint',()=>assert.equal(base.p0_first.site_qa_existing_order.join(','),'285:5,285:2,287:5,418:1,418:2,407:1'));
test('four not-mapped-inline images cannot be declared unused site-wide',()=>{
 const rows=base.rows.filter(r=>r.published_inline_post_ids.length===0);
 assert.equal(rows.length,4);assert.ok(rows.every(r=>r.recommendation.includes('CHECK_FEATURED_PAGES')));
});
change('fake actual transfer percent is forbidden',a=>a.performance.actual_reduction_percent=76);
change('invented browser status is forbidden',a=>a.rows[0].actual_guest_http_status=200);
change('invented visitor currentSrc is forbidden',a=>a.rows[0].actual_browser_selected_current_src=a.rows[0].original_url);
change('invented true 42 broken count is forbidden',a=>a.cohorts.reported_broken_42_guest_verified=true);
change('unauthorized derivative created is forbidden',a=>a.rows[0].output_binary_created=true);
change('WordPress write permission cannot be introduced',a=>a.staging_contract.wordpress_production_writes=true);
change('binary image download cannot be introduced',a=>a.staging_contract.third_party_binary_downloads=true);
change('cannot remove rights approval',a=>a.staging_contract.rights_and_editorial_approval_required=false);
change('cannot allow item reuse by assertion',a=>a.rows[0].commercial_reuse_cleared=true);
change('cannot preapprove exact historical scene',a=>a.rows[0].exact_scene_cleared=true);
change('cannot preapprove layout',a=>a.rows[0].layout_approved=true);
change('cannot add production authority',a=>a.rows[0].production_edit_allowed=true);
change('cannot forge WordPress subsize count',a=>a.rows[0].generated_wp_subsize_count=8);
change('cannot claim a 960 source covers 1024 CSS px at 2x',a=>a.rows.find(r=>r.media_id===39).retina_2x_safe_at_html_width_hint=true);
change('cannot forge native source dimensions',a=>a.rows[0].native_px=[960,960]);
change('cannot forge conditional output dimensions',a=>a.rows[0].conditional_no_upscale_960px=[960,960]);
change('cannot forge CSS 2x maximum',a=>a.rows[0].conditional_max_css_width_px_at_dpr_2=960);
change('cannot mismatch 3x density ceiling',a=>a.rows[0].conditional_max_css_width_px_at_dpr_3=960);
change('cannot replace original source with arbitrary photo',a=>a.rows[0].original_url='https://example.org/unrelated.jpg');
change('cannot invent stored bytes',a=>a.rows[0].stored_original_bytes=1);
change('cannot alter historic 61 to expanded 66',a=>a.cohorts.historical_posts=66);
change('cannot promote 76 percent estimate into measured',a=>a.performance.proposed_76_percent_transfer_reduction_unmeasured=false);
change('cannot mutate P0 order',a=>a.p0_first.site_qa_existing_order.reverse());
change('cannot mutate source blob SHA',a=>a.source_custody.git_blob_sha='0'.repeat(40));
change('cannot silently remove media',a=>a.rows.pop());
change('cannot duplicate media ids',a=>a.rows[1].media_id=a.rows[0].media_id);
change('cannot delete original rights observation',a=>a.rows[0].item_rights_review='PUBLIC_DOMAIN_APPROVED');
change('cannot reclassify non-inline image as safe to delete',a=>a.rows.find(r=>r.published_inline_post_ids.length===0).recommendation='SAFE_TO_DELETE');
change('cannot claim hypothetical 960px derivative already exists',a=>a.staging_contract.derivatives_are_only_hypothetical=false);
