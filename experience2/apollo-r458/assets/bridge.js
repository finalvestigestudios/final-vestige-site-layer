/* Apollo R458: optional accessibility-preserving filters + local study-note download. */
(()=>{'use strict';
function init(root){if(root.dataset.fv458Ready==='1')return;
 const controls=root.querySelector('[data-fv458-filters]'),status=root.querySelector('[data-fv458-status]');
 const cards=[...root.querySelectorAll('[data-fv458-record]')],buttons=[...root.querySelectorAll('[data-fv458-choice]')];
 if(!controls||!status||cards.length!==5||buttons.length!==3)return;
 function show(choice){if(!['all','historical','retrospective'].includes(choice))return;
  let count=0;for(const card of cards){card.hidden=(choice!=='all'&&card.dataset.fv458Record!==choice);if(!card.hidden)count++;}
  for(const b of buttons)b.setAttribute('aria-pressed',String(b.dataset.fv458Choice===choice));
  status.textContent=`Showing ${count} of 5 source records. All records are available without JavaScript.`;
 }
 try{for(const b of buttons)b.addEventListener('click',()=>show(b.dataset.fv458Choice));
  const save=root.querySelector('[data-fv458-save]'),result=root.querySelector('[data-fv458-save-status]');
  if(save&&result&&typeof Blob!=='undefined'&&URL.createObjectURL){
   save.hidden=false;save.addEventListener('click',()=>{
    const lines=['Apollo 1 — independent evidence study note','',...cards.map(c=>c.querySelector('h3').textContent+' | '+c.querySelector('a[data-fv458-source]').href),
     '', 'Research question: How does a source identify a probable cause without proving one specific wire?',
     'Placement discrepancy: the homepage currently presents S67-19766 while the public Atlas lists it as not shown. This is a cross-page editorial-status difference, not a licensing verdict.',
     'This is not a rights clearance, paid product, or agency-endorsed lesson.'];
    const blob=new Blob([lines.join('\n')+'\n'],{type:'text/plain;charset=utf-8'});const url=URL.createObjectURL(blob);
    try{const anchor=document.createElement('a');anchor.href=url;anchor.download='apollo1-source-study-note.txt';anchor.style.display='none';root.append(anchor);anchor.click();anchor.remove();result.textContent='Study note prepared locally. No information was submitted.';}
    finally{setTimeout(()=>URL.revokeObjectURL(url),1500);}
   });
  }
  root.dataset.fv458Ready='1';controls.hidden=false;show('all');
 }catch(_){for(const c of cards)c.hidden=false;controls.hidden=true;status.textContent='All source records remain available.';}
}
function run(){document.querySelectorAll('[data-fv458-root]').forEach(init)}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',run,{once:true});else run();
})();
