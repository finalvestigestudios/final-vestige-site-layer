'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {validate}=require('./validate_pelee_413_loc_20261114.cjs');
const source=JSON.parse(fs.readFileSync(path.join(__dirname,'pelee_413_loc_20261114.json'),'utf8'));
const clone=()=>JSON.parse(JSON.stringify(source));
test('source custody control remains HOLD',()=>assert.deepEqual(validate(source),{ok:true,errors:[]}));
const reject=(name,mutate,code)=>test(name,()=>{let x=clone();mutate(x);const r=validate(x);assert.equal(r.ok,false);assert.ok(r.errors.some(e=>e.includes(code)),JSON.stringify(r));});
for(let i=0;i<4;i++){
reject('source URL mutation '+i,a=>a.rows[i].published_src+='?change','source_identity_drift');
reject('spurious guest 404 '+i,a=>a.rows[i].visitor_http_status=404,'invented_guest_http');
reject('spurious 960px dimensions '+i,a=>a.rows[i].native_width_px=960,'geometry_or_stereo_gate');
reject('false reuse rights '+i,a=>a.rows[i].right_to_rehost_cleared=true,'unauthorized_reuse');
reject('cropped stereo '+i,a=>a.rows[i].full_stereo_pair_required=false,'geometry_or_stereo_gate');
reject('unapproved caching '+i,a=>a.rows[i].cache_allowed=true,'unauthorized_reuse');
reject('wrong catalog '+i,a=>a.rows[i].loc_item='https://www.loc.gov/item/000/','source_identity_drift');
}
reject('cannot claim guest broken count',a=>a.summary.guest_broken_verified=3,'inaccurate_measurements');
reject('cannot claim 76% achieved',a=>a.summary.sitewide_76_percent='VERIFIED','inaccurate_measurements');
reject('cannot duplicate source record',a=>a.rows[1].slot=a.rows[0].slot,'duplicate_or_foreign_slot');
reject('must keep missing catalog explicitly missing',a=>a.rows[1].loc_item='https://www.loc.gov/item/123/','source_identity_drift');
reject('must not write production',a=>a.release.wp_prod_writes=1,'release_safety');
