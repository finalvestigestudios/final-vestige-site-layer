'use strict';
const {validate}=require('./validate_lady_be_good_278_20261107.cjs');
const base=require('./lady_be_good_278_source_audit_20261107.json');
const clone=()=>JSON.parse(JSON.stringify(base));
const cases=[
['wrong post',a=>a.post.id=290],
['wrong census',a=>a.frozen.img_refs=353],
['broken images falsely proven',a=>a.sitewide_status.alleged_broken_42='confirmed'],
['wire reduction falsely proven',a=>a.sitewide_status.claimed_transfer_reduction_76_percent='achieved'],
['original bytes wrong',a=>a.sitewide_status.thirteen_large_original_stored_bytes=0],
['unsafe WP write',a=>a.production_writes=true],
['download',a=>a.downloaded_media=true],
['duplicate QA',a=>a.site_qa_browser_collector_duplicated=true],
['slot missing',a=>a.images.pop()],
['wrong original URL',a=>a.images[0].source_url+='?bad'],
['HTML dimensions invented',a=>a.images[0].stored_width=1000],
['origin status invented',a=>a.images[0].independent_retriever.origin_http_status=403],
['browser 200 invented',a=>a.images[2].independent_retriever.guest_browser_http_status=200],
['decoded pixels invented',a=>a.images[2].independent_retriever.natural_width=1800],
['wire bytes invented',a=>a.images[2].independent_retriever.transferred_bytes=999],
['retriever status changed',a=>a.images[3].independent_retriever.outcome='ok'],
['uncleared copy',a=>a.images[4].candidate.copy_approved=true],
['false exact identity',a=>a.images[3].candidate.exact_image_match=true],
['unknown source pixels',a=>a.images[0].catalog_original_dimensions={width:960,height:500}],
['upscale',a=>a.images[2].conditional_preview.width=1920],
['crop drift',a=>a.images[2].conditional_preview.height=700],
['premature release',a=>a.images[5].release='APPROVED'],
['WordPress upload invented',a=>a.images[5].wp_attachment_id=42],
['ALT removed',a=>a.images[3].alt=''],
['canteen misleading',a=>a.images[3].fidelity_warning='fine'],
['NARA photo misdescribed',a=>a.images[5].fidelity_warning='fine']];
if(validate(clone()).length)throw Error('baseline fails');
let count=1;for(const [name,change] of cases){const x=clone();change(x);if(validate(x).length===0)throw Error('FAIL OPEN '+name);count++;}
console.log('PASS '+count+'/'+count+' exact-source regression scenarios');module.exports={count};
