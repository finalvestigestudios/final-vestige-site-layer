"""Refuse release until authentic independently documented staging/CI/commerce preconditions."""
import json,sys
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]/'QA/release_gate_result.json'
REQUIRED=['installed_wordpress_and_assembler','independent_editorial_and_nasa_rights_review','axe_core_real_staging','navigated_lcp_cls_and_field_coverage','exact_head_green_ci','screen_reader_review','founder_release_approval']
result={'status':'HARD_HOLD','code':2,'required':{key:'MISSING' for key in REQUIRED},'sales_verified':False,'reason':'Offline PHP/Chromium fixture is not release acceptance; no installed staging or authorized commercial offer.'}
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps(result,sort_keys=True))
sys.exit(2)
