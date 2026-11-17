'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const DUP='https://cloudfront-us-east-1.images.arcpublishing.com/deseretnews/PLWPL72QKJB7BBFJWTXJWVK6QQ.JPG';
function validate(a,original){
 const errs=[];const ok=(c,m)=>{if(!c)errs.push(m)};
 ok(a?.schema==='fv.media.teton291.20261104.v1','schema');
 ok(a?.post_id===291 && a?.live_wordpress?.status==='publish' && a?.live_wordpress?.exact_unchanged_src_and_alt===6 && a?.live_wordpress?.missing_html_width_height===6,'wp read-only snapshot');
 ok(a?.frozen_inventory?.posts===61 && a?.frozen_inventory?.image_refs===355 && a?.frozen_inventory?.external_origin===288 && a?.frozen_inventory?.oversize_originals===13,'site inventory');
 ok(Array.isArray(a?.rows) && a.rows.length===6,'six slots');
 const rows=Object.fromEntries((a?.rows||[]).map(x=>[x.key,x]));
 ok(Object.keys(rows).length===6,'unique slots');
 for(let i=0;i<6;i++){
  const k='291:'+i,x=rows[k],y=original?.images?.find(z=>z.key===k);
  ok(x && x.url===y?.source_url && x.alt===y?.alt && x.host===y?.source_host,'source drift '+k);
  if(!x)continue;
  ok(x.word_press_match===true,'live mismatch '+k);
  ok(x.origin_http_status===null&&x.guest_browser_http_status===null&&x.guest_browser_decoded===null&&x.guest_natural_width===null&&x.guest_transfer_bytes===null&&x.broken_in_browser===null,'fabricated HTTP/browser '+k);
  ok(x.rights_review==='HOLD'&&x.can_copy===false&&x.wp_write===false,'unauthorized copying '+k);
  ok(x.max_derivative_width<=960&&x.allow_upscale===false&&x.intrinsic_dimensions===null&&x.target_height_px===null,'invented dimensions '+k);
 }
 ok(rows['291:2']?.url===DUP&&rows['291:5']?.url===DUP,'duplicated Deseret URL');
 ok(a?.confirmed_visual_issue?.kind==='DUPLICATE_SOURCE_CONTRADICTS_EVENT_DESCRIPTION_NOT_MISSING_IMAGE'&&a?.confirmed_visual_issue?.incorrect_slot==='291:2'&&a?.confirmed_visual_issue?.same_image_after_slot==='291:5'&&a?.confirmed_visual_issue?.unique_urls===5,'visual truth');
 ok(Array.isArray(a?.candidate_mappings)&&a.candidate_mappings.some(c=>c.catalog==='https://catalog.archives.gov/id/28894685'&&c.for_slot==='291:2'),'NARA original candidate');
 for(const c of a?.candidate_mappings||[])ok(/^https:\/\//.test(c.catalog||'')&&c.rights?.startsWith('HOLD')&&c.width_limit<=960&&c.height===null&&c.rehost_approved===false,'candidate approval/rights');
 ok(a?.status?.claimed_42_broken_verified===false&&a?.status?.claimed_76_percent_wire_savings_measured===false&&a?.status?.actual_guest_broken_count===null,'unverified claim');
 ok(a?.status?.production_images_fixed===0&&a?.status?.third_party_downloads===0&&a?.status?.wordpress_writes===0&&a?.status?.homepage_edits===0&&a?.status?.subscription_spend===0,'production boundary');
 return errs;
}
function run(){
 let folder=__dirname,ap=path.join(folder,'teton_291_visual_mismatch_20261104.json'),fp=path.join(folder,'parts','02.json');
 const a=JSON.parse(fs.readFileSync(ap,'utf8')),buf=fs.readFileSync(fp),f=JSON.parse(buf);
 const sha=crypto.createHash('sha1').update('blob '+buf.length+'\0').update(buf).digest('hex');
 const errors=validate(a,f);
 if(sha!==a.frozen_inventory.git_blob_sha)errors.push('frozen blob SHA changed');
 if(errors.length){console.error(errors.join('\n'));process.exitCode=1;}else console.log('PASS Teton 291: six URLs and live WordPress visual custody, item-level rights and no invented browser savings');
}
module.exports={validate};if(require.main===module)run();
