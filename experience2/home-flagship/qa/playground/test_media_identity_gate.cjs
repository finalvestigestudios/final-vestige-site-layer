'use strict';
/* Dependency-free PHP CLI regression: controlled synthetic headers, never historical imagery. */
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const crypto=require('node:crypto'),{execFileSync}=require('node:child_process');
const TEMPLATE=path.join(__dirname,'fv-ex2-playground.php.template');
const SPEC=[
 ['apollo.webp',78346,1041,810,'webp'],
 ['franklin.jpg',466043,960,1526,'jpeg'],
 ['nypl.jpg',5553669,5667,3831,'jpeg']
];
function synthetic(name,size,w,h,kind) {
 const b=Buffer.alloc(size,0);
 if(kind==='webp'){
  b.write('RIFF',0);b.writeUInt32LE(size-8,4);b.write('WEBP',8);b.write('VP8X',12);
  b.writeUInt32LE(10,16);b.writeUIntLE(w-1,24,3);b.writeUIntLE(h-1,27,3);
 } else if(kind==='jpeg'){
  Buffer.from('ffd8ffe000104a46494600010100000100010000ffc0001108','hex').copy(b,0);
  b.writeUInt16BE(h,25);b.writeUInt16BE(w,27);
  Buffer.from('03012200021101031101ffd9','hex').copy(b,29);
 } else if(kind==='gif'){
  b.write('GIF89a',0);b.writeUInt16LE(w,6);b.writeUInt16LE(h,8);
 } else throw new Error(kind);
 return b;
}
function sha(b){return crypto.createHash('sha256').update(b).digest('hex')}
function phpLiteral(hashes) {
 return 'array('+Object.keys(hashes).map(k=>"'"+k+"' => '"+hashes[k]+"'").join(',')+')';
}
function inSandbox(fn) {
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'fv-media-identity-'));
 try {
  const media=path.join(dir,'media');fs.mkdirSync(media);
  const files={};
  for(const [name,size,w,h,kind] of SPEC){
   const b=synthetic(name,size,w,h,kind);files[name]=b;fs.writeFileSync(path.join(media,name),b);
  }
  const trusted=Object.fromEntries(Object.entries(files).map(([k,v])=>[k,sha(v)]));
  const template=fs.readFileSync(TEMPLATE,'utf8');
  function build(trust=trusted){
   let content=template.replace('__FV_EXPECTED_HASHES__','array()')
    .replace('__FV_ENQUEUE_STATEMENTS__','')
    .replace('__FV_TRUSTED_MEDIA_SHA256__',phpLiteral(trust));
   assert(!content.includes('__FV_'),'markers expanded');
   fs.writeFileSync(path.join(dir,'stage.php'),content);
  }
  function inspect(host='http://localhost',allow=true){
   const command="define('ABSPATH','/');"+(allow?"define('FV_EX2_ALLOW_LOCAL_REVIEW',true);":'')
    +"function wp_get_environment_type(){return 'local';}"
    +"function home_url($p='/'){return getenv('FV_TEST_HOST').$p;}"
    +"function add_action($a,$b){}function add_shortcode($a,$b){}"
    +"include getenv('FV_TEST_PLUGIN');"
    +"echo json_encode(array('safe'=>fv_ex2_safe_stage(),'integrity'=>fv_ex2_integrity(),'ready'=>fv_ex2_ready()));";
   return JSON.parse(execFileSync('php',['-r',command],{encoding:'utf8',
    env:{...process.env,FV_TEST_PLUGIN:path.join(dir,'stage.php'),FV_TEST_HOST:host}}));
  }
  return fn({dir,media,files,trusted,build,inspect});
 } finally {fs.rmSync(dir,{recursive:true,force:true})}
}
test('controlled media headers: matching MIME/size/dimensions + explicitly trusted hashes can pass',()=>inSandbox(s=>{
 s.build();assert.deepEqual(s.inspect(),{safe:true,integrity:true,ready:true});
}));
test('modified media content same filename, byte count, MIME and dimensions is rejected',()=>inSandbox(s=>{
 s.build();const f=path.join(s.media,'nypl.jpg');const b=Buffer.from(s.files['nypl.jpg']);b[b.length-1]=1;fs.writeFileSync(f,b);
 assert.equal(s.inspect().integrity,false);
}));
test('GIF masquerading as named WebP original with same bytes/dimensions is rejected',()=>inSandbox(s=>{
 s.build();const [name,size,w,h]=SPEC[0];fs.writeFileSync(path.join(s.media,name),synthetic(name,size,w,h,'gif'));
 assert.equal(s.inspect().integrity,false);
}));
test('without a separately reviewed media hash manifest, refuse all evidence images',()=>inSandbox(s=>{
 s.build({});assert.equal(s.inspect().integrity,false);
}));
test('missing original must be refused',()=>inSandbox(s=>{
 s.build();fs.unlinkSync(path.join(s.media,'franklin.jpg'));assert.equal(s.inspect().integrity,false);
}));
test('deny production-looking host and absent approval even with synthetic valid media',()=>inSandbox(s=>{
 s.build();assert.equal(s.inspect('https://finalvestige.com').safe,false);
 assert.equal(s.inspect('http://localhost',false).safe,false);
}));
