"use strict";
function run(src,validate){
 const copy=x=>JSON.parse(JSON.stringify(x));
 const insist=(v,m)=>{if(!v)throw Error("TEST_FAILED "+m)};
 let passed=0;insist(validate(src).images===54,"control");passed++;
 const trials=[
 ["wrong source",x=>x.rows[0].live_src+="?wrong=1"],
 ["wrong frozen",x=>x.rows[0].frozen_src+="?wrong=1"],
 ["alt drift",x=>x.rows[0].live_alt="false ALT"],
 ["missing row",x=>x.rows.pop()],
 ["repeated slot",x=>x.rows[1].slot=x.rows[0].slot],
 ["fake origin 404",x=>x.rows[0].origin_http_status=404],
 ["fake guest 200",x=>x.rows[0].guest_http_status=200],
 ["fake guest broken",x=>x.rows[0].guest_broken=true],
 ["fake wire bytes",x=>x.rows[0].guest_wire_bytes=1000],
 ["fake decoded width",x=>x.rows[0].guest_natural_px=[960,540]],
 ["fake currentSrc",x=>x.rows[0].guest_current_src=x.rows[0].live_src],
 ["invented width",x=>x.rows[0].html_width=960],
 ["invented srcset",x=>x.rows[0].literal_srcset_present=true],
 ["host mismatch",x=>x.rows[0].source_host="example.org"],
 ["not a redirect",x=>x.rows[0].is_commons_redirect=false],
 ["fake rights",x=>x.rows[0].rights_cleared=true],
 ["fake catalog rights",x=>x.rows[0].catalog_candidates[0].item_rights_cleared=true],
 ["fake pixel match",x=>x.rows[0].catalog_candidates[0].exact_image_match_verified=true],
 ["erase catalog",x=>x.rows[0].catalog_candidates=[]],
 ["erase catalog link",x=>{x.rows[0].catalog_candidates[0].catalog_url=null;x.rows[0].catalog_candidates[0].authoritative_primary_url=null;}],
 ["960 overflow",x=>{const row=x.rows.find(r=>r.catalog_candidates.some(c=>c.conditional_960px));row.catalog_candidates.find(c=>c.conditional_960px).conditional_960px[0]=961;}],
 ["upscale",x=>x.rows[0].staging.no_upscale=false],
 ["scene swap",x=>x.rows[0].staging.require_scene_identity=false],
 ["rehost",x=>x.rows[0].rehost_or_cache_approved=true],
 ["WP rewrite",x=>x.rows[0].wordpress_write_approved=true],
 ["false 76%",x=>x.unverified.network_saving_76pct_measured=true],
 ["false broken 42",x=>x.unverified.guest_confirmed_failures=42],
 ["invented CLS",x=>x.unverified.real_cls=0.2],
 ["wrong post count",x=>x.posts[0].live_image_count++],
 ["wrong source blob",x=>x.baseline.blob="bad"],
 ["alter tally",x=>x.counts.candidate_mapped=0],
 ["unauthorized policy",x=>x.policy.no_prod_wp_writes=false]
 ];
 for(const [name,mutate]of trials){const x=copy(src);mutate(x);let held=false;try{validate(x);}catch(e){held=true;}insist(held,name);passed++;}
 return {passed,failed:0,guest_browser_tested:false,native_node_compatible:true};
}
if(typeof require!=="undefined"&&require.main===module){const fs=require("node:fs"),path=require("node:path"),{validate}=require("./validate_live_part05_54_20261112.cjs");const d=JSON.parse(fs.readFileSync(path.join(__dirname,"live_part05_8posts_54_commons_20261112.json"),"utf8"));console.log(JSON.stringify(run(d,validate)));}
module.exports={run};
