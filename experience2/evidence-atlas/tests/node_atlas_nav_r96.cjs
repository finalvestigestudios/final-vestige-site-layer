/* R96 deterministic source navigation state tests; real browser QA remains separate. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const {resolve}=require('node:path');
const script=fs.readFileSync(resolve(__dirname,'../tools/build_curated_atlas_r94.py'),'utf8');
const block=script.match(/JS='''([\s\S]*?)'''\n(?:def render)/);
assert.ok(block,'R94 generated JS must exist');
const js=block[1];
function fixture({partial=false,hash=''}={}){
  let focused=null,scrolled=null;
  const handlers=new Map();
  const node=(props={})=>({
    ...props,handlers:{},
    addEventListener(type,fn){this.handlers[type]=fn;},
    trigger(type){this.handlers[type]?.();},
    setAttribute(name,value){this[name]=value;},
    getAttribute(name){return this[name];}
  });
  const panel={hidden:true};
  const cards=Array.from({length:6},(_,i)=>node({
    id:'atlas-0'+(i+1),hidden:false,
    dataset:{precision:i===0?'month':'day',search:'source 0'+(i+1)+' catalog-'+(i+1)},
    focus(){focused=this.id;},scrollIntoView(){scrolled=this.id;}
  }));
  const buttons=['all','day','month'].map(filter=>node({dataset:{filter}}));
  const query=node({value:''}),status={textContent:'All records'},empty={hidden:true};
  const links=cards.map(c=>node({
    href:'#'+c.id,getAttribute(name){return name==='href'?this.href:null;}
  }));
  const win={
    addEventListener(type,fn){handlers.set(type,fn);},
    dispatch(type){handlers.get(type)?.();}
  };
  const loc={hash};
  const doc={
    querySelector(name){return {'#filters':panel,'#query':query,'#count':status,
      '#empty':partial?null:empty}[name]||null;},
    querySelectorAll(name){return {'.card':cards,'[data-filter]':buttons,
      'a[href^="#atlas-"]':links}[name]||[];},
    getElementById(id){return cards.find(c=>c.id===id)||null;}
  };
  vm.runInNewContext(js,{document:doc,window:win,location:loc,
    requestAnimationFrame(fn){fn();}},{timeout:1000});
  return {cards,buttons,query,panel,links,win,loc,
    get focused(){return focused;},get scrolled(){return scrolled;}};
}
let count=0;
function ok(value,message){assert.ok(value,message);count++;}
let f=fixture();
ok(!f.panel.hidden,'enhancement enabled only on complete markup');
ok(f.cards.every(c=>!c.hidden),'all six initially visible');
f.links[0].trigger('click');ok(f.focused==='atlas-01','native link focuses source');
f.buttons[1].trigger('click');ok(f.cards.filter(c=>!c.hidden).length===5,'day filter');
f.query.value='no-match';f.query.trigger('input');ok(f.cards.every(c=>c.hidden),'search can hide all');
f.links[0].trigger('click');
ok(f.cards.every(c=>!c.hidden),'same-hash source click restores records');
ok(f.query.value==='','same-hash click resets search');
ok(f.focused==='atlas-01','same-hash click retains keyboard focus');
f.buttons[2].trigger('click');f.query.value='absent';f.query.trigger('input');
f.loc.hash='#atlas-05';f.win.dispatch('hashchange');
ok(f.cards.every(c=>!c.hidden),'hashchange restores hidden source');
ok(f.query.value==='','hashchange resets query');
ok(f.focused==='atlas-05'&&f.scrolled==='atlas-05','history targets exact source');
f.buttons[2].trigger('click');f.loc.hash='#atlas-99';f.win.dispatch('hashchange');
ok(f.cards.filter(c=>!c.hidden).length===1,'invalid fragment cannot change filters');
f=fixture({hash:'#atlas-06'});ok(f.focused==='atlas-06','direct deep link focuses source');
f=fixture({partial:true});ok(f.panel.hidden&&f.cards.every(c=>!c.hidden),'partial markup fails open');
console.log(JSON.stringify({suite:'R96_DOM_NAV',assertions:count,pass:true,
  note:'Deterministic state unit tests; not Chromium or axe evidence'}));
