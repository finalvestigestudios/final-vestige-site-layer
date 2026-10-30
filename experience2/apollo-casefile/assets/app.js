/* Unintrusive Experience 2.0 enhancement. No network calls, cookies, telemetry or dependencies. */
(()=>{'use strict';
 const root=document;
 const tools=root.querySelector('[data-ex2-atlas-tools]');
 const search=root.querySelector('[data-ex2-atlas-search]');
 const filter=root.querySelector('[data-ex2-atlas-filter]');
 const items=[...root.querySelectorAll('[data-ex2-atlas-item]')];
 const count=root.querySelector('[data-ex2-atlas-status]');
 const empty=root.querySelector('[data-ex2-atlas-empty]');
 if(tools&&search&&filter&&count&&empty&&items.length){
   try{
     const update=()=>{
       const q=search.value.trim().toLocaleLowerCase();const theme=filter.value;
       let shown=0;
       items.forEach(item=>{const visible=(theme==='all'||item.dataset.ex2Theme===theme)&&(!q||item.dataset.ex2Search.includes(q));item.hidden=!visible;if(visible)shown++});
       count.textContent=`${shown} of ${items.length} investigations`;empty.hidden=shown!==0;
     };
     search.addEventListener('input',update);filter.addEventListener('change',update);
     update();tools.hidden=false;
   }catch(_){items.forEach(item=>item.hidden=false);empty.hidden=true;tools.hidden=true;}
 }
 /* A missing/throwing IntersectionObserver must not hide or change any evidence. */
 const sections=[...root.querySelectorAll('[data-ex2-stage]')];
 const links=[...root.querySelectorAll('[data-ex2-rail-link]')];
 if(typeof IntersectionObserver!=='function'||sections.length!==6||links.length!==6)return;
 let observer;
 try{
   observer=new IntersectionObserver(entries=>{
     for(const entry of entries){if(!entry.isIntersecting)continue;
       links.forEach(link=>{if(link.hash===`#${entry.target.id}`){link.setAttribute('aria-current','location')}else{link.removeAttribute('aria-current')}});
     }
   },{rootMargin:'-10% 0px -65% 0px',threshold:0});
   sections.forEach(section=>observer.observe(section));
 }catch(_){if(observer)observer.disconnect();links.forEach(link=>link.removeAttribute('aria-current'));}
})();
