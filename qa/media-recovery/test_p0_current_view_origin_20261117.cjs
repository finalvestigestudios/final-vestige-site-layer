'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {verifyCrosswalk,loadPinned}=require('./validate_p0_current_view_origin_20261117.cjs');
const fixture=JSON.parse(fs.readFileSync(path.join(__dirname,'p0_current_view_origin_20261117_1832pt.json'),'utf8'));
const slices=loadPinned();const copy=x=>JSON.parse(JSON.stringify(x));
assert.equal(verifyCrosswalk(fixture,slices).status,'SOURCE_ONLY_HOLD');let n=1;
const mutations=["fabricated visitor GET","false source right","unsafe WordPress upload","unsafe rehosting","unsafe Gutenberg rewrite","invented 76pct result","invented 42 failures","tool 500 wrongly called origin","tool 400 wrongly called origin","wrong encoded exact probe","pretend percent-encoding identical","wrong VIEW src","wrong ALT","wrong source revision","bad crop geometry","preview upscale 600 to 800","preview beyond 960","missing priority slot","wrong host category","fake binary hash","duplicate key","incorrect response totals","invented paid media"];
const changes=[
 r=>r.slots[0].visitor.final_http=404,
 r=>r.slots[0].rights='APPROVED',
 r=>r.slots[0].wp_write_allowed=true,
 r=>r.slots[0].rehost_allowed=true,
 r=>r.slots[0].post_rewrite_allowed=true,
 r=>r.summary.verified_76_percent_wire_savings=true,
 r=>r.summary.guest_confirmed_failures=42,
 r=>r.slots[1].probe.status=500,
 r=>r.slots[5].probe.status=400,
 r=>r.slots[0].probe.requested_url=r.slots[0].previous_probe_url,
 r=>r.slots[0].previous_probe_was_exact=true,
 r=>r.slots[1].authored_view_src='https://i0.wp.com/bad.com/a.jpg',
 r=>r.slots[2].alt='other image',
 r=>r.slots[3].view_revision='2000',
 r=>r.slots[0].candidate.target_px.height=700,
 r=>r.slots[4].candidate.target_px.width=800,
 r=>r.slots[4].candidate.target_px.width=961,
 r=>r.slots.pop(),
 r=>r.slots[1].source_route='third_party_direct',
 r=>r.slots[0].candidate.binary_sha256='123',
 r=>r.slots[5].slot='285:5',
 r=>r.summary.public_origin_numeric_http_errors=6,
 r=>r.summary.subscription_spend_usd=1
];
for(let i=0;i<changes.length;i++){const r=copy(fixture);changes[i](r);assert.throws(()=>verifyCrosswalk(r,slices),Error,mutations[i]);n++;}
let s=copy(slices);s[0].posts[0].view_modified='2000';assert.throws(()=>verifyCrosswalk(fixture,s));n++;
s=copy(slices);s[0].images[0].visitor_http_status=404;assert.throws(()=>verifyCrosswalk(fixture,s));n++;
console.log('PASS '+n+'/'+n+' native Node fail-closed cases, source blob pins loaded');
