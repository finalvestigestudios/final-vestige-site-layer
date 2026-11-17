/* R440 private original classroom exercise export: no fetch, storage, forms, cookies or analytics. */
(()=>{'use strict';
  const sourceA='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/';
  const sourceB='https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/';
  const rights='https://www.nasa.gov/nasa-brand-center/advertising-guidelines/';
  const text=()=>[
    'FINAL VESTIGE | APOLLO 1 - ORIGINAL CLASSROOM EVIDENCE ACTIVITY',
    'Free original educational exercise; not a NASA-endorsed or official NASA product.',
    'Task: Compare evidence from an original investigation with a later retrospective.','',
    '1. Which date belongs to the ground test and which to the later publication?',
    '2. What probable initiator did the 1967 Review Board identify?',
    '3. Why do later controlled flammability tests not identify the original spark?','',
    'INSTRUCTOR RUBRIC / EVIDENCE LIMITS',
    'Chronology: January 27, 1967 was the accident; later experiments followed and the retrospective was published in February 2018.',
    'Cause: An electrical arc was the most probable initiator; no single ignition source was conclusively established.',
    'Limits: Later experiments show fire hazards and redesign evidence, not a proven initial spark.',
    'Rights: NASA historical sources do not confer commercial rights or imply NASA endorsement.','',
    'PRIMARY: '+sourceA,
    'LATER NASA HISTORY: '+sourceB,
    'NASA COMMERCIAL MEDIA GUIDANCE: '+rights,
    'Full free FV investigation: https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/',''
  ].join('\n');
  function init(root){
    if(root.dataset.r440Ready==='yes')return;
    const slot=root.querySelector('[data-r440-export]'),status=root.querySelector('[data-r440-status]');
    if(!slot||!status)return;
    const b=document.createElement('button');b.type='button';b.textContent='Download original classroom exercise (.txt)';
    b.addEventListener('click',()=>{
      const url=URL.createObjectURL(new Blob([text()],{type:'text/plain;charset=utf-8'}));
      const a=document.createElement('a');a.href=url;a.download='fv-apollo-1-original-classroom-activity.txt';a.hidden=true;
      root.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),3000);
      status.textContent='Classroom text file prepared for local download. Nothing was submitted or saved by this page.';
    });
    slot.append(b);root.dataset.r440Ready='yes';
  }
  const start=()=>document.querySelectorAll('[data-r440-root]').forEach(init);
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
