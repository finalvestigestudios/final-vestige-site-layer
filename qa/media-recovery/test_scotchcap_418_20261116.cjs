"use strict";
const test=require("node:test");
const assert=require("node:assert/strict");
const {assess}=require("./validate_scotchcap_418_20261116.cjs");
const original=require("./scotchcap_418_six_source_custody_20261116_1930pt.json");
const clone=()=>JSON.parse(JSON.stringify(original));
test("pinned source manifest passes as HOLD, not production approval",()=>{const r=assess(clone());assert.equal(r.decision,"HOLD");assert.deepEqual(r.errors,[]);});
const cases=[
["false visitor 404",d=>d.rows[1].guest_http_status=404],
["false visitor 200",d=>d.rows[2].guest_http_status=200],
["fabricated browser currentSrc",d=>d.rows[2].guest_current_src="https://example.org/x"],
["fake decode",d=>d.rows[3].guest_decoding_success=true],
["fake wire bytes",d=>d.rows[5].guest_transfer_bytes=400],
["fake MIME",d=>d.rows[4].guest_mime_type="image/jpeg"],
["fake source HTTP status",d=>d.rows[1].source_http_status=403],
["fake 42 confirmed",d=>d.historical_census.guest_confirmed_broken=42],
["fake 76 percent measured",d=>d.historical_census.measured_wire_reduction_percent=76],
["stored bytes mistaken for visitor",d=>d.historical_census.visitor_bytes_for_oversized=64385752],
["wrong original",d=>d.rows[1].authored_url="https://example.org/portrait.jpg"],
["wrong proxy",d=>d.rows[5].jetpack_view_url="https://i0.wp.com/example.org/no.jpg?ssl=1"],
["wrong official catalog",d=>d.rows[1].catalog_url=d.rows[2].catalog_url],
["wrong candidate binary",d=>d.rows[2].asset_url=d.rows[3].asset_url],
["fabricated frame equality",d=>d.rows[0].exact_frame_verified=true],
["fabricated SHA",d=>d.rows[5].candidate_sha256="f".repeat(64)],
["fake decoded source dimensions",d=>d.rows[5].native_candidate_dimensions_verified=true],
["fake observed source size",d=>d.rows[1].measured_candidate_binary_bytes=40000],
["unauthorized wordpress upload",d=>d.rows[1].wordpress_upload_approved=true],
["unauthorized rehosting",d=>d.rows[5].item_copy_rehost_approved=true],
["image upscaling",d=>d.rows[2].conditional_review_dimensions_px=[960,741]],
["image exceeds width cap",d=>d.rows[0].max_width_px=1280],
["rights wrongly generalized",d=>d.rows[4].rights_claim="USCG_PUBLIC_DOMAIN"],
["noaa replacement invented",d=>d.rows[4].asset_url="https://noaa.gov/photo.jpg"],
["USGS unknown creator erased",d=>d.rows[5].rights_claim="USGS_AUTHOR_KNOWN"],
["responsive srcset invented",d=>d.rows[3].published_srcset_present=true],
["missing image slot",d=>d.rows.pop()],
["duplicate slot",d=>d.rows[1].key=d.rows[0].key],
["wrong width/height",d=>d.rows[0].published_dimensions_px=[960,984]],
["alt text mismatch",d=>d.rows[2].alt_view="wrong"],
["homepage scope widened",d=>d.scope.homepage_design_changes=1],
["wordPress production write",d=>d.scope.production_wordpress_writes=1],
["sensitive photo spelling issue hidden",d=>d.rows[1].spelling_review=""],
["false uploaded media",d=>d.scope.media_rehosts=1]
];
for(const [name,mutate] of cases)test(name+" fails closed",()=>{const d=clone();mutate(d);const r=assess(d);assert.equal(r.decision,"INVALID",name);assert.ok(r.errors.length>0);});
