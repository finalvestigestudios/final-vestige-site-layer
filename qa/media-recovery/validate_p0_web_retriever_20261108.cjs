'use strict';
/** Source-wrapper status audit validator. Never treats a retrieval wrapper as guest HTTP. */
const EXPECT=[
 ['287:5','published_original','https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg','WEB_OPEN_FETCH_404',404],
 ['287:5','publisher_relocation_candidate','https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg','WEB_OPEN_IMAGE_RENDERED',null],
 ['418:2','published_original','https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg','WEB_OPEN_FETCH_403',403]
];
function validate(x){
 const err=[];
 if(!x||x.schema!=='fv-source-wrapper-p0-20261108-v1'||x.observed_date_utc!=='2026-11-08'||!Array.isArray(x.rows)||x.rows.length!==3)err.push('invalid_cohort');
 if(x?.guest_browser_verified!==false||x?.guest_origin_http_statuses_known!==0||
    x?.rights_clearances_granted!==0||x?.production_writes!==0||
    x?.policy?.claims_about_42_broken!=='UNVERIFIED'||x?.policy?.claimed_76_percent_reduction!=='UNMEASURED'||
    x?.policy?.media_rehosting_allowed!==false||x?.policy?.subscription_spend_usd!==0)
  err.push('unsupported_recovery_or_wire_claim');
 for(let i=0;i<EXPECT.length;i++){
  const [key,role,url,observation,status]=EXPECT[i],r=x?.rows?.[i];
  if(!r||r.image_key!==key||r.role!==role||r.url!==url||
     r.observation!==observation||r.web_tool_status!==status)err.push('source_or_method_drift:'+i);
  if(!r||r.real_origin_http_status!==null||r.guest_browser_http_status!==null||
     r.browser_decode!==null||r.transferred_bytes!==null||r.exact_image_hash!==null||
     r.rights_release!=='HOLD'||r.cache_authorized!==false||
     r.wordpress_write_authorized!==false)err.push('fabricated_browser_or_rights_evidence:'+i);
 }
 const alt=x?.rows?.[1];
 if(!alt||alt.source_article_credit!=='University Press of Florida'||alt.same_photograph_binary_proven!==false||
    alt.original_dimensions_px!==null||alt.derivative_height_px!==null||
    alt.conditional_max_width_px!==960||alt.no_upscale!==true)err.push('unsafe_replacement_candidate');
 return {valid:err.length===0,errors:[...new Set(err)],checked_rows:EXPECT.length};
}
if(require.main===module){
 const fs=require('node:fs'),path=require('node:path');
 const input=JSON.parse(fs.readFileSync(path.join(__dirname,'p0_live_web_retriever_287_418_20261108.json'),'utf8'));
 const report=validate(input);console.log(JSON.stringify(report,null,2));if(!report.valid)process.exitCode=2;
}
module.exports={validate};
