'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const {selectCdpImageRequests}=require('./cdp_image_request_scope.cjs');
const src='https://archive.example.gov/photograph.jpg';
const image=(overrides={})=>({url:src,type:'Image',status:200,mime_type:'image/jpeg',encodedDataLength:2000,...overrides});
test('actual Image response retained with URL, MIME, status, and byte evidence',()=>{
 const r=image();assert.deepEqual(selectCdpImageRequests([r]),[r]);
});
test('XHR and Fetch sharing the image URL cannot certify that an image loaded',()=>{
 const got=selectCdpImageRequests([image({type:'XHR'}),image({type:'Fetch'})]);
 assert.equal(got.length,0);
});
test('Document and Script fetches returning image/jpeg cannot certify image requests',()=>{
 assert.deepEqual(selectCdpImageRequests([image({type:'Document'}),image({type:'Script'})]),[]);
});
test('CDP Other, Preflight, WebSocket and missing-type records fail closed',()=>{
 assert.equal(selectCdpImageRequests(['Other','Preflight','WebSocket',null].map(t=>image({type:t}))).length,0);
});
test('genuine image HTTP 403 and network failure still reach the classifier',()=>{
 const rows=[image({status:403,encodedDataLength:0}),image({status:null,failed_error:'net::ERR_ABORTED'})];
 assert.deepEqual(selectCdpImageRequests(rows),rows);
});
test('unrelated 200 Fetch cannot overshadow a genuine 404 Image on same URL',()=>{
 const rows=[image({status:404}),image({type:'Fetch',status:200})];
 const selected=selectCdpImageRequests(rows);
 assert.equal(selected.length,1);assert.equal(selected[0].status,404);
});
test('redirect aliases stay intact when the final resource is Image',()=>{
 const rows=[image({url:'https://upload.wikimedia.org/wikipedia/commons/a/aa/photo.jpg',url_aliases:[src]})];
 assert.deepEqual(selectCdpImageRequests(rows)[0].url_aliases,[src]);
});
test('non-http images and missing URLs are not fabricated into valid network evidence',()=>{
 assert.equal(selectCdpImageRequests([image({url:'data:image/png;base64,AAAA'}),image({url:''}),image({url:null})]).length,0);
});
test('two independently requested images remain distinct request records',()=>{
 const rows=[image({encodedDataLength:2000}),image({encodedDataLength:3000})];
 assert.equal(selectCdpImageRequests(rows).length,2);
});
test('input array and individual request objects are not modified',()=>{
 const r=image();const rows=[r,image({type:'Fetch'})];
 const selected=selectCdpImageRequests(rows);
 assert.equal(rows.length,2);assert.equal(selected[0],r);assert.equal(r.encodedDataLength,2000);
});
test('invalid or missing record collections are handled conservatively',()=>{
 assert.deepEqual(selectCdpImageRequests(null),[]);
 assert.deepEqual(selectCdpImageRequests({url:src,type:'Image'}),[]);
 assert.deepEqual(selectCdpImageRequests([null,{},undefined]),[]);
});
