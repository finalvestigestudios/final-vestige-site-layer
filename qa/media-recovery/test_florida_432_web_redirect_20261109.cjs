'use strict';
const {test}=require('node:test');const assert=require('node:assert/strict');const {readFileSync}=require('node:fs');const {join}=require('node:path');
const {validate}=require('./validate_florida_432_web_redirect_20261109.cjs');
const base=JSON.parse(readFileSync(join(__dirname,'florida_432_seven_web_redirect_20261109.json'),'utf8'));
test('seven real WP source URLs and exact official catalog IDs',()=>assert.deepEqual(validate(base),[]));
const mutations={
  "real-browser-status": a=>a.rows[0].web_open.guest_chrome_status=500,
  "origin-status": a=>a.rows[0].web_open.origin_status=500,
  "browser-broken": a=>a.rows[1].web_open.guest_broken=true,
  "invented-bytes": a=>a.rows[1].web_open.guest_encoded_bytes=100,
  "invented-dimensions": a=>a.rows[1].candidate.conditional_960px_dimensions=[960,640],
  "premature-license": a=>a.rows[0].candidate.rights_cleared=true,
  "premature-publish": a=>a.rows[6].candidate.publish=true,
  "premature-download": a=>a.rows[6].candidate.downloaded=true,
  "false-seven-outages": a=>a.scope.not_seven_independent_outages=false,
  "bad-original-source": a=>a.rows[0].wp_published_src="https://malicious.example/foo.jpg",
  "alter-archive": a=>a.rows[2].identifier="PR04493",
  "change-canonical": a=>a.rows[0].conditional_canonical_origin_url="https://other.example/image.jpg",
  "bad-wrapper-code": a=>a.rows[4].web_open.wrapper_status=404,
  "invented-rights": a=>a.rights.blank_catalog_rights_field_is_permission=true,
  "image-rights-release": a=>a.rights.cache_or_republish_approved=true,
  "fake-measured-weight": a=>a.performance.verified_wire_bytes=123,
  "fake-960-file": a=>a.performance.actual_960_derivatives=["960x720"],
  "wp-write": a=>a.release.wordpress_writes=1,
  "wrong-link-target": a=>a.rows[5].source_href_catalog_verified=true,
  "duplicate": a=>a.rows[1].slot="432:0",
  "missing": a=>a.rows.pop(),
};
for(const [name,mutate] of Object.entries(mutations))test('fail closed: '+name,()=>{const a=structuredClone(base);mutate(a);assert.ok(validate(a).length>0,name)});
