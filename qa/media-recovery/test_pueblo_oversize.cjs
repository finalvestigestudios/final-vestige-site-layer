'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),{load,validate}=require('./validate_pueblo_oversize.cjs');
const s=load(),dup=x=>structuredClone(x);
function run(edit){const x={p:dup(s.p),b:dup(s.b)};edit(x);return validate(x.p,x.b,s.ims,s.originals)}
test('full source and size crosswalk passes',()=>{const r=run(()=>{});assert.deepEqual(r.errors,[]);assert.equal(r.pueblo_images,6);assert.equal(r.oversize_originals,13);assert.deepEqual(r.distribution,[5,2,6])});
for(const [name,mut,expected] of [
 ['fabricated 404',x=>x.p.rows[0].browser_http_status=404,'fabricated_status'],
 ['fake image width',x=>x.p.rows[1].browser_natural_width_px=960,'fabricated_status'],
 ['false measured transfer',x=>x.p.rows[2].browser_transfer_bytes=1000,'fabricated_status'],
 ['false rights approval',x=>x.p.rows[0].rights_item_level_cleared=true,'rights_or_cms'],
 ['false WP approval',x=>x.p.rows[1].wp_upload_approved=true,'rights_or_cms'],
 ['unverified binary hash',x=>x.p.rows[2].original_image_binary_sha256='0'.repeat(64),'rights_or_cms'],
 ['Banner catalog overstated',x=>x.p.rows[4].match_evidence='catalog_id_in_source_url','banner_not_verified_exact'],
 ['missing precise ALT correction',x=>x.p.rows[3].editorial_alt_proposal=null,'one_crewman_correction'],
 ['altered canonical url',x=>x.p.rows[5].stored_source_url='https://example.org/a.jpg','image_snapshot'],
 ['invented 42 broken',x=>x.p.claim_42_broken_verified=true,'unsupported_broken_count'],
 ['invented 76 percent reduction',x=>x.b.claimed_76pct_measured=true,'unsupported_savings_claim'],
 ['misstated source size',x=>x.b.rows[0].original_storage_bytes=100,'oversize_snapshot'],
 ['fake WordPress variant status',x=>x.b.rows[3].variant_http_status=200,'invented_bytes_or_approval'],
 ['media derivative permission',x=>x.b.rows[4].approved_for_recompression=true,'invented_bytes_or_approval'],
 ['wrong computed 960 height',x=>x.b.rows[5].target_height_px=1,'unsafe_dimensions'],
 ['unapproved 1280 output',x=>x.b.rows[6].target_width_px=1280,'unsafe_dimensions'],
 ['false inline usage',x=>x.b.rows[7].inline_image_keys=['621:0'],'oversize_snapshot'],
 ['wrong priority',x=>x.b.rows[8].priority='P2_inline_variant_known_unverified','priority'],
 ['duplicate media ID',x=>x.b.rows[1].media_id=x.b.rows[0].media_id,'oversize_snapshot'],
])test('reject '+name,()=>{const r=run(mut);assert.equal(r.ok,false);assert.ok(r.errors.some(e=>e.includes(expected)),r.errors.join(','))});
