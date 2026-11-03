'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),{validate}=require('./validate_five_png_no_subsizes_20261103.cjs');
const source=JSON.parse(fs.readFileSync(path.join(__dirname,'five_png_no_subsizes_live_wp_20261103.json'),'utf8'));
const copy=()=>JSON.parse(JSON.stringify(source));
test('real five-media authenticated snapshot validates',()=>assert.equal(validate(copy()).ok,true));
const mutations=[
 ['invented 76% saving',v=>v.sitewide_context.claimed_76_percent_page_transfer_saving_measured=true],
 ['invented forty-two broken',v=>v.sitewide_context.founder_reported_42_broken_browser_verified=42],
 ['invented production repair',v=>v.sitewide_context.production_media_repairs=1],
 ['original as browser bytes',v=>v.rows[0].guest_encoded_transfer_bytes=v.rows[0].media_original_bytes],
 ['fabricated image HTTP 200',v=>v.rows[0].guest_http_status=200],
 ['fabricated image decode',v=>v.rows[0].guest_decoded=true],
 ['fabricated savings',v=>v.rows[1].measured_savings_bytes=1],
 ['fake installed size',v=>v.rows[1].media_registered_sizes_count=1],
 ['wrong original geometry',v=>v.rows[2].media_dimensions_px.width=1024],
 ['made-up CDN srcset',v=>v.rows[3].published_img_has_srcset=true],
 ['asset not AI-labelled',v=>v.rows[3].published_figcaption='Historical photo'],
 ['incorrect media source',v=>v.rows[2].published_img_source_url='https://elsewhere.example/foo.png'],
 ['false user rights clearance',v=>v.rows[0].rights_ownership_and_tool_terms_cleared=true],
 ['false derivative approval',v=>v.rows[4].derivative_authorized=true],
 ['WordPress production write',v=>v.rows[0].wordpress_production_write_authorized=true],
 ['forged 960->1200 derivative',v=>v.rows[0].conditional_max_width_px=1200],
 ['altered batch storage bytes',v=>v.batch.original_storage_bytes=100],
 ['changed first id',v=>v.rows[0].media_id=44],
 ['duplicate row',v=>v.rows[4]=JSON.parse(JSON.stringify(v.rows[0]))],
 ['reconstruction absent in library',v=>v.rows[3].media_library_alt='Old photograph'],
 ['forgot post featured-media link',v=>v.rows[1].featured_media_id=null],
 ['invented currentSrc',v=>v.rows[4].guest_current_src=v.rows[4].published_img_source_url],
 ['wrong mime',v=>v.rows[4].media_mime='image/jpeg'],
 ['lost source disclaimer',v=>v.batch.stored_originals_are_not_visitor_transfer_bytes=false],
 ['no rights review gate',v=>v.safety.licensed_republication_assumed=true]
];
for(const [title,mutate] of mutations)test('reject '+title,()=>{const x=copy();mutate(x);assert.equal(validate(x).ok,false,title)});
