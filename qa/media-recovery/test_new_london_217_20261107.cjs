"use strict";
const assert=require("node:assert/strict");
const {validate}=require("./validate_new_london_217_20261107.cjs");
const baseline=require("./new_london_217_six_lineage_20261107.json");
const clone=()=>JSON.parse(JSON.stringify(baseline));
let count=0;
function test(label,fn){fn();count++;console.log("PASS",label);}
test("unchanged source ledger passes",()=>assert.equal(validate(baseline).ok,true));
const cases=[
["fabricated 404",a=>a.images[0].browser.http_status=404],
["fabricated 200",a=>a.images[4].retriever.actual_origin_http_status=200],
["invented transfer",a=>a.performance.cold_browser_image_bytes=10000],
["42 confirmed",a=>a.performance.reported_42_broken_proven=true],
["76% measured",a=>a.performance.claimed_76_percent_wire_saved_measured=true],
["incorrect original URL",a=>a.images[3].stored_source_url="https://example.com/other.jpg"],
["wrong slot key",a=>a.images[1].key="217:0"],
["upscaled AP photograph",a=>a.images[0].safe_preview.width=960],
["wrong crop geometry",a=>a.images[4].safe_preview.height=1020],
["crop permitted",a=>a.images[2].safe_preview.crop=true],
["copyright cleared without evidence",a=>a.images[2].provenance.rights_republication_cleared=true],
["missing attribution",a=>a.images[5].provenance.credit=""],
["premature WP staging",a=>a.images[0].wp_recovery.wp_media_id=4],
["premature replacement",a=>a.images[0].wp_recovery.replacement_authorized=true],
["invented checksum",a=>a.images[4].wp_recovery.master_sha256="abc"],
["erase shared newspaper lineage",a=>a.images[3].provenance.lineage="other"],
["erase anomalous AP date",a=>a.images[0].provenance.date_record="1937-03-18"],
["misdate modern monument",a=>a.images[5].provenance.date_record="1937-03-18"],
["strip license",a=>a.images[5].provenance.rights="free"],
["substitute unrelated archive",a=>a.related_authoritative_source.rights_rehosting_cleared=true],
["WP edit flag",a=>a.prohibitions.no_wordpress_writes=false],
["wrong baseline cohort",a=>a.post.inventory_blob_sha="wrong"],
["wrong oversize storage",a=>a.performance.oversized_wp_originals_stored_bytes_historical=1],
["missing slot",a=>a.images.pop()]
];
for (const [name,mutation] of cases)test("reject "+name,()=>{const copy=clone();mutation(copy);assert.equal(validate(copy).ok,false);});
console.log(count+"/"+(cases.length+1)+" cases passed");
