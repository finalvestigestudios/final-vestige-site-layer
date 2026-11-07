'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {validate,fileMeta}=require('./validate_commons_redirect_20261106.cjs');
const originals=[1,2,3,4].map(n=>JSON.parse(fs.readFileSync(path.join(__dirname,'commons_redirect_20261106_shard0'+n+'.json'),'utf8')));
const clone=()=>structuredClone(originals);
test('all 24 published article sources pinned to 124 exact Commons redirect URLs',()=>{
 const a=validate(clone());
 assert.deepEqual(a.errors,[]);
 assert.equal(a.ok,true);
 assert.deepEqual(a.metrics,{published_posts:24,exact_redirect_sources:124,requested_1280:79,requested_960:17,requested_900:2,unspecified_width:26,license_clearances:0,visitor_confirmed_failures:0,wordpress_writes:0});
});
test('Wikimedia file lookup is only derived from original path, never assumed to exist',()=>{
 const u='https://commons.wikimedia.org/wiki/Special:Redirect/file/Archimedes%20Palimpsest.jpg?width=1280';
 assert.deepEqual(fileMeta(u),{title:'Archimedes Palimpsest.jpg',width:1280,lookup:'https://commons.wikimedia.org/wiki/File:Archimedes_Palimpsest.jpg'});
});
test('unencoded spaces cannot create duplicate or arbitrary candidate destinations',()=>{
 assert.throws(()=>fileMeta('https://commons.wikimedia.org/wiki/Special:Redirect/file/Fake%GG.jpg'));
 assert.throws(()=>fileMeta('https://commons.wikimedia.org/wiki/Special:Redirect/file/a/b.jpg'));
 assert.throws(()=>fileMeta('http://commons.wikimedia.org/wiki/Special:Redirect/file/a.jpg'));
 assert.throws(()=>fileMeta('https://commons.wikimedia.org/wiki/Special:Redirect/file/a.jpg?width=960&width=1280'));
});
function rejects(label,mutate){test(label,()=>{const a=clone();mutate(a);assert.equal(validate(a).ok,false);});}
rejects('no silent omission of one image',s=>s[0].images.pop());
rejects('no fabricated browser failure',s=>s[0].images[0].browser_http=404);
rejects('no fabricated license clearance',s=>s[0].images[0].rights_cleared=true);
rejects('no fabricated transfer savings',s=>s[1].images[0].wire_savings_percent=76);
rejects('no different source substituted',s=>s[1].images[0].stored_src='https://example.com/a.jpg');
rejects('no arbitrary Commons file page',s=>s[1].images[0].catalog_lookup_url='https://commons.wikimedia.org/wiki/File:Not_It.jpg');
rejects('no image slot moved',s=>s[2].images[0].image_index=150);
rejects('no unrelated post association',s=>s[2].images[0].post_url='https://finalvestige.com/a');
rejects('no duplicate source URL',s=>s[2].images[1].stored_src=s[2].images[0].stored_src);
rejects('no invented width',s=>s[2].images[0].requested_width_px=5000);
rejects('no missing article',s=>s[3].posts.pop());
rejects('no changed image catalog identity',s=>s[3].images[0].commons_file_title_unverified='Wrong.jpg');
rejects('no synthetic clearance in caption hint',s=>s[3].images[0].license_hints_from_caption.push('LICENSE VERIFIED'));
rejects('no mismatched post counts',s=>s[3].posts[0].commons_redirects++);
rejects('no HTTP source',s=>s[3].images[0].stored_src='http://commons.wikimedia.org/img.jpg');
rejects('no swapped image ID',s=>s[3].images[0].key='999:1');

rejects('no missing WordPress recensus revision',s=>s[0].posts[0].modified_wp='');
