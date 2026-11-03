'use strict';
const urls=["https://arc-anglerfish-washpost-prod-washpost.s3.amazonaws.com/public/IIYZWAFLJUQD3YGEYEKMG5PVXY.jpg","https://cloudfront-us-east-1.images.arcpublishing.com/tbt/555OWMWIJMI6TGNIIBWI6S7HAY.jpg","https://skywaydisaster.com/images/timeline2.jpg","https://img.connatix.com/ecf95169-f8cd-4cd5-8698-9bc54211f8e9/1_th.jpg","https://www.flmd.uscourts.gov/sites/flmd/files/images/figure-9-sunshine-skyway-bridge-3.jpg","https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg"];
const alts=["An automobile stopped near the broken end of the Sunshine Skyway Bridge after the May 9, 1980 collapse.","The bulk carrier Summit Venture beneath the broken Sunshine Skyway Bridge after the collision.","Diagram showing the Summit Venture collision sequence at the Sunshine Skyway Bridge.","Automobile halted at the broken end of the Sunshine Skyway after the 1980 collapse.","Federal archival view of the collapsed Sunshine Skyway Bridge and Summit Venture after the May 1980 accident.","The old Sunshine Skyway wreckage and the later bridge replacement in Tampa Bay."];
function validate(a) {
 const err=[],bad=s=>err.push(s);
 if(a?.schema!=='fv-skyway-287-six-source-p0-v1')return ['schema'];
 if(a.wordpress?.post_id!==287||a.wordpress?.status!=='publish'||a.wordpress?.modified!=='2026-11-02T21:40:01'||a.wordpress?.source_confirmed!==true||a.archive?.source_blob!=='49183f66f880f7c4dfd363acca906876877f2e5e')bad('source evidence');
 if(!Array.isArray(a.images)||a.images.length!==6)return [...err,'missing images'];
 a.images.forEach((x,i)=>{
   if(x.key!=='287:'+i||x.original_url!==urls[i]||x.original_alt!==alts[i]||x.target_max_width_px!==960||x.cached!==false||x.wp_write!==false)bad('source/unsafe '+i);
   const y=x.observation||{};
   if(y.method!=='independent_web_image_retriever'||y.result!==(i===5?'retriever_wrapper_404':'displayed')||y.wrapper_code!==(i===5?404:null))bad('wrapper '+i);
   for(const f of ['origin_http_status','guest_http_status','guest_decoded','guest_current_src','guest_natural_width','guest_transfer_bytes'])if(y[f]!==null)bad('fake browser/origin '+i+':'+f);
 });
 const c=a.candidate||{};
 if(a.priority_image!=='287:5'||c.type!=='semantically_related_not_binary_identical'||c.catalog_id!=='K894127'||c.photographer!=='H. Milo Stewart'||c.date!=='circa 1987'||c.commons_record!=='https://commons.wikimedia.org/wiki/File:View_of_the_old_and_new_Sunshine_Skyway_bridges_from_St._Petersburg,_Florida,_1987.jpg')bad('provenance');
 if(c.commons_width_px!==600||c.commons_height_px!==595||c.conditional_derivative_px?.join('x')!=='600x595'||c.alternate_native_dimensions_px!==null)bad('dimensions / upscaling');
 if(c.rights_mark!=='Florida Memory PDM 1.0 (mark, not grant)'||c.commons_uploader_cc0_not_rightsholder_proof!==true||c.rights_cleared!==false||c.exact_original_match!==false||c.original_crop_verified!==false||c.replacement_authorized!==false||c.editorial_recaption_required!==true||c.proposed_credit!=='State Archives of Florida/Stewart')bad('rights / identity');
 const s=a.acceptance||{};
 if(s.status!=='HOLD'||s.guest_browser_test!=='NOT_PERFORMED'||s.archival_binary_download!=='NOT_AUTHORIZED'||s.wp_media_upload!=='NOT_AUTHORIZED'||s.post_block_rewrite!=='NOT_AUTHORIZED'||s.credit_and_rights!=='REQUIRES_ITEM_REVIEW')bad('release hold');
 const n=a.counts||{},b=a.site_baseline||{};
 if(n.source_slots!==6||n.independently_displayed!==5||n.retriever_404_wrapper!==1||n.guest_confirmed_broken!==0||n.production_repaired!==0||n.visitor_weight_savings_percent!==null)bad('inferred network');
 if(b.posts!==61||b.slots!==355||b.external_origins!==288||b.originals_over_1_5MiB!==13||b.reported_42!=='UNVERIFIED_AS_BROWSER_FAILURES'||b.claimed_76!=='NOT_MEASURED')bad('false baseline');
 return err;
}
module.exports={validate};
