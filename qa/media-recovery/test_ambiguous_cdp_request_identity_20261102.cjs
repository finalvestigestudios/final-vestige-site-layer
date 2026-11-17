'use strict';
/**
 * Browser Image request disambiguation: synthetic CDP records, NOT live failures.
 * Distinct Chrome Image request IDs to the same normalized historical photo
 * cannot be assigned to one DOM element by choosing the last response.
 */
const {test}=require('node:test'),assert=require('node:assert/strict');
const {classifyImages}=require('./browser_probe_core.cjs');
const {proofKind}=require('./image_census_coverage_core.cjs');
const {scopeByRequestId}=require('./request_id_wire_core.cjs');
const src='https://archive.example.gov/1946-scotch-cap.jpg';
const original=[{key:'418:2',source_url:src,alt:'1946 remains of Scotch Cap'}];
const dom=(w=0,url=src)=>[{index:0,src:url,currentSrc:url,alt:original[0].alt,
 complete:true,naturalWidth:w}];
const req=(id,status=200,url=src)=>({request_id:id,type:'Image',url,status,
 mime_type:'image/jpeg',encodedDataLength:5000,was_cached:false,
 from_disk_cache:false,from_service_worker:false,url_aliases:[]});
const scan=(rows,width=0,domUrl=src,sources=original)=>
 classifyImages(sources,dom(width,domUrl),rows,true)[0];
test('one unambiguous Image 404 with zero-width DOM still proves a broken photo',()=>{
 const x=scan([req('22.1',404)]);
 assert.equal(x.result,'confirmed_broken_in_probe_browser');
 assert.equal(x.request_id,'22.1');assert.equal(x.matching_cdp_image_request_count,1);
 assert.equal(proofKind(x),'broken');
});
test('two conflicting Image statuses for same source cannot fabricate a 404',()=>{
 const x=scan([req('22.1',200),req('22.2',404)]);
 assert.equal(x.result,'ambiguous_network_request_identity');
 assert.equal(x.verified_broken_in_browser,null);
 assert.equal(x.visual_failure_kind,null);assert.equal(x.http_status,null);
 assert.equal(x.ambiguous_network_request_identity,true);
 assert.equal(x.matching_cdp_image_request_count,2);
 assert.equal(proofKind(x),'unresolved');
});
test('two 403s at same URL do NOT determine which CDP request belongs to DOM',()=>{
 const x=scan([req('22.1',403),req('22.2',403)]);
 assert.equal(x.result,'ambiguous_network_request_identity');
 assert.equal(x.verified_broken_in_browser,null);
});
test('two 200 image responses with decoded pixels cannot prove article-only transfer',()=>{
 const rows=[req('22.1',200),req('22.2',200)];
 const x=scan(rows,960);
 assert.equal(x.result,'ambiguous_network_request_identity');
 assert.equal(x.verified_broken_in_browser,null);
 const wire=scopeByRequestId([x],rows.map(r=>({...r,encoded_data_length:r.encodedDataLength})));
 assert.equal(wire.article_bytes,null);
});
test('different resizing URLs normalize to same photo and remain ambiguous',()=>{
 const x=scan([req('22.1',200,src+'?width=960'),req('22.2',404,src+'?width=1200')]);
 assert.equal(x.result,'ambiguous_network_request_identity');
 assert.equal(x.matching_cdp_image_request_count,2);
});
test('historically different crop remains a different scene, no false collision',()=>{
 const top=src+'?crop=top',bottom=src+'?crop=bottom';
 const source=[{key:'418:2',source_url:top,alt:original[0].alt}];
 const x=scan([req('22.1',200,top),req('22.2',404,bottom)],960,top,source);
 assert.equal(x.result,'loaded_in_probe_browser');assert.equal(x.request_id,'22.1');
 assert.equal(x.matching_cdp_image_request_count,1);
});
test('unrelated second image does not invalidate unique source evidence',()=>{
 const x=scan([req('22.1',200),req('22.2',404,'https://example.org/logo.jpg')],960);
 assert.equal(x.result,'loaded_in_probe_browser');
 assert.equal(x.matching_cdp_image_request_count,1);
});
test('one redirect chain remains one CDP request after Map deduplication',()=>{
 const from='https://commons.wikimedia.org/wiki/Special:Redirect/file/Scotch_Cap.jpg';
 const to='https://upload.wikimedia.org/wikipedia/commons/1/12/Scotch_Cap.jpg';
 const source=[{key:'418:2',source_url:from,alt:original[0].alt}];
 const x=scan([ {...req('22.1',200,to),url_aliases:[from]} ],960,from,source);
 assert.equal(x.result,'loaded_in_probe_browser');
 assert.equal(x.matching_cdp_image_request_count,1);
});
test('missing CDP Image records remains unverified rather than falsely broken',()=>{
 const x=scan([]);
 assert.equal(x.result,'zero_intrinsic_width_needs_review');
 assert.equal(x.verified_broken_in_browser,null);
 assert.equal(x.matching_cdp_image_request_count,0);
});
