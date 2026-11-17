'use strict';
const assert=require('node:assert/strict');
const audit=require('./tmi285_archive_rights_20261116_2327pt.json');
const {validate}=require('./validate_tmi285_archive_rights_20261116_2327pt.cjs');
function selfTest(a,fn){
let n=0,fail=[];const tryCase=(label,mut,want)=>{let d=JSON.parse(JSON.stringify(a));mut(d);let v=fn(d);if(v.ok!==want)fail.push(label+": "+v.errors.join(","));else n++;};
tryCase("baseline",()=>{},true);
const cases=[
["invent 404",d=>d.items[5].guest.status=404],
["invent 200",d=>d.items[0].guest.status=200],
["invent decode",d=>d.items[1].guest.decode=true],
["invent bytes",d=>d.items[2].guest.transfer_bytes=10],
["invent screenshot",d=>d.items[3].guest.screenshot="http://example.org/1.png"],
["fake broken",d=>d.items[4].guest.broken=true],
["claim 42 confirmed",d=>d.baseline.verified_broken=42],
["claim 76 observed",d=>d.baseline.measured_savings_percent=76],
["storage as wire",d=>d.baseline.visitor_bytes=64385752],
["wrong images",d=>d.baseline.images=354],
["missing slot",d=>d.items.pop()],
["duplicate slot",d=>d.items[2].slot="285:1"],
["remove ALT",d=>d.items[4].alt=""],
["corrupt source",d=>d.items[2].authored="javascript:x()"],
["HTML query mismatch",d=>d.items[3].view_url=d.items[3].view_html],
["fabricate responsive sizes",d=>d.items[0].view_markup.width=960],
["fake srcset",d=>d.items[1].view_markup.srcset=true],
["incorrect proxy",d=>d.items[3].jetpack=true],
["discard retriever caveat",d=>d.items[5].retriever_note="HTTP 404 browser"],
["rights assumed",d=>d.items[5].candidates[0].rights_cleared=true],
["frame assumed",d=>d.items[5].candidates[0].exact_frame_verified=true],
["binary assumed",d=>d.items[5].candidates[0].binary_sha256="x"],
["rehosting approved",d=>d.items[2].candidates[0].wordpress_rehosting_approved=true],
["upscale 2010",d=>d.items[5].candidates[0].review_px=[960,719]],
["stretch panel",d=>d.items[2].candidates[0].review_px=[604,400]],
["invent NRC pixels",d=>d.items[0].candidates[0].review_px=[960,600]],
["modify homepage",d=>d.safety.no_homepage_scope=false],
["permit WP writes",d=>d.safety.wordpress_writes=1],
["permit downloads",d=>d.safety.downloads=1],
["permit rehosting",d=>d.safety.rehosts=1],
["release gate bypass",d=>d.safety.decision="APPROVE"],
["collector duplication",d=>d.safety.site_qa_collector="new"]
];for(const [name,mut] of cases)tryCase(name,mut,false);if(fail.length)throw Error(fail.join("\n"));return n;
}
const n=selfTest(audit,validate);assert.equal(n,33);console.log(n+'/'+n+' fail-closed regression cases passed');
