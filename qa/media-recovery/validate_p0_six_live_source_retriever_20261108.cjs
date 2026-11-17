'use strict';
const CODES={"285:5":404,"285:2":500,"287:5":404,"418:1":403,"418:2":403,"407:1":400};
const IMMUTABLE={"285:5":{"post":"https://finalvestige.com/2026/08/19/the-light-said-closed-three-mile-island/","source":"https://images.saymedia-content.com/.image/ar_16:9,c_fill,cs_srgb,fl_progressive,q_auto:eco,w_1200/MTg5ODU1MTM1NjYzNDAwNjM2/the-china-syndrome-blockbuster-movie-becomes-eerie-prophecy.jpg","candidate":"https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg","rights":"PD_SELF","outcome":"NOT_FOUND"},"285:2":{"post":"https://finalvestige.com/2026/08/19/the-light-said-closed-three-mile-island/","source":"https://blog.ucsusa.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg","candidate":"https://blog.ucs.org/wp-content/uploads/2022/10/DBD-42-Figure-4-tmi-panel.jpg","rights":"UNKNOWN","outcome":"REDIRECT_TARGET_INACCESSIBLE"},"287:5":{"post":"https://finalvestige.com/2026/08/19/the-warning-was-a-man-waving-sunshine-skyway/","source":"https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg","candidate":"https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg","rights":"RIGHTS_UNVERIFIED","outcome":"NOT_FOUND"},"418:1":{"post":"https://finalvestige.com/2026/08/20/the-lighthouse-was-gone-at-dawn-1946-tsunami/","source":"https://media.defense.gov/2021/Mar/30/2002610812/1920/1080/0/210330-G-DE713-0002.JPG","candidate":"https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/","rights":"USCG_PUBLIC_DOMAIN_RELEASE_CATALOG","outcome":"FORBIDDEN"},"418:2":{"post":"https://finalvestige.com/2026/08/20/the-lighthouse-was-gone-at-dawn-1946-tsunami/","source":"https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg","candidate":"https://www.lighthousefriends.com/Scotch_Cap_debris2_1946.jpg","rights":"RIGHTS_UNVERIFIED","outcome":"FORBIDDEN"},"407:1":{"post":"https://finalvestige.com/2026/08/20/the-lake-wasnt-there-yesterday-hebgen/","source":"https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg","candidate":"https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/img7535.jpg","rights":"USGS_PUBLIC_DOMAIN_CATALOG","outcome":"UNSUPPORTED_OCTET_STREAM"}};
function validate(a) {
const e=[],fail=s=>e.push(s);
if(!a||typeof a!=='object'||Array.isArray(a))return ['invalid_audit'];
if(a.schema!=='fv-p0-six-wp-sources-retriever-20261108-v1'||a.date_local!=='2026-11-08'||!String(a.method).includes('neither origin nor guest browser HTTP'))fail('method_provenance');
if(a.frozen_git_source?.path!=='qa/media-recovery/p0_guest_browser_disposition_pending_20261105.json'||!/^[a-f0-9]{40}$/.test(a.frozen_git_source?.blob_sha||''))fail('frozen_git_source');
const c=a.counts||{},r=a.release||{};
if(c.posts_read!==4||c.p0_exact_wp_sources_verified!==6||c.wrapper_results!==6||c.wrapper_nonrender!==6||c.alternative_images_displayed!==2||c.documented_item_pd_claims!==3||c.visitor_confirmed_broken!==null||c.verified_broken_42!==false||c.measured_transfer_reduction_76!==false||c.historical_posts!==61||c.historical_images!==355||c.live_published_posts_previous_census!==66||c.oversize_originals_decimal_mb!==15||c.oversize_stored_original_bytes!==47096779)fail('claims_counts');
if(r.guest_browser_verification!==false||r.wordpress_writes!==0||r.binary_downloads!==0||r.cache_writes!==0||r.homepage_edits!==0||r.spend_usd!==0||r.all_replacements_hold!==true)fail('production_safety');
if(!Array.isArray(a.rows)||a.rows.length!==6)return [...new Set([...e,'six_p0_rows_required'])];
const keys=new Set(),urls=new Set();let disp=0,pd=0;
for(const x of a.rows) {
if(!Object.hasOwn(CODES,x.slot)||keys.has(x.slot))fail('invalid_or_duplicate_slot');keys.add(x.slot);
if(x.post_id!==Number(x.slot.split(':')[0])||![285,287,407,418].includes(x.post_id)||x.live_wp_post_published!==true||x.live_wp_exact_src_found!==true||!/^https:\/\/finalvestige\.com\//.test(x.post_url||'')||!/^2026-/.test(x.modified||'')||!/^https:\/\//.test(x.published_src||'')||urls.has(x.published_src))fail('live_wp_src');urls.add(x.published_src);
const expected=IMMUTABLE[x.slot]||{};
if(x.post_url!==expected.post||x.published_src!==expected.source)fail('immutable_live_source_identity');
const w=x.wrapper||{};
if(w.method!=='web.open'||w.date_local!=='2026-11-08'||w.tool_status!==CODES[x.slot]||typeof w.tool_result!=='string'||['origin_http','guest_http','guest_pixels','guest_bytes','guest_broken'].some(k=>w[k]!==null))fail('browser_wrapper_conflation');
if(w.tool_result!==expected.outcome)fail('wrapper_outcome_identity');
const v=x.candidate||{};
if(v.url!==expected.candidate||v.rights_evidence!==expected.rights)fail('immutable_candidate_rights_identity');
if(!/^https:\/\//.test(v.url||'')||!v.relationship||!v.rights_evidence||v.binary_sha256!==null||v.right_to_cache_or_republish_proven!==false||v.editor_approved!==false)fail('candidate_release');
if(v.rendered_by_retriever===true)disp++;
if(['PD_SELF','USCG_PUBLIC_DOMAIN_RELEASE_CATALOG','USGS_PUBLIC_DOMAIN_CATALOG'].includes(v.rights_evidence))pd++;
if(x.slot==='285:5'){
if(JSON.stringify(v.native_dimensions)!=='[819,614]'||JSON.stringify(v.conditional_max_960_derivative)!=='[819,614]')fail('tmi_no_upscale');
}else if(v.native_dimensions!==null||v.conditional_max_960_derivative!==null)fail('invented_native_size');
if(['fetch_binary','cache','wp_media','wp_post','homepage'].some(k=>x.actions?.[k]!==false))fail('unauthorized_action');
}
if(keys.size!==6||Object.keys(CODES).some(k=>!keys.has(k)))fail('missing_p0');
if(disp!==2||pd!==3)fail('candidate_count');
return [...new Set(e)];
}
module.exports={validate};
if(typeof require!=='undefined'&&require.main===module){
const a=JSON.parse(require('node:fs').readFileSync(process.argv[2]||'qa/media-recovery/p0_six_live_source_retriever_20261108.json','utf8'));
const e=validate(a);if(e.length){console.error('HOLD '+e.join(','));process.exitCode=1;}else console.log('PASS six P0 WP source readbacks; no visitor claims or writes');
}
