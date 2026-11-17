/* Progressive enhancement: no fetch, storage, cookies, analytics or auto-selection. */
(()=>{'use strict';
 const init=root=>{
   if(root.dataset.r438Ready==='true')return;
   const cards=[...root.querySelectorAll('[data-r438-card]')];
   const box=root.querySelector('[data-r438-comparison]');
   if(cards.length!==5||!box)return;
   const selections=[];const buttons=[];
   const group=document.createElement('div');group.className='fv-r438__actions';group.setAttribute('role','group');group.setAttribute('aria-label','Compare two NASA source records');
   const hint=document.createElement('p');hint.className='fv-r438__compare-help';hint.setAttribute('role','status');hint.setAttribute('aria-live','polite');
   const render=()=>{
     for(let i=0;i<buttons.length;i++){const selected=selections.includes(i);buttons[i].setAttribute('aria-pressed',String(selected));buttons[i].textContent=selected?'Selected: '+cards[i].querySelector('h3').textContent:'Compare: '+cards[i].querySelector('h3').textContent;}
     hint.textContent=selections.length===2?'Two sources selected for comparison.':`Choose ${2-selections.length} more source${2-selections.length===1?'':'s'} to compare; selection does not prove causation.`;
     box.replaceChildren();box.hidden=selections.length!==2;
     if(selections.length===2){
       const title=document.createElement('h3');title.textContent='Side-by-side evidence boundaries';box.appendChild(title);
       const grid=document.createElement('div');grid.className='fv-r438__compare-grid';
       for(const i of selections){
         const src=cards[i],cell=document.createElement('article'),heading=document.createElement('h4');heading.textContent=src.querySelector('h3').textContent;cell.appendChild(heading);
         for(const [label,selector] of [['Supports','[data-r438-supports]'],['Cannot prove','[data-r438-limit]']]){
           const p=document.createElement('p');const strong=document.createElement('strong');strong.textContent=label+': ';p.appendChild(strong);p.appendChild(document.createTextNode(src.querySelector(selector).textContent));cell.appendChild(p);
         }grid.appendChild(cell);
       }box.appendChild(grid);
       const clear=document.createElement('button');clear.type='button';clear.textContent='Clear comparison';clear.addEventListener('click',()=>{selections.length=0;render();buttons[0].focus()});box.appendChild(clear);
     }
   };
   cards.forEach((card,i)=>{
     const button=document.createElement('button');button.type='button';button.dataset.r438Pick=card.dataset.r438Card;
     button.addEventListener('click',()=>{const at=selections.indexOf(i);if(at!==-1)selections.splice(at,1);else if(selections.length<2)selections.push(i);else{selections.shift();selections.push(i)}render()});
     buttons.push(button);group.appendChild(button);
   });
   group.appendChild(hint);root.querySelector('[data-r438-atlas]').after(group,box);render();root.dataset.r438Ready='true';
 };
 const start=()=>document.querySelectorAll('[data-r438-atlas-root]').forEach(init);
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
