/* R450: voluntary local .txt export. No network, cookies, beacons or user input collected. */
(()=>{'use strict';
  const init=root=>{
    if(root.dataset.r450Ready==='yes')return;
    const records=[...root.querySelectorAll('[data-r450-claim]')];
    const target=root.querySelector('[data-r450-export]');
    const status=root.querySelector('[data-r450-status]');
    if(!target||!status||records.length!==4)return;
    const button=document.createElement('button');button.type='button';
    button.textContent='Download original four-source receipt (.txt)';
    button.addEventListener('click',()=>{
      const lines=['FINAL VESTIGE — APOLLO 1 SOURCE AND INFERENCE RECEIPT',
        'Original classroom/research note; NOT a NASA publication or endorsement.',
        'Historical interpretation pending independent Final Vestige editorial review.',
        'All official documents remain free. No commercial rights to NASA images are claimed.',''];
      for(const record of records){
        const title=record.querySelector('h3');
        const paragraphs=[...record.querySelectorAll('p')];
        if(!title||paragraphs.length!==4){status.textContent='Receipt export unavailable; review the visible source cards instead.';return;}
        lines.push(title.textContent.trim(),...paragraphs.map(p=>p.textContent.trim()));
        const source=record.querySelector('a[href]');
        if(!source||!/^https:\/\/www\.nasa\.gov\//.test(source.href)){
          status.textContent='Receipt export unavailable; review the visible source cards instead.';return;
        }
        lines.push('SOURCE URL: '+source.href,'');
      }
      lines.push('Full original investigation (free): https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/','');
      const url=URL.createObjectURL(new Blob([lines.join('\n')],{type:'text/plain;charset=utf-8'}));
      const anchor=document.createElement('a');anchor.href=url;anchor.download='fv-apollo-1-original-evidence-receipt.txt';anchor.hidden=true;
      root.append(anchor);anchor.click();anchor.remove();
      setTimeout(()=>URL.revokeObjectURL(url),3000);
      status.textContent='Source receipt downloaded locally. No answers or information were submitted.';
    });
    target.append(button);root.dataset.r450Ready='yes';
  };
  const start=()=>document.querySelectorAll('[data-fv-r450]').forEach(init);
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
