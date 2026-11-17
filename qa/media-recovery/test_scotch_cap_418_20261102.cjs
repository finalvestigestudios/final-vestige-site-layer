'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const {validate}=require('./validate_scotch_cap_418_20261102.cjs');
const p=require('./scotch_cap_418_uscg_noaa_20261102.json');
const originals=p.rows.map(x=>({source_url:x.source_url,alt:x.alt}));
const clone=()=>JSON.parse(JSON.stringify(p));
test('exact audited six published sources pass',()=>{assert.deepEqual(validate(clone(),originals),{ok:true,errors:[]})});
const mutations=[
 ['wrong source',x=>x.rows[2].source_url+='?guess=1'],
 ['ALT rewritten',x=>x.rows[1].alt='Just a boat'],
 ['new browser status invented',x=>x.rows[1].independent_retrieval.guest_browser_http_status=403],
 ['false visitor failure',x=>x.rows[2].independent_retrieval.visibly_broken_in_guest_browser=true],
 ['wrapper 403 promoted to origin 403',x=>x.rows[1].independent_retrieval.origin_http_status=403],
 ['fake transfer',x=>x.rows[4].independent_retrieval.guest_browser_encoded_transfer_bytes=100000],
 ['unverified dimensions',x=>x.rows[5].conditional_derivative.target_width_px=960],
 ['automatic WP copy',x=>x.rows[2].caching.wordpress_media_cache_permitted=true],
 ['wrong NOAA event year',x=>x.external_historical_conflict.correct_disaster_year=1964],
 ['hide NOAA gallery warning',x=>x.external_historical_conflict.chronology_gate='IGNORE'],
 ['rights approved without evidence',x=>x.rows[2].authority.rights_review='CLEARED'],
 ['false binary identity',x=>x.rows[2].authority.exact_binary_identity_verified=true],
 ['third-party mirror falsely licensed',x=>x.third_party_mirror.third_party_mirror_caching_approved=true],
 ['fake measured claim',x=>x.corpus.claimed_76_percent_savings_wire_measured=true],
 ['fake repaired source',x=>x.corpus.production_repaired=1],
 ['duplicate image slot',x=>x.rows[2].image_key='418:1'],
 ['remove image',x=>x.rows.pop()],
 ['incorrect retrieval outcome',x=>x.rows[4].independent_retrieval.outcome='RETRIEVER_403'],
 ['unverified source parity',x=>x.source_evidence.current_authenticated_wp_readback=false],
 ['alter source blob SHA',x=>x.source_evidence.frozen_git_blob_sha='fake']
];
for(const [name,change]of mutations)test('fail closed: '+name,()=>{const x=clone();change(x);assert.equal(validate(x,originals).ok,false,name)});
test('external frozen source drift is rejected',()=>{const rows=originals.map(x=>({...x}));rows[4].source_url+='?changed';assert.equal(validate(clone(),rows).ok,false)});
