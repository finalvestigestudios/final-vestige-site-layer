'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const path=require('node:path');
const {validate,load,httpsURL}=require('./validate_franklin_433_custody_20261114.cjs');
const file=path.join(__dirname,'franklin_433_custody_20261114.json');
const fresh=()=>structuredClone(load(file));
test('six-slot source custody remains HOLD',()=>assert.deepEqual(validate(fresh()),{result:'HOLD',checked:6,editorial_rights_conflict:['433:5'],guest_browser_evidence_available:false,production_change_authorized:false}));
test('reject unsafe URLs',()=>{assert.equal(httpsURL('http://a.test/x'),null);assert.equal(httpsURL('javascript:alert(1)'),null);assert.equal(httpsURL('https://user:pass@a.test/x'),null);assert.equal(httpsURL('https://a.test/x#fragment'),null);});
const mutations=[
 ['allow production writes',m=>m.release.allow_wordpress_production_writes=true],
 ['allow cache',m=>m.release.allow_asset_downloads_or_caches=true],
 ['allow autowrite',m=>m.release.allow_auto_replacement=true],
 ['remove CSS/DPR check',m=>m.release.require_actual_css_dpr=false],
 ['remove rollback',m=>m.release.require_reversible_stage=false],
 ['include homepage',m=>m.release.homepage_excluded=false],
 ['invent guest 404',m=>m.images[0].logged_out_browser_http_status=404],
 ['invent origin 200',m=>m.images[1].origin_http_status=200],
 ['claim broken guest',m=>m.images[2].confirmed_guest_broken=true],
 ['invent transfer size',m=>m.images[3].actual_transfer_bytes=42],
 ['invent browser currentSrc',m=>m.images[3].rendered_current_src=m.images[3].stored_url],
 ['claim binary matched',m=>m.images[5].candidate_binary_identity_verified=true],
 ['allow rehost',m=>m.images[5].rights_cleared_for_rehost=true],
 ['allow replacement',m=>m.images[5].production_replacement_approved=true],
 ['remove review hold',m=>m.images[2].review_hold=false],
 ['bless claimed 76 percent',m=>m.historical_baseline.actual_wire_reduction_percent=76],
 ['claim measured 42 failures',m=>m.historical_baseline.confirmed_guest_broken=42],
 ['make 399px image 960px',m=>m.images[2].conditional_960_no_upscale_px=[960,1444]],
 ['crop chart height',m=>m.images[3].conditional_960_no_upscale_px=[960,800]],
 ['change native dimensions',m=>m.images[0].native_px=[960,1000]],
 ['omit original slot',m=>m.images.pop()],
 ['duplicate slot',m=>m.images[1].slot='433:1'],
 ['change post',m=>m.published_post.id=434],
 ['wrong original host',m=>m.images[5].stored_url='https://lookalike.example/missing.jpg'],
 ['use HTTP source',m=>m.images[1].stored_url='http://upload.wikimedia.org/bad.jpg'],
 ['replace catalog with generic wiki article',m=>m.images[4].source_record_url='https://commons.wikimedia.org/wiki/Main_Page'],
 ['erase accessibility ALT',m=>m.images[1].alt=''],
 ['erase rights statement',m=>m.images[4].source_rights='PD'],
 ['claim FabTet photo is public-domain',m=>m.images[4].license_class='public_domain_asserted'],
 ['omit rights mismatch flag',m=>m.images[4].caption_license_mismatch=false],
 ['claim poster host cleared',m=>m.images[5].license_class='public_domain_asserted'],
 ['wrong portrait cap',m=>m.images[4].published_caption='Copyright status not proven'],
 ['wrong QA owner',m=>m.release.site_qa_cold_browser_owner=123],
];
for(const [name,change] of mutations)test('reject: '+name,()=>{const m=fresh();change(m);assert.throws(()=>validate(m));});
