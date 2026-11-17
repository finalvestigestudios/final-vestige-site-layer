'use strict';
/** Bounded full-document scrolling. Deterministic and read-only; no browser or network required. */
const STEP_PX=720, MAX_STEPS=120, MAX_HEIGHT_PX=80000;
const finite=n=>Number.isFinite(n)&&n>=0;
function nextScrollTarget({pageHeight,viewportHeight,scrollY,steps}){
 if(![pageHeight,viewportHeight,scrollY,steps].every(finite)||viewportHeight===0||!Number.isInteger(steps))return null;
 if(steps>=MAX_STEPS||pageHeight>MAX_HEIGHT_PX)return null;
 const bottom=Math.max(0,pageHeight-viewportHeight);
 if(scrollY>=bottom-1)return null;
 return Math.min(scrollY+STEP_PX,bottom);
}
function evaluateCoverage({pageHeight,viewportHeight,scrollY,steps,scanError=null}){
 const valid=[pageHeight,viewportHeight,scrollY,steps].every(finite)&&viewportHeight>0&&Number.isInteger(steps);
 if(!valid)return{complete:false,state:'invalid_scroll_observation',reason:'missing_or_invalid_browser_metrics'};
 if(scanError)return{complete:false,state:'scan_error',reason:String(scanError)};
 if(pageHeight>MAX_HEIGHT_PX)return{complete:false,state:'height_cap',reason:'document_taller_than_80000px'};
 const bottom=Math.max(0,pageHeight-viewportHeight);
 if(scrollY+2<bottom)return{complete:false,state:'incomplete_scan',reason:steps>=MAX_STEPS?'step_budget_exhausted':'bottom_not_reached'};
 return{complete:true,state:'full_height_scanned',reason:null};
}
module.exports={STEP_PX,MAX_STEPS,MAX_HEIGHT_PX,nextScrollTarget,evaluateCoverage};
