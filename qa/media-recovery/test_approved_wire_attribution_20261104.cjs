'use strict';
const {assessApprovedWireAttribution}=require('./approved_wire_attribution_20261104.cjs');
function row(post_id,keys,bytes){
 const network_images=[],stored_images=[];
 keys.forEach((key,i)=>{const request_id='r'+i;
  network_images.push({request_id,encoded_data_length:bytes[i]});
  stored_images.push({image_key:key,request_id});});
 return {post_id,stored_images,network_images};
}
function sample(){
 return {before:{pages:[row(1,['1:0','1:1'],[1000,1000])]},
         after:{pages:[row(1,['1:0','1:1'],[200,1000])]}};
}
function runTests(){
 let n=0;const ok=(x,msg)=>{if(!x)throw Error(msg);n++};
 let s=sample(),r=assessApprovedWireAttribution(s.before,s.after,['1:0']);
 ok(r.pass&&r.approved_source_savings_bytes===800,'changed source alone carries 800 saved bytes');
 r=assessApprovedWireAttribution(s.before,s.after,[]);
 ok(!r.pass&&r.reasons.includes('no_approved_changed_image_sources'),'unapproved improvement rejected');
 s=sample();s.after.pages[0].network_images[1].encoded_data_length=250;
 r=assessApprovedWireAttribution(s.before,s.after,['1:0']);
 ok(!r.pass&&r.reasons.some(x=>x.startsWith('unattributed_unchanged_source_wire_delta')),'unchanged image drift rejected');
 s=sample();s.after.pages[0].network_images[0].encoded_data_length=1400;
 r=assessApprovedWireAttribution(s.before,s.after,['1:0']);
 ok(r.pass&&r.approved_source_savings_bytes===-400,'negative approved savings not spun');
 s=sample();s.after.pages[0].stored_images[0].request_id='r1';
 r=assessApprovedWireAttribution(s.before,s.after,['1:0']);
 ok(!r.pass&&r.reasons.some(x=>x.startsWith('changed_network_request_grouping')),'deduping topology drift needs review');
 s=sample();s.after.pages[0].network_images[0].encoded_data_length=NaN;
 r=assessApprovedWireAttribution(s.before,s.after,['1:0']);
 ok(!r.pass&&r.reasons.some(x=>x.startsWith('after:1:invalid_or_duplicate_request_group')),'NaN rejected');
 s=sample();s.before.pages[0].stored_images[1].request_id='r0';
 s.after.pages[0].stored_images[1].request_id='r0';
 r=assessApprovedWireAttribution(s.before,s.after,['1:0']);
 ok(!r.pass&&r.reasons.some(x=>x.startsWith('mixed_changed_and_unchanged_shared_request')),'shared unchanged+changed cannot be attributed');
 s=sample();s.after.pages.pop();
 r=assessApprovedWireAttribution(s.before,s.after,['1:0']);
 ok(!r.pass&&r.reasons.some(x=>x.startsWith('missing_candidate_post')),'missing post rejected');
 return {passed:n,fixture:'synthetic only',actual_browser_measurements:0};
}
if(require.main===module)console.log(JSON.stringify(runTests()));
module.exports={runTests};
