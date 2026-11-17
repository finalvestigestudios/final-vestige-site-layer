'use strict';
const EXPECT={'370:0':'80-G-276907','370:1':'80-G-202485','370:3':'80-G-276940','370:4':'SC 427947'};
function validate(a,p){
 if(a?.schema!=='fv-westloch-370-v1'||a.source?.post_id!==370||a.source.blob_sha!=='48e1ebf07207e948ba5802e714eb39659d2e1c1d'||a.source.no_fresh_wordpress_read!==true)throw Error('source');
 const live=p?.images?.filter(x=>x.post_id===370).sort((x,y)=>x.slot-y.slot);
 if(live?.length!==8||a.images?.length!==8)throw Error('count');
 const m=a.metrics,q=a.policy;
 if(m?.stored_slots!==8||m?.external_direct_navy!==4||m?.already_first_party!==4||m?.guest_broken_confirmed!==0||m?.visitor_bytes_measured!==0)throw Error('metrics');
 if(q?.max_width_px!==960||q?.no_upscale!==true||q?.rights_approved!==false||q?.caching_allowed!==false||q?.production_writes!==false)throw Error('policy');
 for(let i=0;i<8;i++){
 const r=a.images[i],s=live[i],ref=EXPECT[s.key];
 if(r.key!==s.key||r.original_alt!==s.alt||r.source_url!==s.source_url||r.source_kind!==s.source_kind)throw Error('identity');
 if((!!ref)!==(r.source_kind==='external'))throw Error('origin');
 for(const k of ['origin_http','guest_http','decoded','current_src','wire_bytes'])if(r.transport?.[k]!==null)throw Error('invented_response');
 if(r.transport?.method!==(ref?'web.open exact URL':'not_tested'))throw Error('method');
 if(ref){
 if(r.archive?.id!==ref||!r.archive.catalog_url.startsWith('https://www.history.navy.mil/'))throw Error('archive_id');
 if(r.transport?.outcome!==(i===0||i===3?'web_timeout_400_wrapper':'web_inaccessible_no_http'))throw Error('transport');
 if(i===1&&!r.archive.notes?.includes('5860x4890'))throw Error('tiff_conflict');
 if(i===4&&!r.archive.custody?.includes('Army Signal Corps'))throw Error('signal_corps');
 }else if(r.transport?.outcome!=='not_tested')throw Error('untested');
 if(r.rights?.permission_verified!==false||r.rights?.credits_verified!==false||r.rights?.copy_allowed!==false)throw Error('rights');
 const d=r.derivative;
 if(d?.source_width!==null||d?.source_height!==null||d?.max_width!==960||d?.output_width!==null||d?.output_height!==null||d?.no_upscale!==true)throw Error('geometry');
 if(r.release?.download!=='HOLD'||r.release?.rehost!=='HOLD'||r.release?.swap!=='HOLD'||r.release?.rollback_source_url!==s.source_url)throw Error('publish_hold');
 }
 return {state:'SOURCE_ONLY_HOLD',slots:8,external:4,guest_failures:0};
}
module.exports={validate};
