"use strict";
const fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict");
const {validate}=require("./validate_thresher_220_20261103.cjs");
const audit=JSON.parse(fs.readFileSync(path.join(__dirname,"thresher_220_navy_custody_20261103.json"),"utf8"));
const frozen=JSON.parse(fs.readFileSync(path.join(__dirname,"parts/05.json"),"utf8"));
let passed=0;
const check=(label,fn)=>{fn();passed++;console.log("PASS",label)};
check("baseline",()=>assert.deepEqual(validate(audit,frozen),[]));
const bads=[
["invented browser 404",a=>a.images[0].retrieval.guest_browser_http_status=404],
["invented origin 403",a=>a.images[1].retrieval.origin_http_status=403],
["invented image transfer",a=>a.images[2].retrieval.guest_image_wire_bytes=42],
["claimed decode",a=>a.images[3].retrieval.guest_browser_decoded=true],
["claim 42 confirmed",a=>a.conclusion.sitewide_42_verified=true],
["claim 76 percent",a=>a.conclusion.sitewide_76_percent_measured=true],
["false production fix",a=>a.conclusion.production_repairs=1],
["altered url",a=>a.images[0].exact_source_url="https://example.com/photo.jpg"],
["wrong alt",a=>a.images[6].original_alt="foo"],
["duplicate slot",a=>a.images[3].key=a.images[2].key],
["upscaled 740 original",a=>a.images[1].proposed.width_px=960],
["wrong height",a=>a.images[0].proposed.height_px=1000],
["rehost approved without rights",a=>a.images[5].proposed.wordpress_cache_and_rehost="APPROVED"],
["swap approved",a=>a.images[5].proposed.swap_published_src="APPROVED"],
["licensed despite missing proof",a=>a.images[2].rights.copy_allowed=true],
["license signed",a=>a.images[4].rights.item_specific_signoff=true],
["credits reviewed",a=>a.images[0].rights.credits_reviewed=true],
["related image promoted exact",a=>a.images[4].catalog.association="same_catalog_image_by_Commons_source_record"],
["invented primary ID for related 1964",a=>a.images[4].catalog.navy_catalog_id="USN 1084706"],
["removed ID on exact",a=>a.images[0].catalog.navy_catalog_id=null],
["missing row",a=>a.images.pop()],
["source not frozen",a=>a.source.not_live_wp_read=false],
["changed post",a=>a.source.post_id=999],
["catalog http presumed",a=>a.images[0].catalog.observation="HTTP 200"],
["tampered frozen blob sha",a=>a.source.blob_sha="ffffffff"],
["fabricated catalog original",a=>a.images[0].catalog.original_width_px=5000],
["swapped Navy primary ID",a=>a.images[6].catalog.navy_catalog_id="NH 97545"]
];
for (const [name,mutate] of bads){check(name,()=>{const a=structuredClone(audit);mutate(a);assert.ok(validate(a,frozen).length>0,name)})}
console.log(passed+"/"+(bads.length+1)+" assertions passed");
