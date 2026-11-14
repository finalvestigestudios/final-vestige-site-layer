/* Optional presentation filter. Without JavaScript the entire source list stays visible. */
(function(){
  'use strict';
  var choices = [['all','All records'],['findings','Board findings'],['chronology','Chronology'],['later','Later history'],['photos','Photographs']];
  function upgrade(root){
    if(root.dataset.fvApolloIndexReady==='1')return;
    var bar=root.querySelector('[data-fv-apollo-filters]');
    var status=root.querySelector('[data-fv-apollo-status]');
    if(!bar || !status || root.querySelectorAll('[data-fv-apollo-entry]').length!==13)return;
    var groups=Array.prototype.slice.call(root.querySelectorAll('[data-fv-apollo-group]'));
    if(groups.length!==4)return;
    root.dataset.fvApolloIndexReady='1';
    choices.forEach(function(choice){
      var button=document.createElement('button');button.type='button';button.textContent=choice[1];button.setAttribute('aria-pressed',choice[0]==='all'?'true':'false');
      button.addEventListener('click',function(){
        var count=0;
        groups.forEach(function(group){
          group.hidden=choice[0]!=='all' && group.dataset.fvApolloGroup!==choice[0];
          if(!group.hidden)count+=group.querySelectorAll('[data-fv-apollo-entry]').length;
        });
        Array.prototype.forEach.call(bar.querySelectorAll('button'),function(item){item.setAttribute('aria-pressed',item===button?'true':'false');});
        status.textContent='Showing '+count+' of 13 evidence entries.';
      });
      bar.appendChild(button);
    });
    bar.hidden=false;status.hidden=false;status.textContent='Showing all 13 evidence entries.';
  }
  function ready(){Array.prototype.forEach.call(document.querySelectorAll('[data-fv-apollo-source-index]'),upgrade);}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',ready);else ready();
}());
