/* Optional only: forms must be rendered by the existing Jetpack block; never clone, intercept, or submit data. */
(function(){
  'use strict';
  const dialog=document.getElementById('fv-focus-dialog');
  const open=document.querySelector('.fv-focus-invite__open');
  if(!dialog||!open||typeof dialog.showModal!=='function')return;
  const form=dialog.querySelector('form');
  const email=form && form.querySelector('input[type="email"]');
  if(!form||!email)return; // fail closed: leave ordinary /focus/ link visible
  const close=dialog.querySelector('.fv-focus-dialog__close');
  const fallback=document.querySelector('.fv-focus-invite__fallback');
  open.hidden=false;
  if(fallback)fallback.hidden=true;
  let returnFocus=null;
  open.addEventListener('click',()=>{
    returnFocus=document.activeElement;
    dialog.showModal();
    email.focus();
  });
  if(close)close.addEventListener('click',()=>dialog.close());
  dialog.addEventListener('click',(e)=>{
    const rect=dialog.getBoundingClientRect();
    if(e.clientX<rect.left||e.clientX>rect.right||e.clientY<rect.top||e.clientY>rect.bottom)dialog.close();
  });
  dialog.addEventListener('close',()=>{if(returnFocus&&returnFocus.isConnected)returnFocus.focus()});
  // Intentional: no timer, no exit-intent, no session tracking, no form listener, no forced subscribe.
})();
