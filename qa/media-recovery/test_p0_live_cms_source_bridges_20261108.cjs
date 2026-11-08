'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {validate}=require('./validate_p0_live_cms_source_bridges_20261108.cjs');
const audit=require('./p0_live_cms_3_source_bridges_20261108.json');
const clone=()=>JSON.parse(JSON.stringify(audit));
test('real live CMS source audit passes',()=>assert.equal(validate(clone()).ok,true));
const mutations=[
 ["drop slot",x=>x.rows.pop()],
 ["duplicate slot",x=>x.rows[1]=x.rows[0]],
 ["source swap",x=>x.rows[0].original="https://example.org/wrong.jpg"],
 ["alter ALT",x=>x.rows[1].alt="other"],
 ["pretend loaded",x=>x.rows[0].visitor_broken=false],
 ["claim guest 404",x=>x.rows[1].visitor_http_status=404],
 ["claim wrapper origin",x=>x.rows[0].retriever.origin_http=true],
 ["claim wrapper visitor",x=>x.rows[1].retriever.visitor_http=true],
 ["invent network bytes",x=>x.rows[2].visitor_transfer_bytes=300],
 ["invent hash",x=>x.rows[0].source_binary_sha256="a".repeat(64)],
 ["pretend exact source pixels",x=>x.rows[0].candidate.binary_match=true],
 ["clear secondary rights",x=>x.rows[0].candidate.license_proven=true],
 ["clear publisher rights",x=>x.rows[1].candidate.rights_status="CLEAR"],
 ["claim USGS rendered now",x=>x.rows[2].candidate.evidence="IMAGE_DISPLAYED"],
 ["omit NOAA conflict",x=>x.rows[0].candidate.scene_note="1946 photo"],
 ["upscale",x=>x.rows[0].derive.max_width=1200],
 ["fake dimensions",x=>x.rows[0].derive.native_px=[700,500]],
 ["fake derivative",x=>x.rows[1].derive.target_px=[960,600]],
 ["allow upload",x=>x.rows[0].cache_or_wp_edit_authorized=true],
 ["allow WP writes",x=>x.permissions.cms_write=true],
 ["allow rehost",x=>x.permissions.image_rehost=true],
 ["allow subscription",x=>x.permissions.spend=true],
 ["declare 42 broken",x=>x.baseline.reported_broken_42="CONFIRMED"],
 ["declare 76% savings",x=>x.baseline.measured_76pct_reduction=true],
 ["invent transfer total",x=>x.baseline.measured_visitor_image_transfer_bytes=240],
 ["falsify site inventory",x=>x.baseline.historic_images=354],
 ["falsify storage",x=>x.baseline.oversize_original_storage_bytes=1],
 ["falsify retrieved status",x=>x.rows[0].retriever.code=200],
 ["flip live status",x=>x.rows[2].status="draft"],
 ["change candidate URL",x=>x.rows[0].candidate.url="https://example.org/new.jpg"],
];
for(const [name,change] of mutations)test('reject '+name,()=>{const d=clone();change(d);assert.equal(validate(d).ok,false,name)});
