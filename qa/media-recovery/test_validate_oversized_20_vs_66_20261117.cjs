'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {readOversize,verifyOversize}=require('./validate_oversized_20_vs_66_20261117.cjs');
const base=readOversize();
function mutation(name,change) {
  test(name,()=>{
    const x=structuredClone(base);change(x);
    assert.throws(()=>verifyOversize(x.media,x.crosswalk,x.census));
  });
}
test('verified 20 decimal oversize records and 11 exact inline source matches',()=>{
  assert.deepEqual(verifyOversize(base.media,base.crosswalk,base.census),{oversized:20,inline_exact:11,not_inline_exact:9,stored_bytes:64385752});
});
mutation('reject changed 64 MB stored byte total',x=>x.media.summary.decimal_over_1_5MB_stored_bytes+=1);
mutation('reject 19/20 MiB unit confusion',x=>x.media.summary.binary_over_1_5MiB_count=20);
mutation('reject missing borderline Halifax item',x=>x.media.items.splice(x.media.items.findIndex(m=>m.id===1714),1));
mutation('reject invented visitor bytes',x=>x.crosswalk.items[0].visitor_network_bytes=100000);
mutation('reject fabricated rights clearance',x=>x.crosswalk.items[0].rights_for_reprocessing='CLEARED');
mutation('reject unapproved WordPress media action',x=>x.media.items[0].production_action='upload');
mutation('reject fabricated exact inline match',x=>x.crosswalk.items[0].inline_exact_origin_slots.push({slot_id:'1922:99'}));
mutation('reject missing legitimate exact inline match',x=>x.crosswalk.items.find(y=>y.id===388).inline_exact_origin_slots=[]);
mutation('reject false no-upscale derivative',x=>x.media.items[0].recommended_no_upscale_max960.width=1920);
mutation('reject mismatched responsive source data',x=>x.crosswalk.items.find(y=>y.id===388).inline_exact_origin_slots[0].has_srcset=false);
mutation('reject bad media original byte count',x=>x.media.items[0].original_bytes+=1);
mutation('reject a negative asset native width',x=>x.media.items[0].width=-1);
mutation('reject production writes in media ledger',x=>x.media.production_writes=1);
mutation('reject production writes in crosswalk',x=>x.crosswalk.production_writes=1);
mutation('reject a non-960 Jetpack option',x=>x.media.items.find(y=>y.existing_responsive_variants_at_or_under960.length).existing_responsive_variants_at_or_under960[0].width=2500);
