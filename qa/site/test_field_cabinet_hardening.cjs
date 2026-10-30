"use strict";
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const source = fs.readFileSync(path.join(__dirname, 'field_cabinet_hardened_wp_block.html'), 'utf8');
const match = source.match(/<script>([\s\S]*?)<\/script>/);
assert.ok(match, 'review block contains exactly one script');
const script = match[1];
assert.equal((source.match(/<script>/g)||[]).length, 1);

function setup(initial, options={}) {
  const values=new Map([['fvFieldCabinetV1',JSON.stringify(initial)]]);
  const selectors=[
    '[data-fv-cabinet-status]','[data-fv-cabinet-message]',
    '[data-fv-cabinet-continue]','[data-fv-cabinet-investigations]',
    '[data-fv-cabinet-research]','[data-fv-cabinet-tools]',
    '[data-fv-cabinet-recent]','[data-fv-import]',
    '[data-fv-clear-recent]','[data-fv-export]','[data-fv-copy-list]'
  ];
  const nodes=Object.fromEntries(selectors.map(selector=>[selector,{
    innerHTML:'', textContent:'', listeners:{},
    addEventListener(name,cb){this.listeners[name]=cb;}
  }]));
  const doc={
    querySelector(selector){return nodes[selector]??null;},
    querySelectorAll(){return [];},
    createElement(){return {href:'',download:'',click(){}};}
  };
  const storage={
    getItem(key){return values.get(key)??null;},
    setItem(key,value){values.set(key,value);}
  };
  const win={location:{origin:'https://finalvestige.com'},addEventListener(){},prompt(){}};
  class Reader{
    readAsText(file){this.result=file.content;this.onload();}
  }
  vm.runInNewContext(script,{
    document:doc,window:win,localStorage:storage,FileReader:Reader,
    URL,Blob,setTimeout,navigator:{clipboard:{writeText:async()=>{}}}
  },{timeout:1500});
  return {
    nodes,
    html:()=>Object.values(nodes).map(n=>n.innerHTML||'').join('\n'),
    saved:()=>JSON.parse(values.get('fvFieldCabinetV1')),
    importJSON:(data,size=500)=>{
      nodes['[data-fv-import]'].listeners.change({
        target:{files:[{size,content:JSON.stringify(data)}]}
      });
    },
    message:()=>nodes['[data-fv-cabinet-message]'].textContent
  };
}
const good={id:'a',title:'The Archive Trail',url:'/the-archive-trail/',type:'research'};
const malicious=(url,id='evil')=>({id,title:'malicious',url,type:'research'});

test('source is a Gutenberg HTML block with no added network requests',()=>{
  assert.equal(source.includes('<!-- wp:html -->'),true);
  assert.equal(source.includes('<!-- /wp:html -->'),true);
  for(const token of ['fetch(', 'XMLHttpRequest','document.cookie'])assert.equal(script.includes(token),false,token);
});
test('valid relative and absolute HTTPS saved links remain accessible',()=>{
  const app=setup({saved:[good,{id:'b',title:'Test',url:'https://example.org/manual',type:'research'}]});
  assert.match(app.html(),/href="https:\/\/finalvestige\.com\/the-archive-trail\/"/);
  assert.match(app.html(),/href="https:\/\/example\.org\/manual"/);
});
test('malicious stored URL schemes cannot become clickable hrefs',()=>{
  const app=setup({saved:[
    malicious('javascript:alert(1)','j'),
    malicious('data:text/html,<script>alert(1)</script>','d'),
    malicious('vbscript:alert(1)','v'),
    malicious('file:///private/thing','f'),
    good
  ]});
  assert.doesNotMatch(app.html(),/href="(?:javascript|data|vbscript|file):/i);
  assert.doesNotMatch(app.html(),/malicious/);
  assert.match(app.html(),/The Archive Trail/);
});
test('newlines and control characters cannot disguise dangerous URL schemes',()=>{
  const app=setup({saved:[
    malicious('java\nscript:alert(1)','a'),
    malicious('\tjavascript:alert(1)','b'),
    malicious('javascript:\ralert(1)','c')
  ]});
  assert.doesNotMatch(app.html(),/malicious/);
});
test('user information in URL authority cannot be smuggled into an href',()=>{
  const app=setup({saved:[malicious('https://trusted.example@evil.example/a')]});
  assert.doesNotMatch(app.html(),/malicious/);
});
test('unsafe imported records are discarded while legitimate saved items remain',()=>{
  const app=setup({saved:[good]});
  app.importJSON({saved:[malicious('javascript:alert(1)'),{id:'ok',title:'New Source',url:'https://finalvestige.com/what-survives/',type:'research'}]});
  const items=app.saved().saved;
  assert.equal(items.length,2);
  assert.equal(items.some(x=>x.id==='evil'),false);
  assert.equal(items.some(x=>x.id==='ok'),true);
  assert.equal(items.some(x=>x.id==='a'),true);
});
test('unsafe reading-progress URLs are rejected on import',()=>{
  const app=setup({saved:[]});
  app.importJSON({saved:[],reading:{bad:{title:'Unsafe',url:'javascript:alert(1)'},good:{title:'Safe',url:'/what-survives/'}}});
  const reading=app.saved().reading;
  assert.equal(Object.hasOwn(reading,'bad'),false);
  assert.equal(Object.hasOwn(reading,'good'),true);
});
test('legacy unsafe reading links are not rendered',()=>{
  const app=setup({saved:[],reading:{bad:{title:'malicious',url:'data:text/html,foo'}}});
  assert.doesNotMatch(app.html(),/malicious/);
});
test('oversized import is rejected without altering stored saves',()=>{
  const app=setup({saved:[good]});
  app.importJSON({saved:[{id:'new',title:'New',url:'/new/'}]},2*1024*1024+1);
  assert.equal(app.saved().saved.length,1);
  assert.match(app.message(),/too large/);
});
test('bad shapes in localStorage do not crash rendering',()=>{
  const app=setup({saved:{oops:1},recent:'bad',reading:5});
  assert.match(app.html(),/Nothing here yet/);
});
test('text and attributes are escaped even for attacker-supplied titles',()=>{
  const app=setup({saved:[{id:'c',title:'"><img src=x onerror=alert(1)>',url:'/the-archive-trail/',type:'research'}]});
  assert.doesNotMatch(app.html(),/<img src=x/);
  assert.match(app.html(),/&lt;img/);
});
test('reading-progress return links have safe composed URL',()=>{
  const app=setup({saved:[],reading:{article:{title:'Current chapter',url:'/the-archive-trail/',lastSection:'sources'}}});
  assert.match(app.html(),/the-archive-trail\/#sources/);
});
test('import preserves existing legitimate item and its original ID',()=>{
  const app=setup({saved:[good]});
  app.importJSON({saved:[]});
  assert.equal(app.saved().saved[0].id,'a');
});
test('a file with no saved array is handled without writing',()=>{
  const app=setup({saved:[good]});
  app.importJSON({reading:{foo:{url:'https://example.org'}}});
  assert.equal(app.saved().saved.length,1);
  assert.match(app.message(),/not a valid/);
});
