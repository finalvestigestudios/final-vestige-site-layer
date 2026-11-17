'use strict';
function runTests(validate,base,source){
 const faults=[];
 const check=(name,mutate,shouldPass=false)=>{
  const a=JSON.parse(JSON.stringify(base));
  if(mutate)mutate(a);
  const problems=validate(a,source);
  if((problems.length===0)!==shouldPass)faults.push({name,problems});
 };
 check('original six-slot audit accepted',null,true);
 check('fabricated guest HTTP rejected',a=>a.image_entries[0].visitor_browser.http_status=200);
 check('fabricated visitor image decode rejected',a=>a.image_entries[1].visitor_browser.natural_width_px=900);
 check('source URL substitution rejected',a=>a.image_entries[0].published_src+='?tamper=1');
 check('ALT/caption identity mutation rejected',a=>a.image_entries[0].published_alt='Unverified caption');
 check('duplicate source key rejected',a=>a.image_entries[1].key='289:0');
 check('retriever 403 not converted to browser HTTP',a=>a.image_entries[4].visitor_browser.http_status=403);
 check('retriever result cannot be relabeled 200',a=>a.image_entries[4].retriever.retriever_wrapper_status=200);
 check('2021 chronology protected',a=>a.image_entries[4].chronology='This image was taken in 1967');
 check('2013 chronology protected',a=>a.image_entries[5].chronology='Original disaster scene');
 check('exact DVIDS VIRIN protected',a=>a.replacement_candidates[0].virin='210811-N-SG189-1111');
 check('asset resolution no upscaling protected',a=>a.replacement_candidates[0].conditional_width_px=6000);
 check('derived aspect ratio protected',a=>a.replacement_candidates[0].conditional_height_px=600);
 check('rights clearance cannot be presumed',a=>a.replacement_candidates[0].rights.wordpress_rehosting_cleared=true);
 check('NHHC image cannot silently be called same-scene',a=>a.replacement_candidates[1].scene_class='same_image');
 check('76 percent savings cannot be claimed',a=>a.baseline.claimed_76_percent_wire_reduction_measured=true);
 check('42 failures cannot be claimed',a=>a.baseline.reported_42_broken_verified=true);
 check('no WordPress production writes',a=>a.controls.wordpress_production_write=true);
 check('no media cache upload approval',a=>a.image_entries[4].wordpress_media_upload_authorized=true);
 check('no production repair count inflation',a=>a.baseline.production_repaired_images=1);
 if(faults.length)throw Error('FAIL '+JSON.stringify(faults));
 return {passed:20,failed:0};
}
module.exports={runTests};
if(typeof require==='function'&&require.main===module){
 const fs=require('node:fs'),path=require('node:path');
 const dir=__dirname;
 const a=JSON.parse(fs.readFileSync(path.join(dir,'forrestal_289_virin_recovery_20261102.json'),'utf8'));
 const source=JSON.parse(fs.readFileSync(path.join(dir,'parts','03.json'),'utf8')).images.filter(x=>x.post_id===289).sort((x,y)=>x.slot-y.slot);
 const result=runTests(require('./validate_forrestal_289_20261102.cjs').validate,a,source);
 process.stdout.write(JSON.stringify(result)+'\n');
}
