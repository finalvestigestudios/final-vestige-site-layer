"use strict";
function validate(m){
 const errors=[],check=(x,c)=>{if(!x)errors.push(c)};
 check(m?.schema==="fv-media-campcentury290-v1","SCHEMA");
 if(!m||typeof m!=="object")return errors;
 check(m.post_id===290&&m.post_modified==="2026-11-02T21:40:03","REVISION");
 check(m.post_url==="https://finalvestige.com/2026/08/19/the-city-kept-moving-camp-century/","POST_URL");
 const c=m.counts||{};
 check(c.images===6&&c.jetpack===5&&c.direct===1&&c.explicit_geometry===0&&c.responsive_pairs===0,"COUNTS");
 check(c.rendered_retriever===5&&c.disabled_retriever===1&&c.browser_verified===0,"EVIDENCE_COUNTS");
 const h=m.historic||{};
 check(h.posts===61&&h.inline_images===355&&h.qa154_offsite===286&&h.media183_offsite===288,"COHORT");
 check(h.reported_broken===42&&h.verified_broken===null&&h.claimed_saving_pct===76&&h.measured_saving_pct===null,"UNPROVEN_CLAIMS");
 check(h.originals_over_1_5mb===20&&h.stored_bytes===64385752&&h.visitor_bytes===null,"STORED_NOT_WIRE");
 for(const k of ["wordpress","downloads","rehosts","post_blocks","homepage","paid","merge","deployment"])check(m.no_changes?.[k]===0,"NO_WRITE_"+k);
 check(Array.isArray(m.rows)&&m.rows.length===6,"SIX_ROWS");
 if(!Array.isArray(m.rows))return errors;
 const expectedRights=["NASA_USE_POLICY_ITEM_REVIEW","PD_US_GOVERNMENT_CATALOG","PD_US_GOVERNMENT_CATALOG","CC_BY_SA_4_0","PD_US_GOVERNMENT_CATALOG","RIGHTS_UNKNOWN"];
 const expectedRelations=["SAME_NASA_COMPOSITE_UNHASHED","SAME_FRAME_CAPTION_CROP_DIFFER","CURRENT_SOURCE_ALREADY_OFFICIAL","RELATED_PLAN_DIFFERENT_VERSION","SAME_FRAME_UNHASHED","ORIGINAL_RESEARCH_FIGURE_RIGHTS_HOLD"];
 for(let i=0;i<m.rows.length;i++){
 const r=m.rows[i];if(!r||typeof r!=="object"){errors.push("ROW_OBJECT");continue;}
 check(r.slot==="290:"+i,"SLOT");
 for(const k of ["authored_url","view_src","source_catalog_url"])check(typeof r[k]==="string"&&r[k].startsWith("https://"),"VALID_URL_"+k);
 check(typeof r.alt_edit==="string"&&r.alt_edit.length>12&&r.alt_edit===r.alt_view,"ALT");
 check(r.view_width===null&&r.view_height===null&&r.view_srcset===false&&r.view_sizes===false,"MARKUP");
 check(r.delivery===(i===2?"DIRECT_WIKIMEDIA":"JETPACK_THIRD_PARTY"),"DELIVERY");
 const host=(r.authored_url||"").replace(/^https?:\/\//,"").split("/")[0];
 check(i===2?r.view_src===r.authored_url:r.view_src.startsWith("https://i0.wp.com/")&&r.view_src.includes(host),"VIEW_URL");
 check(r.reader_result===(i===5?"RETRIEVER_DISABLED":"IMAGE_RENDERED"),"RETRIEVER_NOT_HTTP");
 check(r.visitor_http===null&&r.visitor_current_src===null&&r.visitor_mime===null&&r.visitor_decode===null&&r.visitor_wire_bytes===null,"NO_FAKE_BROWSER");
 check(r.rights_claim===expectedRights[i]&&typeof r.credit==="string"&&r.credit.length>10&&typeof r.authority==="string","LICENSE");
 check(r.visual_relation===expectedRelations[i],"FRAME_CUSTODY");
 check(r.item_rights_review_pending===true&&r.pixel_match_confirmed===false&&r.copy_approved===false&&r.wp_upload_approved===false&&r.downloaded_sha256===null,"HOLD_RELEASE");
 check(typeof r.source_catalog_url==="string"&&r.source_catalog_url.startsWith("https://"),"CATALOG");
 if(r.native_catalog_px===null)check(r.conditional_960px===null,"NO_INVENTED_PIXELS");
 else{
 const a=r.native_catalog_px;
 check(Array.isArray(a)&&a.length===2&&a.every(x=>Number.isInteger(x)&&x>0),"NATIVE_GEOMETRY");
 if(Array.isArray(a)&&a.length===2&&a.every(x=>Number.isInteger(x)&&x>0)){
 const w=Math.min(960,a[0]);check(Array.isArray(r.conditional_960px)&&r.conditional_960px[0]===w&&r.conditional_960px[1]===Math.round(a[1]*w/a[0]),"NO_DISTORT_OR_UPSCALE");
 }
 }
 check(r.candidate_image_file_url===null||r.candidate_image_file_url.startsWith("https://upload.wikimedia.org/wikipedia/commons/"),"REAL_IMAGE_ROUTE");
 if(i===1)check(r.source_catalog_url.includes("trench_construction.png"),"ARCHIVAL_TRENCH");
 if(i===4)check(r.source_catalog_url.includes("/p15141coll5/id/654"),"USACE_654");
 if(i===3)check(r.rights_claim==="CC_BY_SA_4_0"&&r.visual_relation==="RELATED_PLAN_DIFFERENT_VERSION","NO_COLOR_PLAN_SWAP");
 if(i===5)check(r.candidate_image_file_url===null&&r.rights_claim==="RIGHTS_UNKNOWN","PAPER_RIGHTS_HOLD");
 }
 return errors;
}
module.exports={validate};
