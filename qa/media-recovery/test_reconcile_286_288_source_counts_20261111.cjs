'use strict';
const test=require('node:test'), assert=require('node:assert/strict');
const {reconcile,parseCsv}=require('./reconcile_286_288_source_counts_20261111.cjs');
const a='https://i0.wp.com/www.squawkpoint.com/a.jpg',b='https://i0.wp.com/text-message.blogs.archives.gov/b.jpg';
const csv='post_id,stored_img_src_count,offsite_src_count\n285,3,1\n291,3,1\n407,3,1\n', sizes={posts:3,inline:9,qa:3,media:5};
function fixtures(){
 const row=(slot,stored_url)=>({slot,post_id:+slot.split(':')[0],stored_url,visitor_http:null,visitor_wire_bytes:null,visitor_broken:null});
 const ledger={rows:[row('285:1',a),row('285:2','https://external.test/a'),row('291:0',b),row('291:2','https://external.test/b'),row('407:0','https://external.test/c')]};
 const ex=(slot,post_id,src,origin)=>({slot,post_id,siteqa_offsite:1,media_offsite:2,exact_published_src:src,transport_host:'i0.wp.com',underlying_origin:origin,origin_http_status:null,guest_http_status:null,guest_wire_bytes:null,native_px:null,conditional_960px:null,maximum_derivative_width:960,never_upscale:true,exact_photo_identity_proven:false,rights_cleared:false,rehost_authorized:false});
 const audit={rows:[ex('285:1',285,a,'www.squawkpoint.com'),ex('291:0',291,b,'text-message.blogs.archives.gov')],release:{wordpress:false,homepage:false,image_download:false,cache:false,rewrite:false,deploy:false,spend:false}};
 return {ledger,audit};
}
function check(){const x=fixtures();return reconcile(csv,x.ledger,x.audit,sizes)}
function invalid(mutator,pattern){const x=fixtures();mutator(x);assert.throws(()=>reconcile(csv,x.ledger,x.audit,sizes),pattern)}
test('reconciles only 285 and 291 and preserves uncertainty',()=>{const r=check();assert.equal(r.other_posts_equal,1);assert.deepEqual(r.differences.map(x=>x.post_id),[285,291]);assert.equal(r.guest_http_verified,0)});
test('CSV duplicate detected',()=>assert.throws(()=>parseCsv(csv+'285,3,1\n'),/duplicate/));
test('CSV count overrun detected',()=>assert.throws(()=>parseCsv('post_id,stored_img_src_count,offsite_src_count\n285,1,2'),/invalid/));
test('source article cannot be swapped',()=>invalid(x=>x.ledger.rows[0].post_id=291,/binding/));
test('duplicate slots fail',()=>invalid(x=>x.ledger.rows[1].slot='285:1',/slot/));
test('browser 404 cannot be fabricated',()=>invalid(x=>x.ledger.rows[0].visitor_http=404,/fabricated/));
test('original URL cannot be swapped',()=>invalid(x=>x.ledger.rows[0].stored_url=b,/source_identity/));
test('proxy cannot point to own domain',()=>invalid(x=>{x.ledger.rows[0].stored_url=x.audit.rows[0].exact_published_src='https://i0.wp.com/finalvestige.com/a.jpg';x.audit.rows[0].underlying_origin='finalvestige.com'},/not_external/));
test('NARA photo rights cannot be assumed',()=>invalid(x=>x.audit.rows[1].rights_cleared=true,/rights_or_visual/));
test('native pixel dimensions must be observed',()=>invalid(x=>x.audit.rows[0].native_px=[1000,700],/invented/));
test('production change cannot be silently allowed',()=>invalid(x=>x.audit.release.wordpress=true,/unsafe/));
test('guest success cannot be silently entered',()=>invalid(x=>x.audit.rows[1].guest_http_status=200,/invented/));
test('incorrect QA count fails closed',()=>{const x=fixtures();assert.throws(()=>reconcile(csv.replace('407,3,1','407,3,0'),x.ledger,x.audit,sizes),/totals/)});
test('unexpected new missing slot fails closed',()=>{const x=fixtures();x.ledger.rows.pop();assert.throws(()=>reconcile(csv,x.ledger,x.audit,sizes),/cohort/)});
