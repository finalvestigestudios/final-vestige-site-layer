'use strict';
const EXPECTED=["https://media.defense.gov/2007/Jan/25/2000519451/-1/-1/0/070125-F-0000Z-099.JPG","https://media.defense.gov/2006/May/30/2000572755/2000/2000/0/050606-F-1234P-012.JPG","https://upload.wikimedia.org/wikipedia/commons/4/49/0000050606-F-1234P-014.jpg","https://qmmuseum.army.mil/assets/img/aotm/2012/09_M1910_canteen_1.jpg","https://www.ladybegood.net/diaries/full/Toner_Diary2%20.jpg","https://unwritten-record.blogs.archives.gov/wp-content/uploads/sites/6/2017/06/111-c-17240-scaled.jpg","https://media.defense.gov/2006/Jun/02/2000554420/-1/-1/0/060530-F-1234S-041.JPG"];
const OUTCOMES=['wrapper_403','wrapper_403','retriever_rendered','wrapper_502','retriever_rendered','retriever_rendered','wrapper_403'];
function validate(a){
const e=[];const fail=s=>e.push(s);
if(!a||a.schema!=='fv.media-recovery.278.v1')return ['schema'];
if(a.post?.id!==278||a.post?.url!=='https://finalvestige.com/2026/08/19/they-walked-beyond-the-search-lady-be-good/')fail('post');
if(a.frozen?.posts!==61||a.frozen?.img_refs!==355||a.frozen?.blob_sha!=='6df3251e5a67a971d87a516a1ba4a0cc32f51f96')fail('census');
if(a.sitewide_status?.alleged_broken_42!=='unverified'||a.sitewide_status?.claimed_transfer_reduction_76_percent!=='unmeasured'||a.sitewide_status?.thirteen_large_original_stored_bytes!==43522829)fail('performance claims');
if(a.production_writes!==false||a.downloaded_media!==false||a.site_qa_browser_collector_duplicated!==false)fail('unsafe action');
if(!Array.isArray(a.images)||a.images.length!==7)return [...e,'row count'];
a.images.forEach((r,i)=>{
if(r.key!=='278:'+i||r.source_url!==EXPECTED[i]||r.source_host!==EXPECTED[i].split('/')[2]||!r.alt)fail('identity '+i);
if(r.stored_width!==null||r.stored_height!==null)fail('HTML geometry '+i);
const o=r.independent_retriever||{};
if(o.outcome!==OUTCOMES[i]||o.method!=='web.open wrapper'||o.origin_http_status!==null||o.guest_browser_http_status!==null||o.natural_width!==null||o.transferred_bytes!==null)fail('invented browser '+i);
const c=r.candidate||{};
if(!/^https:\/\//.test(c.catalog_url||'')||!c.relationship||!c.rights||c.exact_image_match!==(i===1||i===2)||c.copy_approved!==false)fail('rights '+i);
if(r.release!=='HOLD'||r.wp_attachment_id!==null||!r.fidelity_warning)fail('unsafe release '+i);
if(i===2){if(r.catalog_original_dimensions?.width!==1800||r.catalog_original_dimensions?.height!==1192||r.conditional_preview?.width!==960||r.conditional_preview?.height!==636)fail('Commons preview');}
else if(r.catalog_original_dimensions!==null||r.conditional_preview?.width!==null||r.conditional_preview?.height!==null)fail('unverified pixels '+i);
if(i===3&&!r.fidelity_warning.includes('DO NOT assert'))fail('canteen artifact identity');
if(i===5&&!r.fidelity_warning.includes('no visible investigators'))fail('NARA ALT conflict');
});
return e;
}
module.exports={validate};
if(require.main===module){const fs=require('node:fs'),path=require('node:path');const f=process.argv[2]||path.join(__dirname,'lady_be_good_278_source_audit_20261107.json');const errs=validate(JSON.parse(fs.readFileSync(f,'utf8')));if(errs.length){console.error(errs.join('\n'));process.exitCode=1;}else console.log('PASS 7 exact-source safety gates');}
