'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const {buildPriorityPlan,RELEASE_ORDER,BROWSER_ORDER}=require('./probe_p0_queue_core.cjs');
function fixture(){
  const rows=RELEASE_ORDER.map(key=>({image_key:key,post_id:Number(key.split(':')[0]),current_published_source_url:'https://archive.example.org/'+key+'.jpg',current_published_alt:'Historical image '+key,approval:{replacement_ready:false,media_cache_authorized:false,wordpress_upload_authorized:false,wordpress_post_edit_authorized:false}}));
  const extra={key:'287:5',post_id:287,source_url:'https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg',alt:'Skyway photo',source_kind:'external',allowed_to_localize:false};
  const posts=[...new Set([...RELEASE_ORDER.map(k=>Number(k.split(':')[0])),287,432,434,621])].map(id=>({id,url:'https://finalvestige.com/posts/'+id+'/',title:'test'}));
  const images=[...rows.map(r=>({key:r.image_key,post_id:r.post_id,source_url:r.current_published_source_url,alt:r.current_published_alt,source_kind:'external'})),extra];
  return {snapshot:{parts:[{posts,images},...Array.from({length:7},()=>({posts:[],images:[]}))]},release:{schema_version:1,rows}};
}
test('guest default targets all 11 critical images and 8 article URLs',()=>{const {snapshot,release}=fixture();const result=buildPriorityPlan(snapshot,release);assert.deepEqual(result.post_ids,[285,287,407,418,268,432,434,621]);assert.deepEqual(result.priority_image_keys,BROWSER_ORDER);assert.equal(result.priority_targets.length,11);assert.ok(result.priority_targets.every(r=>r.visitor_http_status===null&&!r.production_replacement_authorized));assert.equal(result.guest_browser_verified,false)});
test('old six-post queue misses urgent Three Mile Island and Skyway',()=>{const {snapshot,release}=fixture();const r=buildPriorityPlan(snapshot,release);assert.ok(r.post_ids.includes(285));assert.ok(r.post_ids.includes(287));assert.equal(r.priority_targets.find(x=>x.image_key==='285:5').post_id,285);assert.equal(r.priority_targets.find(x=>x.image_key==='287:5').post_id,287)});
const invalid=[
['source URL drift',(a)=>{a.snapshot.parts[0].images.find(x=>x.key==='285:5').source_url+='?changed'}],
['ALT drift',(a)=>{a.snapshot.parts[0].images.find(x=>x.key==='418:1').alt+='changed'}],
['queue URL drift',(a)=>{a.release.rows[0].current_published_source_url+='?unreviewed'}],
['queue ALT drift',(a)=>{a.release.rows[0].current_published_alt+='changed'}],
['missing hotlink',(a)=>{a.snapshot.parts[0].images=a.snapshot.parts[0].images.filter(x=>x.key!=='407:1')}],
['duplicate hotlink',(a)=>{a.snapshot.parts[1].images.push({...a.snapshot.parts[0].images[0]})}],
['duplicate queue key',(a)=>{a.release.rows[1].image_key=a.release.rows[0].image_key}],
['missing release row',(a)=>{a.release.rows.pop()}],
['unexpected release row',(a)=>{a.release.rows[0].image_key='100:0'}],
['unapproved replacement',(a)=>{a.release.rows[0].approval.replacement_ready=true}],
['unauthorized cache',(a)=>{a.release.rows[0].approval.media_cache_authorized=true}],
['unsafe destination page',(a)=>{a.snapshot.parts[0].posts.find(x=>x.id===285).url='https://evil.example/posts/285/'}],
['plain HTTP source',(a)=>{a.snapshot.parts[0].images.find(x=>x.key==='285:5').source_url='http://archive.example.org/a.jpg';a.release.rows[0].current_published_source_url='http://archive.example.org/a.jpg'}],
['Skyway relocation without re-audit',(a)=>{a.snapshot.parts[0].images.find(x=>x.key==='287:5').source_url='https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg'}],
['Skyway localization flip',(a)=>{a.snapshot.parts[0].images.find(x=>x.key==='287:5').allowed_to_localize=true}],
['missing legacy article',(a)=>{a.snapshot.parts[0].posts=a.snapshot.parts[0].posts.filter(x=>x.id!==621)}]
];
for(const [name,change]of invalid)test('fail closed: '+name,()=>{const x=fixture();change(x);assert.throws(()=>buildPriorityPlan(x.snapshot,x.release))});
