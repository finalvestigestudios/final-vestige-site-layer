'use strict';
const fs=require('node:fs'),path=require('node:path');
const {validate}=require('./validate_malbone_621_wp_rendition_gate_20261105.cjs');
function testCases(validate,audit){
 const valid=validate(audit);
 if(!valid.valid||valid.count!==2||valid.stored_bytes!==10352064)throw Error('valid baseline rejected');
 const mut=[
 ['wrong image URL',d=>d.images[0].exact_published_src+='?crop=1'],
 ['different post source',d=>d.images[1].wp_source_url+='x'],
 ['modified original dims',d=>d.images[0].wp_dimensions[0]=900],
 ['forged original size',d=>d.images[1].wp_filesize_bytes=1],
 ['wrong mime',d=>d.images[0].wp_mime='image/png'],
 ['ALT modified',d=>d.images[1].alt='map'],
 ['virtual false',d=>d.images[0].registered_sizes_virtual=false],
 ['invented HTML width',d=>d.images[0].html_width=960],
 ['invented HTML srcset',d=>d.images[1].html_srcset=true],
 ['forged intermediate 768 URL',d=>d.images[0].intermediate_768.url+='?fm=webp'],
 ['768 candidate presumed loaded',d=>d.images[1].intermediate_768.guest_decodes=true],
 ['768 status assumed',d=>d.images[0].intermediate_768.actual_http_status=200],
 ['1024 candidate changed',d=>d.images[1].intermediate_1024.dimensions[0]=960],
 ['1024 claimed loaded',d=>d.images[1].intermediate_1024.guest_decodes=true],
 ['960 enlarged',d=>d.images[0].candidate_derivative_960[0]=1000],
 ['960 crop drift',d=>d.images[1].candidate_derivative_960[1]=700],
 ['rights allowed',d=>d.images[0].provenance.rights='CLEARED'],
 ['insufficient attribution checks',d=>d.images[0].provenance.checklist=[]],
 ['invented guest status',d=>d.images[0].guest_http_status=200],
 ['invented decoded image',d=>d.images[0].guest_decode_ok=true],
 ['invented guest currentSrc',d=>d.images[0].guest_current_src=d.images[0].wp_source_url],
 ['invented bytes',d=>d.images[0].guest_encoded_transfer_bytes=100],
 ['invented original hash',d=>d.images[1].original_sha256='0'.repeat(64)],
 ['cache approved',d=>d.images[1].cache_authorized=true],
 ['WP upload enabled',d=>d.images[1].wp_upload_authorized=true],
 ['post rewrite enabled',d=>d.images[1].post_edit_authorized=true],
 ['release enabled',d=>d.approved_to_publish=true],
 ['fake CDP trace',d=>d.guest_trace_sha256='abcdef'],
 ['misstated 42 failures',d=>d.sitewide_broken_42='CONFIRMED'],
 ['misstated 76 savings',d=>d.reduction_76_percent='MEASURED'],
 ['post inline count off',d=>d.post.inline_images=5],
 ['storage bytes off',d=>d.wp_originals_stored_bytes=10352065],
 ['third slot added',d=>d.images.push(d.images[0])],
 ['altered post link',d=>d.post.url='https://example.com'],
 ['render stage greenlit',d=>d.staging_gate='APPROVED']
 ];
 for(const [name,fn] of mut){const x=JSON.parse(JSON.stringify(audit));fn(x);let rejected=false;try{validate(x)}catch(_){rejected=true}if(!rejected)throw Error('Accepted invalid mutation '+name)}
 return {pass:mut.length+1,mutation_rejections:mut.length};
}
const audit=JSON.parse(fs.readFileSync(path.join(__dirname,'malbone_621_wp_rendition_gate_20261105.json'),'utf8'));
const r=testCases(validate,audit); console.log(r.pass+'/'+r.pass+' passed; '+r.mutation_rejections+' fail-closed mutations');
