'use strict';
const t=require('node:test'),a=require('node:assert/strict');
const src=require('./p0_primary_candidate_0826.json');
const {verify}=require('./validate_p0_primary_candidate_0826.cjs');
const fixture=()=>structuredClone(src);
t('real ledger held, no autosubstitution',()=>{let x=verify(fixture());a.equal(x.source_origin_http_404,2);a.equal(x.production_writes,0)});
const changes=[
['origin drift',x=>x.rows[0].origin_url='https://bad.example/img.jpg'],
['invent guest 404',x=>x.rows[0].guest_http=404],
['invent guest decoded',x=>x.rows[0].guest_decoded=true],
['invent transfer bytes',x=>x.rows[0].guest_bytes=50000],
['invent 42',x=>x.claimed_42_browser_broken=42],
['invent 76%',x=>x.claimed_76_percent_wire_verified=true],
['approve rehost',x=>x.auto_rehost=true],
['WP write',x=>x.wordpress_write=true],
['wrong Navy accession',x=>x.rows[0].accession='80-G-227987'],
['false exact Florida photo',x=>x.rows[1].candidate_role='possible_same_historical_frame_unverified_crop'],
['Florida incorrect date',x=>x.rows[1].date='1987-01-01'],
['invent Florida pixels',x=>x.rows[1].candidate_raster_catalog=[960,600]],
['remove rights hold',x=>x.rights_review='APPROVED'],
['over width',x=>x.max_derivative_width=1024],
['upscale',x=>x.no_upscaling=false],
['duplicate slot',x=>x.rows[1].slot='274:6'],
['remove row',x=>x.rows.pop()],
['wrong preview',x=>x.rows[0].existing_preview=[960,780]],
['unverified file hash',x=>x.rows[0].new_sha256='abc'],
['no source provenance',x=>x.basis_blob='unknown'],
];
for(const [name,fn] of changes)t(name,()=>{let x=fixture();fn(x);a.throws(()=>verify(x))});
