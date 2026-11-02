#!/usr/bin/env python3
"""Fail-closed Gutenberg save/readback against a DISPOSABLE local WordPress.

Distinct from the iframe preview renderer. No WordPress.com hosted parity,
real-user CWV, or full WCAG certification; no production CMS writes.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit

FIXTURE = 'experience2/home-flagship/qa/release-candidate/fixtures/proposed-production-block-pr604.html'
SITE = 'http://127.0.0.1:9400'
BLOCK_START = re.compile(r'<!--\s*wp:(?:html|group)(?:\s|-->)')


def sha256(data: str) -> str:
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def guard_origin(url: str) -> None:
    try:
        dest = urlsplit(url)
        allowed = (dest.scheme == 'http' and dest.hostname == '127.0.0.1' and
                   dest.port == 9400 and dest.username is None and dest.password is None and
                   dest.path.startswith('/wp-admin/'))
    except ValueError:
        allowed = False
    if not allowed:
        raise ValueError('LOCAL_WORDPRESS_ADMIN_ORIGIN_REQUIRED')


def validate_candidate(repo: Path, expected: str) -> str:
    if len(expected) != 40 or not re.fullmatch('[0-9a-f]{40}', expected):
        raise ValueError('EXACT_COMMIT_SHA_REQUIRED')
    checkout = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
    if checkout != expected:
        raise ValueError('EXACT_COMMIT_NOT_CHECKED_OUT')
    file = repo / FIXTURE
    if not file.is_file() or file.is_symlink():
        raise ValueError('CANDIDATE_FILE_NOT_REGULAR')
    committed = subprocess.check_output(['git', '-C', str(repo), 'show', expected + ':' + FIXTURE])
    raw = file.read_bytes()
    if raw != committed:
        raise ValueError('CANDIDATE_NOT_COMMITTED_EXACT_HEAD')
    value = raw.decode('utf-8')
    if (not value.startswith('<!-- wp:html -->') or
            not value.rstrip().endswith('<!-- /wp:html -->') or
            len(BLOCK_START.findall(value)) != 1 or
            value.count('data-fv-home-flagship') < 1 or
            '<style>' not in value or '<script>' not in value):
        raise ValueError('CANDIDATE_BLOCK_CONTRACT_INVALID')
    return value


def six_block_probe(candidate: str) -> tuple[str, tuple[str, ...]]:
    """Synthetic, public-data-free protected Gutenberg blocks around candidate."""
    others = (
        '<!-- wp:html -->\n<div data-fv-probe="margins">Preserve archival index</div>\n<!-- /wp:html -->',
        '<!-- wp:html -->\n<div data-fv-probe="focus"><a href="/focus/">Focus Fieldbook</a></div>\n<!-- /wp:html -->',
        '<!-- wp:group -->\n<div class="wp-block-group" data-fv-probe="jetpack"><!-- wp:jetpack/subscriptions /--></div>\n<!-- /wp:group -->',
        '<!-- wp:html -->\n<div data-fv-probe="record">Enter the record</div>\n<!-- /wp:html -->',
        '<!-- wp:html -->\n<div data-fv-probe="identity">Final Vestige</div>\n<!-- /wp:html -->',
    )
    return ''.join((others[0], candidate, *others[1:])), others


def check_saved_raw(actual: str, candidate: str, others: tuple[str, ...]) -> None:
    expected, _ = six_block_probe(candidate)
    if actual != expected:
        raise ValueError('WORDPRESS_GUTENBERG_SAVE_CHANGED_BYTES')
    if actual.count('<!-- wp:html -->') != 5 or actual.count('<!-- wp:group -->') != 1:
        raise ValueError('WORDPRESS_GUTENBERG_BLOCK_STRUCTURE_CHANGED')
    if any(actual.count(block) != 1 for block in others):
        raise ValueError('WORDPRESS_PROTECTED_BLOCK_CHANGED')


def run(page, repo: Path, expected_sha: str, out: Path) -> dict:
    """Use only the authenticated local editor Playwright page from CI."""
    guard_origin(SITE + '/wp-admin/post-new.php?post_type=page')
    candidate = validate_candidate(repo, expected_sha)
    probe, others = six_block_probe(candidate)
    check_saved_raw(probe, candidate, others)
    notes = {
        'environment': 'EPHEMERAL_LOCAL_WORDPRESS_ONLY',
        'exact_source_sha': expected_sha,
        'candidate_sha256': sha256(candidate),
        'candidate_bytes': len(candidate.encode('utf-8')),
        'persisted_gutenberg_bytes_exact': False,
        'authored_inline_script_present_in_frontend': False,
        'frontend_flagship_dom_visible': False,
        'wordpress_com_hosted_parity': 'NOT_ESTABLISHED',
        'production_writes': False,
        'status': 'HOLD_NOT_RELEASE',
    }
    page_id = None
    created = False
    try:
        page.goto(SITE + '/wp-admin/post-new.php?post_type=page',
                  wait_until='domcontentloaded', timeout=40000)
        guard_origin(page.url)
        page.wait_for_function('Boolean(window.wp && window.wp.apiFetch)', timeout=30000)
        result = page.evaluate("""async ({content}) => {
          const created = await wp.apiFetch({path:'/wp/v2/pages', method:'POST',
            data:{title:'Isolated FV Gutenberg admission — delete after QA',
                  status:'draft', content}});
          return {id:created.id, status:created.status};
        }""", {'content': probe})
        if not isinstance(result, dict) or type(result.get('id')) is not int or result.get('status') != 'draft':
            raise ValueError('LOCAL_WORDPRESS_DRAFT_CREATE_NOT_CONFIRMED')
        page_id = result['id']
        created = True
        persisted = page.evaluate("""async ({id}) => {
          const p = await wp.apiFetch({path:'/wp/v2/pages/'+id+'?context=edit'});
          return {id:p.id,status:p.status,content:p.content && p.content.raw};
        }""", {'id': page_id})
        if persisted.get('id') != page_id or persisted.get('status') != 'draft':
            raise ValueError('WORDPRESS_GUTENBERG_READBACK_STATUS_CHANGED')
        check_saved_raw(persisted.get('content'), candidate, others)
        notes['persisted_gutenberg_bytes_exact'] = True
        # This URL is generated from a fresh draft on the same localhost only.
        page.goto(SITE + '/?page_id=' + str(page_id) + '&preview=true',
                  wait_until='domcontentloaded', timeout=45000)
        if not page.locator('[data-fv-home-flagship]').count():
            raise ValueError('SAVED_GUTENBERG_FRONTEND_FLAGSHIP_NOT_RENDERED')
        notes['frontend_flagship_dom_visible'] = True
        page.wait_for_function("""() => {
          const list = document.querySelector('[data-fv-case-buttons]');
          return list && !list.hidden;
        }""", timeout=18000)
        notes['authored_inline_script_present_in_frontend'] = True
        out.mkdir(parents=True, exist_ok=True)
        page.set_viewport_size({'width': 390, 'height': 844})
        page.screenshot(path=str(out / 'GUTENBERG_SAVED_FIRST_SCREEN_390.png'))
        page.set_viewport_size({'width': 1440, 'height': 900})
        page.screenshot(path=str(out / 'GUTENBERG_SAVED_FIRST_SCREEN_1440.png'))
        notes['saved_frontend_screenshots'] = ['390', '1440']
        if not all(notes[k] for k in ('persisted_gutenberg_bytes_exact',
                    'frontend_flagship_dom_visible', 'authored_inline_script_present_in_frontend')):
            raise ValueError('LOCAL_WORDPRESS_PERSISTENCE_HOLD')
        notes['status'] = 'ISOLATED_GUTENBERG_PERSISTENCE_PASS_NOT_HOSTED_RELEASE'
        return notes
    finally:
        # Destroy test draft. The entire local WordPress process is ephemeral too.
        if created:
            page.goto(SITE + '/wp-admin/post-new.php?post_type=page',
                      wait_until='domcontentloaded', timeout=40000)
            guard_origin(page.url)
            page.wait_for_function('Boolean(window.wp && window.wp.apiFetch)', timeout=30000)
            deleted = page.evaluate("""async ({id}) => {
              const result = await wp.apiFetch({path:'/wp/v2/pages/'+id+'?force=true',method:'DELETE'});
              return Boolean(result && result.deleted === true &&
                             result.previous && result.previous.id === id);
            }""", {'id': page_id})
            if deleted is not True:
                raise ValueError('LOCAL_WORDPRESS_TEST_DRAFT_CLEANUP_FAILED')
        out.mkdir(parents=True, exist_ok=True)
        (out / 'GUTENBERG_SAVED_BLOCK_ADMISSION.json').write_text(
            json.dumps(notes, indent=2, sort_keys=True) + '\n', encoding='utf-8')
