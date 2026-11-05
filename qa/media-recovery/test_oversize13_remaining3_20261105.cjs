"use strict";
const {test}=require("node:test");
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const {validate}=require("./validate_oversize13_remaining3_20261105.cjs");
const original=JSON.parse(fs.readFileSync(path.join(__dirname,"oversize13_remaining3_20261105.json"),"utf8"));
function modified(change){const a=structuredClone(original);change(a);return a}
test("pinned fresh 115-media source census is exact",()=>assert.deepEqual(validate(original),[]));
const mutations=[
 ["invented browser status",a=>a.entries[0].guest_http_status=200],
 ["invented origin HTTP",a=>a.entries[0].origin_http_status=200],
 ["invented wire bytes",a=>a.entries[0].actual_wire_bytes=1234],
 ["invented currentSrc",a=>a.entries[0].exact_current_visitor_src="https://finalvestige.com/a.jpg"],
 ["fabricated decoded image",a=>a.entries[0].browser_decoding_verified=true],
 ["assert 42 broken",a=>a.external_origin_broken_images_claim="CONFIRMED_42"],
 ["assert 76 percent",a=>a.transferred_weight_reduction_claim="MEASURED_76_PERCENT"],
 ["assert production repair",a=>a.production_fixes_made=1],
 ["fake rights clearance",a=>a.entries[0].rights_clearance="PUBLIC_DOMAIN"],
 ["fake media hash",a=>a.entries[0].asset_binary_sha256="abcd"],
 ["fake caching approval",a=>a.entries[0].caching_approved=true],
 ["fake media upload approval",a=>a.entries[0].wordpress_upload_approved=true],
 ["fake post edit approval",a=>a.entries[0].published_post_edit_approved=true],
 ["bad 960 dimension",a=>a.entries[0].conditional_max_960.width=1280],
 ["bad aspect ratio",a=>a.entries[0].conditional_max_960.height=1200],
 ["upscale",a=>a.entries[0].conditional_max_960.upscale=true],
 ["wrong original bytes",a=>a.entries[0].original_bytes=1234],
 ["wrong total",a=>a.oversized_stored_bytes=10],
 ["stale old scan size",a=>a.media_records_inspected=113],
 ["bad category bytes",a=>a.group_totals.remaining_uncategorized3.bytes=1],
 ["fake empty group",a=>a.group_totals.vasa_press3.count=0],
 ["drop a record",a=>a.entries.pop()],
 ["duplicate an image id",a=>a.entries[1].media_id=a.entries[0].media_id],
 ["wrong image host",a=>a.entries[0].origin_url="https://evil.test/pic.png"],
 ["pretend portrait not in schema",a=>a.entries.find(x=>x.media_id===293).usage_evidence.status="not_in_use"],
 ["pretend draft live",a=>a.entries.find(x=>x.media_id===405).usage_evidence.status="published"],
 ["pretend unknown PNG orphan",a=>a.entries.find(x=>x.media_id===482).usage_evidence.status="verified_orphan"],
 ["invent page usage",a=>a.read_only_page_checks.find(x=>x.id===234).filename_hits.founder_portrait=0],
 ["invent delivered thumbnail",a=>a.entries[0].registered_sizes[0].virtual="VERIFIED"]
];
for(const [name,change]of mutations)test("fail closed: "+name,()=>assert.ok(validate(modified(change)).length>0,name));
