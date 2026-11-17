'use strict';
function validate(d){
 const no=(m)=>{throw Error(m)};
 if(d.schema!=='fv.media_recovery.tmi_285_aerial_v1'||d.post_id!==285||d.inventory.posts!==61||d.inventory.images!==355||d.inventory.offsite_origin!==288||d.inventory.wordpress_originals_over_1_5_mib!==13)no('census');
 if(!Array.isArray(d.images)||d.images.length!==6)d.images&&no('image slots');
 const urls=["https://live.staticflickr.com/7278/7447166686_5d24dff6db_b.jpg","https://i0.wp.com/www.squawkpoint.com/wp-content/uploads/2019/02/Three-Mile-Island-Control-Centre.jpg?ssl=1","https://blog.ucsusa.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg","https://i.insider.com/5d5eb5f754c75f23dc72ed4c?auto=webp&format=jpeg&width=800","https://images.pixels.com/images-medium-large-5/three-mile-island-damaged-reactor-core-nuclear-regulatory-commissionscience-photo-library.jpg","https://images.saymedia-content.com/.image/ar_16:9,c_fill,cs_srgb,fl_progressive,q_auto:eco,w_1200/MTg5ODU1MTM1NjYzNDAwNjM2/the-china-syndrome-blockbuster-movie-becomes-eerie-prophecy.jpg"];
 for(let i=0;i<6;i++){const x=d.images[i];if(!x||x.key!=='285:'+i||x.src!==urls[i]||!x.alt||x.guest_http_status!==null||x.guest_decoded!==null||x.guest_transfer_bytes!==null||x.source_kind!==(i===1?'external_jetpack_proxy':'external_direct'))no('stored source or fabricated browser evidence '+i)}
 const p=d.p0;if(p.key!=='285:5'||p.retriever_url!==urls[5]||p.retriever_result!=='404 Not Found'||p.web_wrapper_status!==404||p.actual_origin_status!==null||p.guest_browser_status!==null||p.broken_for_visitors!==null||p.network_bytes!==null)no('fabricated origin/browser 404');
 if(!Array.isArray(d.candidates)||d.candidates.length!==3)no('candidate count');
 for(let i=0;i<3;i++){const c=d.candidates[i],ids=['NARA-540012','NARA-540027','DOE-COLOR-COMMONS'];if(!c||c.id!==ids[i]||!c.catalog.startsWith('https://')||!c.archive.startsWith('https://www.archives.gov/')||!c.provenance||!c.rights_risk||!c.scene_warning||c.exact_match!==false||c.binary_sha256!==null||c.rights_approved!==false||c.wp_cache_approved!==false||c.post_rewrite_approved!==false)no('rights or identity '+i);
 const [w,h]=c.recorded_dimensions,[ow,oh]=c.proposed_dimensions;if(!Number.isInteger(w)||!Number.isInteger(h)||ow>960||ow>w||oh>h||Math.abs(oh-Math.round(h*ow/w))>1)no('resize '+i)}
 if(d.candidates[0].recorded_dimensions[0]!==2700||d.candidates[1].recorded_dimensions[0]!==2700||d.candidates[2].recorded_dimensions[0]!==2592||d.candidates[2].recorded_dimensions[1]!==2488||d.candidates[2].proposed_dimensions[1]!==921)no('catalog geometry');
 if(d.geometry_policy.max_width_px!==960||d.geometry_policy.no_upscale!==true||d.geometry_policy.dimensions_only_catalog_not_download_verified!==true)no('geometry policy');
 if(d.claims.broken_42_verified!==false||d.claims.weight_saving_76_verified!==false||d.claims.production_repairs!==0||Object.values(d.safety).some(x=>x!==true))no('unsafe claim/write');
 return true;
}
module.exports={validate};
if(require.main===module){const fs=require('node:fs'),p=require('node:path');validate(JSON.parse(fs.readFileSync(p.join(__dirname,'tmi_285_archive_aerial_provenance_20261102.json'),'utf8')));console.log('source rights audit PASS')}
