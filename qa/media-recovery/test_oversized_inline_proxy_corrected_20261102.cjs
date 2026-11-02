'use strict';
/** Regression tests: source-level Vasa Jetpack repair, not a browser or upload test. */
const test=require('node:test');
const fs=require('node:fs'),path=require('node:path');
const {validate}=require('./validate_oversized_inline_proxy_corrected_20261102.cjs');
const load=f=>JSON.parse(fs.readFileSync(path.join(__dirname,f),'utf8'));
const inputs=[
 load('oversized_inline_proxy_corrected_20261102.json'),
 load('oversize_inline_reconciled_20261031.json'),
 load('oversized_inline_exposure_20261102.json'),
 load('parts/02.json')
];
const clone=x=>JSON.parse(JSON.stringify(x));
test('crosswalk validates 10/13 oversized inline originals and 3 Vasa proxies',()=>{
 const r=validate(...inputs);
 if(!r.ok)throw Error(JSON.stringify(r.errors));
 if(r.summary.inline_original_storage_bytes!==36937913)throw Error('wrong inline bytes');
});
const mutations=[
 ['proxy host spoof',x=>x.rows.find(r=>r.media_id===388).inline_slot_matches[0].stored_source_url=
   'https://i0.wp.com/notfinalvestige.com/wp-content/uploads/2026/08/vasa-modell-2020.jpg?fit=1024%2C681&ssl=1'],
 ['proxy selector appended',x=>x.rows.find(r=>r.media_id===388).inline_slot_matches[0].stored_source_url+='&file=other'],
 ['Vasa key swapped',x=>x.rows.find(r=>r.media_id===389).inline_slot_matches[0].image_key='299:6'],
 ['Vasa ALT changed',x=>x.rows.find(r=>r.media_id===389).inline_slot_matches[0].alt='A different ship'],
 ['imaginary browser 404',x=>x.rows[0].guest_http_status=404],
 ['imaginary 76 percent reduction',x=>x.summary.claimed_76_percent_wire_savings_measured=true],
 ['WordPress upload authorization forged',x=>x.rights_and_implementation_gates.wordpress_media_upload_authorized=true],
 ['image rights clearance forged',x=>x.rows[0].rights_cleared_for_derivative=true],
 ['unbounded upscale',x=>x.rows[0].conditional_derivative_px.width=6000],
 ['incorrect height',x=>x.rows[0].conditional_derivative_px.height=1],
 ['Vasa inline match removed',x=>x.rows.find(r=>r.media_id===382).inline_slot_matches=[]],
 ['original record omitted',x=>x.rows.pop()],
 ['original media ID duplicated',x=>x.rows[1].media_id=x.rows[0].media_id],
 ['original storage bytes altered',x=>x.rows[0].original_storage_bytes+=1],
 ['inline total corrupted',x=>x.summary.inline_original_storage_bytes+=1],
 ['unmatched media count reverted to 6',x=>x.summary.not_matched_inline_count=6],
 ['post corpus SHA replaced',x=>x.frozen_inputs.vasa_post_census.blob_sha='0'.repeat(40)],
 ['proxy origin path spoofed',x=>x.rows.find(r=>r.media_id===388).inline_slot_matches[0].stored_source_url=
   'https://i0.wp.com/finalvestige.com.evil.org/wp-content/uploads/2026/08/vasa-modell-2020.jpg?fit=1024%2C681&ssl=1'],
 ['rights gate weakened',x=>x.rights_and_implementation_gates.rights_review_required=false],
 ['Vasa erroneously marked unused',x=>x.rows.find(r=>r.media_id===388).inline_class='NOT_MATCHED_INLINE_IN_FROZEN_61_POSTS'],
 ['Malbone slot identity changed',x=>x.rows.find(r=>r.media_id===1258).inline_slot_matches[0].image_key='621:8'],
 ['fabricated transfer bytes',x=>x.rows[0].guest_encoded_wire_bytes=900],
 ['previous snapshot fingerprint removed',x=>x.frozen_inputs.direct_only_nov02.blob_sha='bad'],
 ['Vasa article destination changed',x=>x.rows.find(r=>r.media_id===388).inline_slot_matches[0].post_url='https://finalvestige.com/not-vasa/']
];
for(const [name,mutation]of mutations){
 test('rejects '+name,()=>{
  const copy=clone(inputs[0]);mutation(copy);
  const result=validate(copy,...inputs.slice(1));
  if(result.ok)throw Error('unsafe mutation accepted: '+name);
 });
}
