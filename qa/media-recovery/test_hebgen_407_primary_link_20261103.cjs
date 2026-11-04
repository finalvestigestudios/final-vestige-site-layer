"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const {validateHebgenPrimary}=require("./validate_hebgen_407_primary_link_20261103.cjs");
const audit=JSON.parse(fs.readFileSync(path.join(__dirname,"hebgen_407_primary_path_audit_20261103.json"),"utf8"));
const part=JSON.parse(fs.readFileSync(path.join(__dirname,"parts/02.json"),"utf8"));
const mutations=[
 ["invented visitor 404",a=>a.rows[1].guest_http_status=404],
 ["invented origin 200",a=>a.rows[1].numeric_origin_http_status=200],
 ["invented image pixels",a=>a.rows[1].guest_natural_width=1000],
 ["invented currentSrc",a=>a.rows[1].guest_current_src="https://example.com/picture.jpg"],
 ["fabricated transfer",a=>a.rows[1].transferred_bytes=1200],
 ["unapproved WP edit",a=>a.rows[1].rights.wordpress_edit_approved=true],
 ["unapproved cache",a=>a.rows[1].rights.local_cache_approved=true],
 ["unreviewed copyright",a=>a.rows[1].rights.specific_rights_and_attribution_check="APPROVED"],
 ["fake original SHA",a=>a.rows[1].rights.master_binary_sha256="fake"],
 ["premature release",a=>a.rows[1].release_gate.production_authorized=true],
 ["no browser proof",a=>a.rows[1].release_gate.needs_guest_chrome_currentSrc_http_mime_decode=false],
 ["false 42 figure",a=>a.observation_limits.claimed_42_broken_images_verified=true],
 ["false 76 savings",a=>a.observation_limits.claimed_76_percent_savings_measured=true],
 ["fabricated browser bytes",a=>a.observation_limits.actual_browser_transfer_bytes=1234],
 ["pretend live WordPress read",a=>a.observation_limits.live_wordpress_read_this_run=true],
 ["published source swapped",a=>a.rows[1].source_url="https://example.com/foo.jpg"],
 ["published ALT swapped",a=>a.rows[1].source_alt="wrong photo"],
 ["candidate scene swap",a=>a.rows[1].archive.usgs_catalog_original_url="https://example.com/other.jpg"],
 ["silent 407:1 drift removal",a=>a.rows[1].archive.usgs_catalog_original_url=a.rows[1].source_url],
 ["wrong 407:1 archive location",a=>a.rows[1].archive.usgs_catalog_original_url=a.rows[1].archive.usgs_catalog_original_url.replace("thumbnails/image/","thumbnails/")],
 ["catalog domain swap",a=>a.rows[3].archive.catalog_url="https://archive.example.org"],
 ["new source identity count",a=>a.findings.exact_usgs_archive_original_link_matches=8],
 ["unsourced aspect geometry",a=>a.rows[2].geometry.conditional_aspect_preserving_height=780],
 ["false intrinsic binary check",a=>a.rows[2].geometry.original_binary_dimensions_verified=true],
 ["dropped slot",a=>a.rows.pop()],
 ["duplicated slot",a=>a.rows[6].key="407:5"],
 ["pinned frozen blob changed",a=>a.frozen_census.git_blob_sha="00000"],
 ["viewer swapped for 407:3",a=>a.rows[3].independent_source_observation="RETRIEVER_INACCESSIBLE_NO_STATUS"],
 ["original link mismatch for 407:4",a=>a.rows[4].archive.usgs_catalog_original_url="https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7536.jpg"],
];
assert.equal(validateHebgenPrimary(audit,part).ok,true,"valid eight-slot pinned USGS audit");
let count=1;
for(const [name,mutate] of mutations){
 const change=structuredClone(audit);mutate(change);
 const output=validateHebgenPrimary(change,part);
 assert.equal(output.ok,false,name+" should fail closed");
 count++;
}
console.log(count+" Hebgen primary-source/URL/status/release checks PASS");
