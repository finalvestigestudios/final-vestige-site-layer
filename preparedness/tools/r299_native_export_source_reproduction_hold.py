#!/usr/bin/env python3
"""R299: independently re-render Preparedness WP draft bytes using a pinned native builder.

Review-only; reads local source and draft exports. NEVER publishes, writes CMS,
changes article content, approves medical/food/water advice or grants QD.
Pins builder, source-register variants, article custody, six tools, and inlined JS.
An exact export match proves mechanical correspondence ONLY, not claim truth.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re

SITE='https://finalvestige.com'
ROOT='preparedness/'
CUSTODY='preparedness/audits/r200_seven_cluster_35_article_frozen_custody.json'
PINS={
 CUSTODY:'5822f9dfde21d1f3bdfc26658769d852c639438c',
 'preparedness/tools/build.py':'349173d1e1d735eade218d95c7a0a2649c8cccd9',
 'preparedness/taxonomy.json':'15c547bb3018ac182b12a51036389cfa39a59168',
 'preparedness/sources/register.json':'b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77',
 'preparedness/sources/crosswalk.json':'d62e493a67dedd23e04cfdf3cce762ef933c6bf9',
 'preparedness/sources/fragments/food.json':'a1f73c8170932d6b3192e9cd506686d516d23d30',
 'preparedness/sources/fragments/health.json':'cc29c439372b9d49debf78e63020ffe4d62baeb8',
 'preparedness/sources/fragments/hist-field.json':'3dafa9425f3829c0be2e6fea00889aff95124031',
 'preparedness/sources/fragments/hist-food.json':'d10628342fea5f177a8d1be00dd906d0c9c7850e',
 'preparedness/sources/fragments/hist-home.json':'8d85fd868508c5caba14a839d119d55f31f14f72',
 'preparedness/sources/fragments/shelter.json':'2a3f1a7ddeab2782add875be1e0e378513504aa1',
 'preparedness/sources/fragments/start.json':'96140d6d1872588e5d20d9052445c9157e88934d',
 'preparedness/content/tools/water-planner.body.html':'a738d1f7824437911064d425868ed3d709326027',
 'preparedness/content/tools/water-planner.meta.json':'7ea188a06b614940a226328c0166c2a2b20ff84e',
 'preparedness/content/tools/home-fire-escape-worksheet.body.html':'01161948b6de6ffbd1b053c9b83a420758e707e4',
 'preparedness/content/tools/home-fire-escape-worksheet.meta.json':'397c7d3072fb237b490a5a316c93fc863c101be9',
 'preparedness/content/tools/power-outage-planner.body.html':'aa8f866aaaaab9253f41c4363d31919029c69234',
 'preparedness/content/tools/power-outage-planner.meta.json':'8796bba2b323cce096639997002c402bd853e50f',
 'preparedness/content/tools/family-reunification-card.body.html':'be8698ac5d020476ff649d85813810e2000c6f98',
 'preparedness/content/tools/family-reunification-card.meta.json':'47da1e7e20e39f0ea85e26d54a8d58301f6e0a15',
 'preparedness/content/tools/reunification-plan.body.html':'3305578369183edb1d427c8f8f8002eaacee420f',
 'preparedness/content/tools/reunification-plan.meta.json':'10cd57dc8d39e366aaef8fd76cc3f8969b8c5348',
 'preparedness/content/tools/kit-builder.body.html':'2cb531174d6828fa5185c47bd2b742a0befa8353',
 'preparedness/content/tools/kit-builder.meta.json':'e9be8a497df737b36d7d399fccc4a00000ce8eac',
 'preparedness/tools/water_planner.js':'9cd2944e7b5c5061ae041669c327069d488c2062',
 'preparedness/tools/shelter_common.js':'efe1c7910d99437e3687621dabab8ce55dc24fd4',
 'preparedness/tools/fire_worksheet.js':'7bfd283205c68ec1cbd9666cb63051c332ba23ac',
 'preparedness/tools/outage_items.js':'3bd519402202c40a49e9e1bde9fc9ba0f54d3fff',
 'preparedness/tools/reunion_card.js':'b1a09b1eda1ae26f081de65b400a37bc19538035',
 'preparedness/tools/plan_builder.js':'311aa78ec1abca6f7c1113f2620a459dad92748d',
 'preparedness/tools/plan_builder_ui.js':'2cc9a1196a6b433d861d91dafa6c5a85161990fb',
 'preparedness/tools/kit_planner.js':'3bf8ea8e64a7b8e70815f1c6d8ee8df15bf7822f',
 'preparedness/tools/kit_planner_ui.js':'d2ff08d8ba5585fe69b557a73db55de42aac9d92',
}
TOOL_SLUGS=frozenset(('water-planner','home-fire-escape-worksheet','power-outage-planner',
 'family-reunification-card','reunification-plan','kit-builder'))
TOKEN_CITE=re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')


def oid(data:bytes)->str:
 return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def sha256(data:bytes)->str:
 return hashlib.sha256(data).hexdigest()


def source_pin_errors(root:Path, pins:dict=PINS)->list[str]:
 """No symlinks, path substitution, missing files, or changed cited source records."""
 errors=[]
 for relative,expected in sorted(pins.items()):
  p=root/relative
  try:
   if not p.is_file() or p.is_symlink() or oid(p.read_bytes())!=expected:
    errors.append('PIN_MISSING_OR_CHANGED:'+relative)
  except (OSError,ValueError):
   errors.append('PIN_UNREADABLE:'+relative)
 fragment_dir=root/'preparedness/sources/fragments'
 if fragment_dir.is_dir():
  actual={f.relative_to(root).as_posix() for f in fragment_dir.iterdir() if f.is_file()}
  expected={p for p in pins if p.startswith('preparedness/sources/fragments/')}
  if actual!=expected:errors.append('SOURCE_FRAGMENT_INVENTORY_DRIFT')
 return errors


def is_unique_routes(report:dict, slugs:set[str], lib)->list[str]:
 """Report must match canonical destinations exactly, without URL duplication."""
 errors=[]
 rows=report.get('articles')
 if not isinstance(rows,list) or len(rows)!=41 or any(not isinstance(x,dict) for x in rows):
  return ['BUILD_REPORT_41_ENTRY_INVENTORY_INVALID']
 seen=[]
 for row in rows:
  s=row.get('slug')
  seen.append(s)
  if not isinstance(s,str) or s not in slugs or s not in lib.articles:errors.append('UNEXPECTED_REPORT_SLUG:'+str(s));continue
  if row.get('canonical')!=SITE+lib.url_path(s):errors.append('CANONICAL_DRIFT:'+s)
 if len(set(seen))!=41 or set(seen)!=slugs:errors.append('DUPLICATE_OR_MISSING_BUILD_SLUG')
 if len({x.get('canonical') for x in rows})!=41:errors.append('DUPLICATE_CANONICAL_URL')
 return errors


def audit_snapshot(custody:dict, report:dict, lib, builder,
                   drafts:dict[str,bytes], raw_article_blobs:dict[str,bytes])->dict:
 """Pure 41-entry audit. Builder is injected to permit adversarial synthetic tests.

 A successful mechanical comparison NEVER upgrades release approvals. Metadata and
 source registry are separately pinned at CLI entry; R200 article divergences
 are recorded for adjudication, NOT silently rewritten as old manuscripts.
 """
 errors=[];reproduced=[];citations=0;lineage=[]
 arts=custody.get('articles',[])
 if (custody.get('state')!='DRAFT_HARD_HOLD' or
     custody.get('artifact_count')!=35 or
     custody.get('export_target_count_with_six_tools')!=41 or
     len(arts)!=35 or
     any(custody.get(k) is not False for k in ('publication_authorized','independent_qd_pass','human_source_approved','medical_safety_verified'))):
  errors.append('R200_CUSTODY_INCOMPLETE_OR_RELEASE_STATE_CHANGED')
 if len(arts)!=35 or len({a.get('slug') for a in arts if isinstance(a,dict)})!=35:
  errors.append('R200_CUSTODY_SLUGS_INVALID')
 original_slugs={a.get('slug') for a in arts if isinstance(a,dict)}
 all_slugs=original_slugs|TOOL_SLUGS
 if len(all_slugs)!=41 or set(lib.articles)!=all_slugs:
  errors.append('LIBRARY_35_PLUS_6_INVENTORY_DRIFT')
 errors.extend(is_unique_routes(report,all_slugs,lib))
 ev=report.get('release_evidence',{})
 if not isinstance(ev,dict) or ev.get('independent_qa_verified') is not False or ev.get('wordpress_publication_performed') is not False or ev.get('state') not in ('HOLD','REQUIRES_INDEPENDENT_QA'):
  errors.append('REPORT_RELEASE_STATE_UNSAFE')
 rows=report.get('articles',[])
 by_slug={x.get('slug'):x for x in rows if isinstance(x,dict)}
 for a in arts:
  if not isinstance(a,dict):continue
  s=a.get('slug')
  if not isinstance(s,str) or s not in lib.articles:continue
  raw=raw_article_blobs.get(s)
  if not isinstance(raw,bytes):errors.append('R200_ARTICLE_SOURCE_MISSING:'+s);continue
  current=oid(raw)
  if current!=a.get('body_oid'):
   lineage.append({'slug':s,'r200_body_oid':a.get('body_oid'),'current_body_oid':current,'status':'UNADJUDICATED_LINEAGE_DRIFT'})
  if a.get('route')!='/preparedness/'+str(lib.articles[s].get('section'))+'/'+s+'/':
   errors.append('R200_ROUTE_MISMATCH:'+s)
 for slug in sorted(all_slugs):
  if slug not in lib.articles:continue
  meta=lib.articles[slug]
  if meta.get('status',{}).get('publish')!='draft':
   errors.append('NOT_DRAFT_STATUS:'+slug)
  path=f'preparedness/build/wp/{slug}.html'
  actual=drafts.get(path)
  if not isinstance(actual,bytes):errors.append('DRAFT_MISSING:'+slug);continue
  try:
   built=builder.build_article(lib,slug)
   rendered=builder.wp_wrap(lib,built['inner']).encode('utf-8')
  except (ValueError,KeyError,TypeError,UnicodeError) as exc:
   errors.append('NATIVE_RENDER_FAILED:'+slug+':'+type(exc).__name__);continue
  row=by_slug.get(slug)
  if row is None:errors.append('REPORT_ENTRY_MISSING:'+slug);continue
  # Source-ID order/meaning is reconstituted through the pinned native
  # source_for(article-origin) and sources_block implementation, not string counts.
  if (row.get('sources')!=built['sources'] or row.get('canonical')!=built['canonical'] or
      row.get('words')!=built['words'] or row.get('minutes')!=built['minutes']):
   errors.append('REPORT_CITATION_OR_METADATA_DRIFT:'+slug)
  # Byte-for-byte equivalence covers every ordered paragraph, HTML link label,
  # numbered citation/anchor, URL, source-scope disclosure, and entire review text.
  # Unlike R298's unordered windows, this allows zero deletion/reordering.
  if actual!=rendered:
   errors.append('EXPORTED_BYTES_NOT_NATIVE:'+slug)
  else:
   reproduced.append({'slug':slug,'word_count':built['words'],
                      'source_ids':list(built['sources']),'export_sha256':sha256(actual)})
  origtext=meta.get('_body','')
  if not isinstance(origtext,str):errors.append('SOURCE_BODY_INVALID:'+slug);continue
  source_occurrences=TOKEN_CITE.findall(origtext)
  if set(source_occurrences)!=set(built['sources']) or list(dict.fromkeys(source_occurrences))!=list(built['sources']):
   errors.append('CITATION_SOURCE_ORDER_MISMATCH:'+slug)
  citations+=len(source_occurrences)
 return {'schema':'fv-preparedness-r299-pinned-native-export-citation-v1',
         'state':'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
         'errors':sorted(set(errors)),
         'native_export_byte_matches':len(reproduced),
         'source_citation_occurrences':citations,
         'per_draft_evidence':reproduced,
         'r200_lineage_differences':lineage,
         'lineage_human_adjudicated':False,
         'all_41_exports_independently_approved':False,
         'publication_authorized':False,'independent_qd_pass':False,
         'medical_safety_verified':False,'privacy_verified':False,
         'merchant_approved':False,'confirmed_paid_orders':None,
         'net_revenue_per_1000_qualified_sessions':None}


def run(root:Path)->dict:
 errors=source_pin_errors(root)
 if errors:return {'schema':'fv-preparedness-r299-pinned-native-export-citation-v1',
                   'state':'INVALID_HARD_HOLD','errors':errors,'publication_authorized':False,
                   'independent_qd_pass':False,'medical_safety_verified':False,
                   'all_41_exports_independently_approved':False}
 source_path=root/'preparedness/tools/build.py'
 spec=importlib.util.spec_from_file_location('fv_r299_pinned_native',source_path)
 if spec is None or spec.loader is None:raise RuntimeError('NATIVE_BUILDER_IMPORT_FAILED')
 build=importlib.util.module_from_spec(spec)
 spec.loader.exec_module(build)
 lib=build.Library(root/'preparedness')
 custody=json.loads((root/CUSTODY).read_bytes())
 report=json.loads((root/'preparedness/build/build-report.json').read_bytes())
 raw={a['slug']:(root/'preparedness/content/articles'/f"{a['slug']}.body.html").read_bytes()
      for a in custody['articles']}
 drafts={f'preparedness/build/wp/{slug}.html':(root/'preparedness/build/wp'/f'{slug}.html').read_bytes()
         for slug in lib.articles}
 return audit_snapshot(custody,report,lib,build,drafts,raw)


def main(argv=None)->int:
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2])
 args=ap.parse_args(argv)
 try: result=run(args.repo_root)
 except (OSError,ValueError,KeyError,TypeError,RuntimeError) as exc:
  result={'state':'INVALID_HARD_HOLD','errors':['AUTHENTIC_REPO_OR_BUILD_UNAVAILABLE:'+type(exc).__name__],
          'publication_authorized':False,'independent_qd_pass':False,'medical_safety_verified':False,
          'all_41_exports_independently_approved':False}
 print(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2))
 return 2 if result['state']=='DRAFT_HARD_HOLD' else 1

if __name__=='__main__':raise SystemExit(main())
