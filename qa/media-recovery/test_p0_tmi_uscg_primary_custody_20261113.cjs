'use strict';
const assert = require('node:assert/strict');
const { test } = require('node:test');
const { validate } = require('./validate_p0_tmi_uscg_primary_custody_20261113.cjs');
const original = require('./p0_tmi_uscg_primary_custody_20261113.json');
const changes = [["baseline", x=>{}],
["alter source slot", x=>x.records[0].slot="999:0"],
["invent new published source", x=>x.records[0].published_src="https://example.com/fake.jpg"],
["fake origin HTTP 404", x=>x.records[0].retriever.origin_status=404],
["fake guest HTTP 404", x=>x.records[1].retriever.guest_status=404],
["false visitor broken", x=>x.records[0].release.browser_failure_confirmed=true],
["false binary parity", x=>x.records[0].release.binary_match_confirmed=true],
["false crop parity", x=>x.records[0].release.crop_parity_confirmed=true],
["unauthorized rehost", x=>x.records[1].release.rehost_cleared_for_this_change=true],
["unauthorized download", x=>x.records[0].release.downloaded=true],
["unauthorized WordPress write", x=>x.records[1].release.wp_post_written=true],
["upscale to 960", x=>x.records[0].derivative_plan.uncropped_possible_px=[960,720]],
["fabricated scene change", x=>x.records[0].primary_credited_source.subject="1979_movie_still"],
["invented PD government status", x=>x.records[0].primary_credited_source.catalog_license="US_GOVT"],
["alter publisher credit", x=>x.records[0].primary_credited_source.publisher_credit_direct_file="https://example.com/other.jpg"],
["alter rights", x=>x.records[1].primary_credited_source.catalog_rights="NO_RESTRICTIONS"],
["invent dimensions", x=>x.records[1].primary_credited_source.catalog_dimensions_px=[960,540]],
["erase field date difference", x=>x.records[0].primary_credited_source.catalog_date_field="2010-06-06"],
["invent wire savings", x=>x.controls.measured_wire_savings_percent=76],
["invent 42 confirmed", x=>x.controls.guest_broken_total=42],
["wrong QA ownership", x=>x.controls.siteqa_owner_pr=1655],
["risk publishing", x=>x.controls.stage="APPROVED"],
["mislabel catalog weight as bytes", x=>x.records[0].primary_credited_source.catalog_size_display=235000]];
for(const [i,[label,change]] of changes.entries()) test(label,()=>{const x=JSON.parse(JSON.stringify(original));change(x);const result=validate(x); assert.equal(result.ok,i===0,JSON.stringify(result.errors));});
