"""Apollo 204 source-paths: a documentary join, never an asserted causal linkage.

The six routes derive only from the versioned 1967 Board/1968 NASA response
crosswalk and the preexisting source-custody ledger. No map geometry, image
assets, auto-generated claims or outside Javascript dependencies.
"""
from html import escape
from urllib.parse import urlparse

BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
RESPONSE = 'https://www.nasa.gov/missions/apollo/apollo-1/nasa-response-to-findings/'

def esc(value):
    return escape(str(value), quote=True)

def validate(response, custody):
    routes = response['records']
    claims = custody['claims']
    if [r['id'] for r in routes] != [f'{i:02}' for i in range(1, 7)]:
        raise ValueError('Expected six ordered, distinct response records')
    if [c['stage_id'] for c in claims] != [f'{i:02}' for i in range(1, 7)]:
        raise ValueError('Source custody stages are not canonical')
    by_stage = {c['stage_id']: c for c in claims}
    for r in routes:
        if r['related_stage'] not in by_stage or r['kind'] not in {'hardware', 'procedures'}:
            raise ValueError('Unreviewed stage reference or response category')
        if r['primary'] != BOARD or r['later'] != RESPONSE:
            raise ValueError('Unreviewed external source endpoint')
        for key in ('board_locator','response_locator','board_summary','response_summary','status','title'):
            if not isinstance(r[key], str) or not r[key].strip():
                raise ValueError(f'Missing reviewed source field: {key}')
    return by_stage

def route(r, claim):
    rid, stage = esc(r['id']), esc(claim['stage_id'])
    return f'''<li class="ex2-trail__card" id="trail-{rid}" tabindex="-1" data-ex2-trail-card data-ex2-trail-kind="{esc(r['kind'])}">
    <article aria-labelledby="trail-title-{rid}">
      <header class="ex2-trail__card-head"><p>DOCUMENTARY ROUTE <b>{rid} / 06</b></p><span>{esc(r['kind']).upper()}</span></header>
      <h3 id="trail-title-{rid}">{esc(r['title'])}</h3>
      <ol class="ex2-trail__steps" aria-label="Three distinct evidence stages">
        <li><div><span class="ex2-trail__step">01</span><p>1967 / REVIEW BOARD</p></div><h4>What the investigators addressed</h4><p>{esc(r['board_summary'])}</p><small>{esc(r['board_locator'])}</small></li>
        <li><div><span class="ex2-trail__step">02</span><p>1968 / NASA RESPONSE ACCOUNT</p></div><h4>What NASA subsequently described</h4><p>{esc(r['response_summary'])}</p><small>{esc(r['response_locator'])}</small></li>
        <li class="ex2-trail__limit"><div><span class="ex2-trail__step">03</span><p>EVIDENCE LIMIT / STILL OPEN</p></div><h4>What this trail does not establish</h4><p>{esc(r['status'])}</p></li>
      </ol>
      <details class="ex2-trail__method"><summary>Inspect the related source custody and limits</summary>
        <div><p>The related claim in the existing Research Desk is <strong>{esc(claim['heading'])}</strong>. It was classified as <em>{esc(claim['certainty'])}</em>. The link is thematic, not proof that a later recommendation corrected this individual claim.</p>
        <p><strong>Original claim:</strong> {esc(claim['claim'])}</p><p><strong>Evidence boundary:</strong> {esc(claim['boundary'])}</p>
        <p><strong>Board report reference:</strong> {esc(claim['board_locator'])}</p></div>
      </details>
      <nav aria-label="Documentary sources for route {rid}" class="ex2-trail__actions"><a href="#custody-{stage}">Related custody claim {stage}</a>
        <a href="{BOARD}" target="_blank" rel="noopener noreferrer">Read Board report <span aria-hidden="true">↗</span><span class="ex2-sr-only"> (new tab)</span></a>
        <a href="{RESPONSE}" target="_blank" rel="noopener noreferrer">Read NASA response <span aria-hidden="true">↗</span><span class="ex2-sr-only"> (new tab)</span></a>
        <a href="#trail-{rid}">Permanent link</a></nav>
    </article></li>'''

def section(response, custody):
    by_stage = validate(response, custody)
    cards = '\n'.join(route(r, by_stage[r['related_stage']]) for r in response['records'])
    return f'''<section class="ex2-section ex2-trail" id="documentary-trails" aria-labelledby="trail-heading">
      <div class="ex2-section__intro"><p class="ex2-eyebrow">VI / DOCUMENTARY TRAILS · TWO DIFFERENT REPORTS</p>
        <h2 id="trail-heading">Follow the remedy. <em>Keep the uncertainty.</em></h2>
        <p>Choose a documentary route through a 1967 Review Board recommendation, the response NASA described in its 1968 report, and the important question that the surviving pair cannot settle. These links are thematic reading paths, not evidence that a proposed remedy was completed or that a photograph proves it.</p></div>
      <div class="ex2-trail__reader"><div class="ex2-trail__prompt"><b>THE READING RULE</b><p>Different source dates mean different claims. A Board recommendation is a proposed remedy; a later report describes contemporaneous progress. Neither source alone proves final hardware acceptance or long-term outcomes.</p></div>
      <div class="ex2-trail__controls" data-ex2-trail-controls hidden><label for="trail-select">Choose a documentary route</label>
        <select id="trail-select" data-ex2-trail-select><option value="all">All six source trails</option>
          {''.join(f'<option value="{esc(r["id"])}">{esc(r["id"])} · {esc(r["title"])}</option>' for r in response['records'])}</select>
        <button type="button" data-ex2-trail-reset>Show all trails</button><output data-ex2-trail-status role="status" aria-live="polite" aria-atomic="true">All six trails visible</output></div>
      <ol class="ex2-trail__grid">{cards}</ol><p class="ex2-trail__closing">Editorial evidence crosswalk, not an independent engineering certification. Source-only records; no NASA images, map pins, sponsor logos or implied NASA endorsement. All six routes remain readable when scripting is disabled.</p></div>
    </section>'''
