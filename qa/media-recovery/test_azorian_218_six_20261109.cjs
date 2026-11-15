'use strict';
const assert=require('assert');
const {validate}=require('./validate_azorian_218_six_20261109.cjs');
const audit=require('./azorian_218_six_source_20261109.json');
const clone=x=>JSON.parse(JSON.stringify(x));
assert.deepStrictEqual(validate(audit),[]);
let n=1;function neg(name,fn){const a=clone(audit);fn(a);assert.ok(validate(a).length,name);n++}
for(let i=0;i<6;i++){
 neg('url'+i,a=>a.rows[i].original_url+='#forged');
 neg('alt'+i,a=>a.rows[i].original_alt+=' FAKE');
 neg('browser broken'+i,a=>a.rows[i].visitor.confirmed_broken=true);
 neg('origin HTTP'+i,a=>a.rows[i].retriever.actual_origin_http=404);
 neg('wrong dimensions'+i,a=>a.rows[i].stage.conditional_catalog_px[1]++);
 neg('WP upload'+i,a=>a.rows[i].release.upload_wp=true);
}
neg('76pct',a=>a.census.transfer_76_pct_measured=true);
neg('cohort',a=>a.census.posts=66);
neg('extra',a=>a.rows.push(a.rows[0]));
neg('duplicate',a=>a.rows[1].slot=a.rows[0].slot);
neg('catalog',a=>a.rows[0].catalog.url='https://example.org/');
neg('catalog dims',a=>a.rows[3].catalog.catalog_native_dimensions_px=[4000,2400]);
neg('rights',a=>a.rows[4].stage.rights_cleared=true);
neg('cache',a=>a.rows[5].release.cache=true);
neg('upscale',a=>a.rows[2].stage.no_upscale=false);
neg('wire bytes',a=>a.rows[0].visitor.encoded_transfer_bytes=9281);
neg('fixture',a=>a.fixture.blob_sha='wrong');
neg('fake browser count',a=>a.retrieval_summary.actual_browser_http_observations=6);
neg('wrong post',a=>a.post.id=219);
neg('binary proof',a=>a.rows[5].stage.verified_binary_identity=true);
assert.equal(n,51);console.log(n+'/'+n+' Azorian positive and synthetic mutations PASS');
