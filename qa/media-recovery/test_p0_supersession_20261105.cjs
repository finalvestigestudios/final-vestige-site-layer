"use strict";
const {test}=require("node:test");
const assert=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path");
const {check}=require("./validate_p0_supersession_20261105.cjs");
const original=JSON.parse(fs.readFileSync(path.join(__dirname,"p0_authoritative_supersession_20261105.json"),"utf8"));
const mutation=[
["guest 404",v=>v.rows[0].guest_http=404],["fake browser fail",v=>v.rows[1].visitor_broken=true],
["invented transfer",v=>v.rows[2].guest_wire_bytes=220],["stale NARA portrait",v=>v.rows[1].candidate=v.rows[1].reject],
["960 upscale of 604",v=>v.rows[1].max_safe_width_if_preview_known=960],["rights invented",v=>v.rows[0].rights_rehost=true],
["wp post write",v=>v.rows[2].wp_post_edit=true],["cache enabled",v=>v.rows[4].cache_allowed=true],
["unknown dimensions invented",v=>v.rows[3].max_safe_width_if_preview_known=960],["wrong 1964 year",v=>v.rows[4].detail="NOAA 1964 correct"],
["unrelated publicity photo passed",v=>v.rows[0].relationship="EXACT_MATCH"],["old Skyway 1980 assumed replacement",v=>v.rows[2].relationship="EXACT_MATCH"],
["VIRIN altered",v=>v.rows[3].src="https://media.defense.gov/other.JPG"],["USGS wrapper 404",v=>v.rows[5].wrapper=404],
["false savings",v=>v.baseline.weight_savings_measured=true],["publication",v=>v.release.production_changes=1],
["duplicate slot",v=>v.rows[5].k=v.rows[0].k],["extra slot",v=>v.rows.push({...v.rows[0]})],
["unknown license grant",v=>v.rows[0].wp_upload=true],["bad crop geometry",v=>v.rows[4].preview=[600,500]],
["non-https catalog",v=>v.rows[1].catalog="http://insecure.test"],["missing credit",v=>v.rows[0].credit=null]
];
test("canonical six-slot ledger validates",()=>assert.equal(check(original).ok,true));
for(const [name,f] of mutation)test("reject "+name,()=>{const v=JSON.parse(JSON.stringify(original));f(v);assert.equal(check(v).ok,false)});
