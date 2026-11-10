"""Fail-closed, synthetic-input verification of R267's offline Chromium reproduction.

This checks one browser/PDF capture for internal consistency. It NEVER confers
publication, medical, privacy, child-data, accessibility or independent QD PASS.
No internet, personal data, WordPress or merchant access is performed.
"""
from __future__ import annotations

import re

HOLD = 'DRAFT_HARD_HOLD'
WIDTHS = (320, 360, 390, 768, 1440)
ORIGINAL_WIDTHS = (680, 680, 680, 768, 1440)
REVIEW_WARNING = 'UNAPPROVED REVIEW CONCEPT. Do not distribute or enter real personal details.'
WARNINGS = (
    'Privacy: This card may be lost or photographed. Do not write child names, school details, home addresses, passwords, medical information or access codes.',
    'Privacy: A finder can read this card. Carry only non-sensitive contact details and review before sharing.',
)
FIELDS = (
    'Out-of-area contact:', 'Telephone:', 'Backup contact:',
    'Backup telephone:', 'Plan reviewed:',
)
FALSE_STATES = (
    'physical_print_cut_fold_approved', 'source_citations_approved',
    'privacy_approved', 'independent_qd_pass', 'public_published',
)

def _need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError('R268 HARD HOLD: ' + message)


def _near(actual, expected: float, tolerance: float = 0.8) -> bool:
    return type(actual) in (float, int) and abs(actual - expected) <= tolerance


def _normalize(s: str) -> str:
    _need(isinstance(s, str), 'PDF extracted text must be a string')
    return re.sub(r'\s+', ' ', s).strip()


def inspect(record: dict, texts: dict, pages: dict) -> dict:
    """Require exact viewport, warning/field, geometry, page and JS parity.

    texts and pages use keys original_js_0 ... preview_js_1.
    Source Git blobs are authenticated by the caller before browser capture.
    A passing result is a bounded reproduction only, always HARD HOLD.
    """
    _need(isinstance(record, dict), 'capture record missing')
    _need(record.get('state') == HOLD, 'record release state changed')
    for k in FALSE_STATES:
        _need(record.get(k) is False, 'approval false-state drift: ' + k)
    _need(isinstance(texts, dict) and isinstance(pages, dict), 'PDF evidence maps missing')
    _need(set(texts) == set(pages) == {
        f'{s}_js_{js}' for s in ('original', 'preview') for js in (0, 1)
    }, 'unexpected or missing PDF evidence')

    for name, expected in (('original', ORIGINAL_WIDTHS), ('preview', WIDTHS)):
        section = record.get(name)
        _need(isinstance(section, dict), name + ' capture absent')
        screen = section.get('screen')
        printed = section.get('print')
        _need(isinstance(screen, dict) and set(screen) == set(map(str, WIDTHS)),
              name + ' screen viewport coverage changed')
        _need(isinstance(printed, dict) and set(printed) == {'True', 'False'},
              name + ' JavaScript print coverage changed')
        for w, expected_width in zip(WIDTHS, expected):
            row = screen[str(w)]
            _need(isinstance(row, dict), 'screen record malformed')
            _need(type(row.get('document_css_px')) in (int, float)
                  and abs(row['document_css_px'] - expected_width) <= 1,
                  f'{name} screen width {w} drift')
            _need(row.get('front_and_back_visible') == [True, True],
                  f'{name} warning/face visibility at {w} invalid')
            _need(type(row.get('card_css_px')) in (int, float) and row['card_css_px'] > 0,
                  'card width missing')
        for js in (0, 1):
            dims = printed[str(bool(js))]
            _need(isinstance(dims, dict), 'print dimensions missing')
            _need(_near(dims.get('card_width'), 672), 'unfolded print width drift')
            _need(_near(dims.get('card_height'), 206, 2), 'unfolded print height drift')
            _need(isinstance(dims.get('face_widths'), list)
                  and len(dims['face_widths']) == 2
                  and all(_near(w, 335, 1.5) for w in dims['face_widths']),
                  'two print face widths drift')
            fonts = dims.get('privacy_font_px')
            _need(fonts == ['10.6667px', '10.6667px']
                  or (isinstance(fonts, list) and len(fonts) == 2
                      and all(isinstance(x, str) and x.endswith('px')
                              and _near(float(x[:-2]), 10.6667, .05) for x in fonts)),
                  'privacy notice font drift')
            key = f'{name}_js_{js}'
            _need(pages[key] == 1 and type(pages[key]) is int,
                  key + ' PDF must have exactly one page')
            content = _normalize(texts[key])
            _need(REVIEW_WARNING in content, key + ' PDF sheet-level review warning missing')
            for warning in WARNINGS:
                _need(warning in content, key + ' printed privacy text missing')
            for field in FIELDS:
                _need(field in content, key + ' printed contact field missing')

    for js in (0, 1):
        a = record['original']['print'][str(bool(js))]
        b = record['preview']['print'][str(bool(js))]
        _need({k:v for k,v in a.items() if k!='sha256'} ==
              {k:v for k,v in b.items() if k!='sha256'},
              f'original-preview printed geometry parity failed: JS={js}')
        _need(_normalize(texts[f'original_js_{js}']) ==
              _normalize(texts[f'preview_js_{js}']),
              f'original-preview text parity failed: JS={js}')
    for name in ('original', 'preview'):
        a = record[name]['print']['True']
        b = record[name]['print']['False']
        _need({k:v for k,v in a.items() if k!='sha256'} ==
              {k:v for k,v in b.items() if k!='sha256'},
              f'JavaScript on/off printed geometry changed: {name}')
        _need(_normalize(texts[f'{name}_js_1']) ==
              _normalize(texts[f'{name}_js_0']),
              f'JavaScript on/off printed text changed: {name}')
    return {
        'state': HOLD,
        'bounded_chromium_screen_print_consistency': 'OBSERVED_IN_TEST_ENVIRONMENT_ONLY',
        'five_viewports_and_two_js_modes': True,
        'both_faces_visible_in_tested_screen_samples': True,
        'two_printed_privacy_warnings_and_five_labels': True,
        'one_page_letter_pdf_in_all_four_samples': True,
        'original_preview_print_and_js_parity': True,
        'sheet_warning_present_but_detached_cutout_approval_unverified': True,
        'independent_qd_pass': False,
        'privacy_approved': False,
        'release_authorized': False,
        'public_published': False,
        'ready_for_wordpress': False,
    }
