"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const {validate}=require("./validate_campcentury290.cjs"),base=require("./campcentury290_six_source_custody_20261116.json");
const copy=()=>JSON.parse(JSON.stringify(base));
test("six-row archival evidence baseline",()=>assert.deepEqual(validate(copy()),[]));
const cases=[
["schema",x=>x.schema="bad","SCHEMA"],["revision",x=>x.post_modified="today","REVISION"],["post id",x=>x.post_id=999,"REVISION"],
["post url",x=>x.post_url="https://bad/","POST_URL"],["jetpack count",x=>x.counts.jetpack=6,"COUNTS"],["markup count",x=>x.counts.explicit_geometry=6,"COUNTS"],
["fake capture count",x=>x.counts.browser_verified=6,"EVIDENCE_COUNTS"],["offsite drift",x=>x.historic.qa154_offsite=288,"COHORT"],
["fake 42 broken",x=>x.historic.verified_broken=42,"UNPROVEN_CLAIMS"],["fake 76 percent",x=>x.historic.measured_saving_pct=76,"UNPROVEN_CLAIMS"],
["wire from library",x=>x.historic.visitor_bytes=64385752,"STORED_NOT_WIRE"],["WP write",x=>x.no_changes.wordpress=1,"NO_WRITE_wordpress"],
["download",x=>x.no_changes.downloads=1,"NO_WRITE_downloads"],["billable call",x=>x.no_changes.paid=1,"NO_WRITE_paid"],
["missing row",x=>x.rows.pop(),"SIX_ROWS"],["wrong slot",x=>x.rows[0].slot="290:2","SLOT"],
["bad url",x=>x.rows[0].authored_url="javascript:bad","VALID_URL_authored_url"],["ALT regression",x=>x.rows[0].alt_view="Wrong","ALT"],
["fake geometry",x=>x.rows[1].view_width=960,"MARKUP"],["proxy mistaken",x=>x.rows[2].delivery="JETPACK_THIRD_PARTY","DELIVERY"],
["wrong proxy",x=>x.rows[0].view_src="https://i0.wp.com/bad/image.jpg","VIEW_URL"],
["retriever 403 declared HTTP",x=>x.rows[5].reader_result="HTTP_403","RETRIEVER_NOT_HTTP"],
["fake HTTP 404",x=>x.rows[5].visitor_http=404,"NO_FAKE_BROWSER"],["fake wire bytes",x=>x.rows[0].visitor_wire_bytes=999,"NO_FAKE_BROWSER"],
["license forgery",x=>x.rows[3].rights_claim="PD_US_GOVERNMENT_CATALOG","LICENSE"],["unsafe swap",x=>x.rows[3].visual_relation="SAME_FRAME_UNHASHED","FRAME_CUSTODY"],
["approval spoof",x=>x.rows[4].copy_approved=true,"HOLD_RELEASE"],["upload spoof",x=>x.rows[4].wp_upload_approved=true,"HOLD_RELEASE"],
["fabricated hash",x=>x.rows[0].downloaded_sha256="fake","HOLD_RELEASE"],["invent native size",x=>x.rows[0].conditional_960px=[960,540],"NO_INVENTED_PIXELS"],
["distorted resize",x=>x.rows[4].conditional_960px=[960,500],"NO_DISTORT_OR_UPSCALE"],
["fake file route",x=>x.rows[1].candidate_image_file_url="https://commons.wikimedia.org/wiki/File:trench.jpg","REAL_IMAGE_ROUTE"],
["wrong accession",x=>x.rows[4].source_catalog_url="https://usace.contentdm.oclc.org/digital/collection/x/id/999","USACE_654"],
["premature ResearchGate rehost",x=>x.rows[5].candidate_image_file_url="https://upload.wikimedia.org/wikipedia/commons/x/x/test.jpg","PAPER_RIGHTS_HOLD"]
];
for(const [name,mutate,want] of cases)test(name,()=>{let m=copy();mutate(m);assert.ok(validate(m).includes(want),name+" expected "+want);});
