"use strict";
const test=require("node:test"),assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const {validate}=require("./validate_publisher_recovery_20261105_night.cjs");
const base=JSON.parse(fs.readFileSync(path.join(__dirname,"publisher_recovery_20261105_night.json"),"utf8"));
const fresh=()=>JSON.parse(JSON.stringify(base));
test("baseline passes",()=>assert.deepEqual(validate(fresh()),[]));
const mutations=[
["faked Chrome error",d=>d.rows[0].chrome_status=404],
["faked source status",d=>d.rows[1].web_reader_old_status=200],
["wrong candidate host",d=>d.rows[1].candidate="https://example.com/photo.jpg"],
["wrong source host",d=>d.rows[0].old="https://different.example/x"],
["faked rights",d=>d.rows[1].rights="public domain"],
["lost 2010",d=>d.rows[0].editorial_gate="nuclear station aerial"],
["lost 1987",d=>d.rows[1].editorial_gate="1980 wreckage"],
["upscale",d=>d.rows[0].derivative=[960,720]],
["unknown pixels invented",d=>d.rows[1].native=[1000,667]],
["unlicensed rehost",d=>d.rows[1].rehost_approved=true],
["unapproved hotlink",d=>d.rows[1].hotlink_approved=true],
["WP edit",d=>d.rows[0].wp_edit=true],
["WP write",d=>d.release.wp_writes=1],
["invent repairs",d=>d.release.production_repairs=2],
["invent savings",d=>d.baseline.measured_wire_savings_percent=76],
["fake 42 browser broken",d=>d.baseline.broken_browser_verified=42],
["remove browser gate",d=>d.release.browser_proof_required=false],
["drop source",d=>d.rows.pop()]
];
for(const [name,mutation] of mutations)test("reject "+name,()=>{const d=fresh();mutation(d);assert.notDeepEqual(validate(d),[],name);});
