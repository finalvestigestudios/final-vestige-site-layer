"""Independent, source-first Apollo 204 recommendation/response comparison; no remote dependencies."""
from html import escape
from pathlib import Path
from urllib.parse import urlparse
from io import StringIO
import csv, json
BOARD="https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/"
RESPONSE="https://www.nasa.gov/missions/apollo/apollo-1/nasa-response-to-findings/"
KEYS={'id','kind','title','board_locator','board_summary','response_locator','response_summary','status','related_stage','primary','later'}
EXPORT_FIELDS=('id','kind','title','board_locator','board_summary','response_locator','response_summary','status','related_stage','board_url','response_url','geometry','image_reuse')
def e(v): return escape(str(v),quote=True)
def validate(data):
    assert data['compiled']=='2026-10-30' and len(data['records'])==6
    assert [x['id'] for x in data['records']]==['01','02','03','04','05','06']
    assert {x['kind'] for x in data['records']}=={'hardware','procedures'}
    for x in data['records']:
        assert set(x)==KEYS and x['primary']==BOARD and x['later']==RESPONSE
        assert x['related_stage'] in {'01','02','03','04','05','06'}
        assert all(x[k] for k in ('title','board_locator','board_summary','response_locator','response_summary','status'))
def link(url,title):
    assert url in {BOARD,RESPONSE}
    return f'<a href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(title)} <span aria-hidden="true">↗</span><span class="ex2-sr-only"> (opens in new tab)</span></a>'
def card(x):
    i=e(x['id'])
    return f'''<li id="response-{i}" tabindex="-1" class="ex2-response__item" data-ex2-response-item data-ex2-response-kind="{e(x['kind'])}"><article aria-labelledby="response-title-{i}">
      <p class="ex2-response__index">RESPONSE {i} / 06 <span>{e(x['kind']).upper()}</span></p><h3 id="response-title-{i}">{e(x['title'])}</h3>
      <div class="ex2-response__pair"><section aria-label="1967 Review Board recommendation">
        <p class="ex2-response__period">1967 / THE REVIEW BOARD</p><h4>What investigators recommended</h4><p>{e(x['board_summary'])}</p><p class="ex2-response__locator">{e(x['board_locator'])}</p>{link(x['primary'],'Read the original Board report')}
      </section><section aria-label="Later NASA response report">
        <p class="ex2-response__period">1968 / SUBSEQUENT REPORT</p><h4>What NASA subsequently reported</h4><p>{e(x['response_summary'])}</p><p class="ex2-response__locator">{e(x['response_locator'])}</p>{link(x['later'],'Read the subsequent NASA report')}
      </section></div><p class="ex2-response__boundary"><b>Evidence limit:</b> {e(x['status'])}</p>
      <p class="ex2-response__actions"><a href="#custody-{e(x['related_stage'])}">Inspect related source custody {e(x['related_stage'])}</a> · <a href="#response-{i}" aria-label="Permalink to response record {i}">Link to this record</a></p>
      </article></li>'''
def section(data):
    validate(data)
    cards='\n'.join(card(x) for x in data['records'])
    return f'''<section class="ex2-section ex2-response" id="response-audit" aria-labelledby="response-heading">
      <div class="ex2-section__intro"><p class="ex2-eyebrow">V / AFTERMATH · DOCUMENTARY CROSSWALK</p><h2 id="response-heading">A recommendation is <em>not a completed repair.</em></h2>
      <p>Six specific recommendations from the 1967 Apollo 204 Review Board, paired with the historically bounded response that NASA later described. Do not mistake a plan, a rule or an account of progress for independent proof of completed changes.</p></div>
      <div class="ex2-response__note"><b>Read the documents in order.</b><p>The left column is the Board's 1967 finding or recommendation. The right column paraphrases a 1968 Senate report excerpt reproduced by NASA. Every pair includes original source links, exact section locators and a distinct evidence boundary. No images are reproduced.</p></div>
      <div class="ex2-response__tools" data-ex2-response-tools hidden><label for="response-filter">Inspect response type</label>
        <select id="response-filter" data-ex2-response-filter><option value="all">All six records</option><option value="hardware">Hardware and materials</option><option value="procedures">Procedures and oversight</option></select>
        <button type="button" data-ex2-response-reset>Show all six</button><output data-ex2-response-count role="status" aria-live="polite" aria-atomic="true">6 of 6 historical response records</output></div>
      <ol class="ex2-response__grid">{cards}</ol><p class="ex2-response__notice">The quoted-era NASA report does not establish which changes were eventually installed, tested or certified. The published historical response is not an endorsement of Final Vestige.</p>
      <div class="ex2-response__downloads"><a href="response-export.csv" download="apollo-response-crosswalk.csv" type="text/csv">Download six-record CSV</a><a href="response-export.json" download="apollo-response-crosswalk.json" type="application/json">Download JSON source data</a></div>
    </section>'''
def export_assets(data,root:Path):
    validate(data)
    rows=[{'id':x['id'],'kind':x['kind'],'title':x['title'],'board_locator':x['board_locator'],'board_summary':x['board_summary'],'response_locator':x['response_locator'],'response_summary':x['response_summary'],'status':x['status'],'related_stage':x['related_stage'],'board_url':BOARD,'response_url':RESPONSE,'geometry':'not_assigned','image_reuse':'source_links_only'} for x in data['records']]
    def safe(v):
        v=str(v)
        return "'"+v if v.lstrip().startswith(('=','+','-','@','\\t','\\r')) else v
    out=StringIO(newline='')
    writer=csv.DictWriter(out,fieldnames=EXPORT_FIELDS,lineterminator='\n');writer.writeheader()
    writer.writerows([{k:safe(v) for k,v in x.items()} for x in rows])
    (root/'response-export.csv').write_text(out.getvalue(),encoding='utf-8',newline='\n')
    (root/'response-export.json').write_text(json.dumps({'scope':'STAGING_HISTORICAL_ACCOUNT','compiled':'2026-10-30','no_nasa_images':True,'no_geolocations':True,'not_a_completed_remediation_audit':True,'rows':rows},indent=2,sort_keys=True,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
