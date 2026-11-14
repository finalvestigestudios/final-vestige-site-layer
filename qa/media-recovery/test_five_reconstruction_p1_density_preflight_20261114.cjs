'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {validate}=require('./validate_five_reconstruction_p1_density_preflight_20261114.cjs');
const baseline=JSON.parse(fs.readFileSync(path.join(__dirname,'five_reconstruction_p1_density_preflight_20261114.json'),'utf8'));
const cases=[
 ['extra release flag',a=>a.allow_upload=true],
 ['claim visitor wire measurement',a=>a.cohort.true_wire_bytes_measured=true],
 ['invent 76 percent',a=>a.historical_context.proposed_76pct_network_reduction_measured=true],
 ['change media ID',a=>a.items[0].media_id=40],
 ['swap original URL',a=>a.items[0].media_original_url=a.items[1].media_original_url],
 ['swap published image URL',a=>a.items[0].post_img_src=a.items[1].post_img_src],
 ['swap bytes preserving sum',a=>{a.items[0].original_stored_bytes+=100;a.items[1].original_stored_bytes-=100}],
 ['fabricate WordPress derivative',a=>a.items[0].wordpress_derivative_count=4],
 ['change published post',a=>a.items[0].post_id=38],
 ['fabricate guest HTTP 200',a=>a.items[0].verification.guest_browser_status=200],
 ['fabricate origin 404',a=>a.items[0].verification.origin_http_status=404],
 ['invent SHA',a=>a.items[0].verification.exact_source_hash='abc'],
 ['pretend binary obtained',a=>a.items[0].verification.binary_received=true],
 ['invent visitor bytes',a=>a.items[0].conditional_derivative.visitor_encoded_transfer_bytes=100],
 ['invent derivative bytes',a=>a.items[0].conditional_derivative.encoded_derivative_bytes=100],
 ['assume rights review',a=>a.items[0].conditional_derivative.rights_reviewed=true],
 ['approve production',a=>a.items[0].conditional_derivative.production_ready=true],
 ['claim scene parity',a=>a.items[0].conditional_derivative.visual_scene_parity_reviewed=true],
 ['claim visual QA',a=>a.items[0].conditional_derivative.quality_reviewed=true],
 ['resize above cap',a=>a.items[0].conditional_derivative.width_px=1024],
 ['distort aspect',a=>a.items[0].conditional_derivative.height_px=541],
 ['invent DPR reading',a=>a.items[0].conditional_derivative.actual_device_pixel_ratio=2],
 ['misstate 2x CSS width',a=>a.items[0].conditional_derivative.css_width_at_2x_max_px=960],
 ['misstate 3x CSS width',a=>a.items[0].conditional_derivative.css_width_at_3x_max_px=960],
 ['strip reconstruction caption',a=>a.items[0].post_figcaption='Historical photograph'],
 ['claim documentary',a=>a.items[0].source_kind='ARCHIVAL_PHOTOGRAPH'],
 ['remove source disclosure',a=>a.items[0].media_description='A historical photograph'],
 ['allow WordPress write',a=>a.policy.wp_production_write=true],
 ['allow cache or rehost',a=>a.policy.media_download_or_rehost_approval=true],
 ['allow archival substitution',a=>a.policy.no_new_archive_photo_substitution=false],
 ['bypass Site QA P0',a=>a.policy.follow_existing_six_p0_first=false],
 ['change cohort count',a=>a.cohort.images=4],
 ['rewrite HTML width',a=>a.items[0].post_img_width_attr_px=960],
 ['unexpected permission',a=>a.items[0].conditional_derivative.wp_write=true],
 ['invent browser trust field',a=>a.items[0].verification.chrome_broken=true],
 ['claim 42 verified',a=>a.historical_context.historical_reported_broken_unverified=0],
 ['change origin',a=>a.items[3].media_original_url='https://unauthorized.example/photo.png'],
 ['change bytes and total',a=>{a.items[3].original_stored_bytes++;a.cohort.original_stored_bytes++}]
];
assert.equal(validate(baseline).ok,true,'normal control');
for(const [name,mutate] of cases){const a=JSON.parse(JSON.stringify(baseline));mutate(a);assert.throws(()=>validate(a),/HOLD:/,name);}
console.log(JSON.stringify({ok:true,controls:1,adversarial:cases.length,total:cases.length+1}));

