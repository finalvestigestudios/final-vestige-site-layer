/* Optional enhancement only. No fetch, cookies, tracking, storage, or server writes. */
(()=>{'use strict';
  const init=(root)=>{
    if(root.dataset.fvR437Init==='yes')return;
    const list=root.querySelector('[data-r437-records]');
    if(!list)return;
    const plates=Array.from(list.querySelectorAll('[data-period]'));
    if(plates.length!==4)return;
    const controls=document.createElement('div');
    controls.className='fv-r437__controls';
    controls.setAttribute('role','group');
    controls.setAttribute('aria-label','Filter the four sourced records');
    const status=document.createElement('p');
    status.className='fv-r437__status';
    status.setAttribute('role','status');
    status.setAttribute('aria-live','polite');
    const options=[['all','All records'],['incident','1967 records'],['retrospective','Later accounts']];
    const buttons=[];
    const show=(value)=>{
      let visible=0;
      for(const plate of plates){const on=value==='all'||plate.dataset.period===value;plate.hidden=!on;if(on)visible++;}
      buttons.forEach(btn=>btn.setAttribute('aria-pressed',String(btn.dataset.filter===value)));
      status.textContent=`Showing ${visible} of ${plates.length} source records. Dates are identified as event, finding, exhibit or publication.`;
    };
    for(const [value,label] of options){
      const button=document.createElement('button');
      button.type='button';button.dataset.filter=value;button.textContent=label;
      button.addEventListener('click',()=>show(value));
      controls.appendChild(button);buttons.push(button);
    }
    list.before(controls,status);
    root.dataset.fvR437Init='yes';
    show('all');
  };
  const start=()=>document.querySelectorAll('[data-fv-r437]').forEach(init);
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
