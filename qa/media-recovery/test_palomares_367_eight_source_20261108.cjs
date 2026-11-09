'use strict';
const assert=require('node:assert/strict');
const original=require('./palomares_367_eight_source_20261108.json');
const {validate}=require('./validate_palomares_367_eight_source_20261108.cjs');
const clone=()=>JSON.parse(JSON.stringify(original));
const tests=[
['unaltered fixture',()=>{assert.equal(validate(clone()).ok,true)}],
['source swap',a=>{a.rows[0].exact_live_wp_src=a.rows[1].exact_live_wp_src}],
['wrong archival slot',a=>{a.rows[1].slot='367:3'}],
['fake guest HTTP 404',a=>{a.rows[0].retriever.guest_browser_http_status=404}],
['fake origin HTTP 200',a=>{a.rows[0].retriever.origin_http_status=200}],
['invented broken count',a=>{a.counts.visitor_broken_confirmed=42}],
['invented 76 percent claim',a=>{a.counts.claimed_76_percent_weight_saving_measured=true}],
['false license approval',a=>{a.rows[2].rights_final_clearance=true}],
['false download approval',a=>{a.rows[2].cache_authorized=true}],
['false post approval',a=>{a.rows[2].wp_post_authorized=true}],
['unearned sha256',a=>{a.rows[2].binary_sha256='f'.repeat(64)}],
['upscale original 500px',a=>{a.rows[6].conditional_max_width_960_px=[960,484]}],
['bad 960px height',a=>{a.rows[0].conditional_max_width_960_px=[960,600]}],
['faked native size',a=>{a.rows[0].original_catalog_px=[960,601]}],
['museum size fabricated',a=>{a.rows[3].conditional_max_width_960_px=[960,778]}],
['wrong license for route map',a=>{a.rows[0].rights_classification='PUBLIC_DOMAIN'}],
['phantom rendered image',a=>{a.rows[1].retriever.outcome='IMAGE_RENDERED'}],
['faked wrapper 500',a=>{a.rows[1].retriever.wrapper_http_status=500}],
['remove one external row',a=>{a.rows.pop()}],
['remove release hold',a=>{a.release.all_on_hold=false}],
['WordPress write claim',a=>{a.release.wordpress_writes=1}],
['legacy source fingerprint',a=>{a.source_custody.frozen_source_blob_sha='0'.repeat(40)}],
];
let passed=0;
for(const [name,edit] of tests){
  if(name==='unaltered fixture'){edit();passed++;continue;}
  const a=clone();edit(a);assert.equal(validate(a).ok,false,'mutant accepted: '+name);passed++;
}
console.log('Palomares recovery validation: '+passed+'/'+tests.length+' PASS');
