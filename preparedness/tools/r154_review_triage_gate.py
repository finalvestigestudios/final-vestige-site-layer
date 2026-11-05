#!/usr/bin/env python3
"""R154 read-only reviewer triage overlay for frozen R153 source-review evidence.

This is a review aid, NEVER a link check, approval, merge or safety certification.
On both successful HOLD and validation error, CLI exits 2; nothing is published.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import ipaddress
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

R153_PATH = 'preparedness/tools/r153_review_packet_gate.py'
R153_BLOB = 'ba0d460f7d43df5cb9f7641694bfa8b223f1352f'
SCHEMA = 'fv-preparedness-r154-triage-v1'
NOTES_SCHEMA = 'fv-preparedness-r154-notes-v1'
SHA256 = re.compile(r'^[a-f0-9]{64}$')
UNSAFE_TEXT = re.compile(r'[<>\x00-\x08\x0b\x0c\x0e-\x1f]')
DISPOSITIONS = {'QUESTION', 'NEEDS_MORE_EVIDENCE', 'PROPOSED_CORRECTION'}
EXPECTED_TOOL_ROWS = {'family-reunification-card': 11, 'home-fire-escape-worksheet': 7,
                      'kit-builder': 22, 'power-outage-planner': 17,
                      'reunification-plan': 7, 'water-planner': 3}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def safe_evidence_url(url: str) -> bool:
    if not isinstance(url, str) or len(url) > 2048 or any(ord(c) < 32 for c in url):
        return False
    try:
        u = urlsplit(url)
        if u.scheme != 'https' or not u.hostname or u.username or u.password or u.port not in (None, 443):
            return False
        h = u.hostname.rstrip('.').lower()
        if h == 'localhost' or h.endswith('.local') or h.endswith('.localhost'):
            return False
        try:
            return ipaddress.ip_address(h).is_global
        except ValueError:
            return '.' in h and not h.startswith('.') and not h.endswith('.')
    except ValueError:
        return False


def validated_packet(packet: dict):
    require(type(packet) is dict and packet.get('schema') == 'fv-preparedness-r153-review-interlock-v1',
            'invalid R153 packet schema')
    require(packet.get('decision') == 'DRAFT_HARD_HOLD' and packet.get('release_authorized') is False
            and packet.get('qualified_source_review') is False
            and packet.get('medical_safety_approved') is False
            and packet.get('independent_qd_pass') is False
            and packet.get('genuine_paid_preparedness_sku_verified') is False,
            'prior evidence asserts unauthorized release, sale or review')
    require(packet.get('review_tasks_total') == 75 and packet.get('tool_source_relationships') == 67
            and packet.get('tool_citation_occurrences') == 173
            and packet.get('tool_unresolved') == 58
            and packet.get('source_interpretation_changes') == 4
            and packet.get('historical_food_substitutions') == 8,
            'historical evidence counts changed')
    tools, history = packet.get('tool_review_tasks'), packet.get('historic_food_review_tasks')
    require(type(tools) is list and len(tools) == 67 and type(history) is list and len(history) == 8,
            'review task inventory changed')
    require(SHA256.fullmatch(str(packet.get('packet_fingerprint'))) is not None,
            'missing R153 packet fingerprint')
    counts, keys, fps, source_uses = {}, set(), set(), 0
    for item in tools + history:
        require(type(item) is dict and item.get('review') == 'PENDING'
                and item.get('qualified_reviewer') is None,
                'review task claims qualification')
        f = item.get('review_fingerprint')
        require(type(f) is str and SHA256.fullmatch(f) is not None and f not in fps,
                'duplicate or missing task fingerprint')
        fps.add(f)
        if item.get('type') == 'tool_source_scope':
            tool, sid, count = item.get('tool'), item.get('source_id'), item.get('citations')
            require(tool in EXPECTED_TOOL_ROWS and isinstance(sid, str) and sid.strip(),
                    'unknown tool/source relationship')
            require(type(count) is int and count > 0, 'invalid citation count')
            require(isinstance(item.get('url'), str) and item['url'].startswith('https://')
                    and all(isinstance(item.get(x), str) and item[x].strip() for x in
                            ('publisher', 'supports', 'author_specific_use')),
                    'lost original citation provenance')
            require(type(item.get('currently_resolvable')) is bool
                    and type(item.get('interpretation_changed_by_shadow_origin')) is bool,
                    'invalid source resolution evidence')
            key = ('tool', tool, sid)
            counts[tool] = counts.get(tool, 0) + 1
            source_uses += count
        else:
            require(item.get('type') == 'historic_food_citation', 'unknown review task type')
            require(item.get('article') in ('pemmican-and-dried-meats', 'pioneer-travel-rations')
                    and type(item.get('occurrence')) is int and item['occurrence'] > 0
                    and type(item.get('line')) is int and item['line'] > 0
                    and isinstance(item.get('excerpt'), str) and item['excerpt'].strip(),
                    'missing Historical Food citation context')
            key = ('historical', item['article'], item['occurrence'])
        require(key not in keys, 'duplicate task identity')
        keys.add(key)
    require(counts == EXPECTED_TOOL_ROWS and source_uses == 173, 'tool source-use inventory drift')
    require(sum(not a['currently_resolvable'] for a in tools) == 58,
            '58 unresolved relationships were not preserved')
    require(sum(a['interpretation_changed_by_shadow_origin'] for a in tools) == 4,
            'four changed source interpretations were lost')
    require(sum(a['article'] == 'pemmican-and-dried-meats' for a in history) == 7
            and sum(a['article'] == 'pioneer-travel-rations' for a in history) == 1,
            'Historical Food review occurrence loss')
    return tools, history


def validate_notes(notes: dict | None, packet: dict, known: set[str]) -> dict[str, dict]:
    if notes is None:
        return {}
    require(type(notes) is dict and set(notes) == {'schema', 'base_packet_fingerprint', 'notes'}
            and notes['schema'] == NOTES_SCHEMA
            and notes['base_packet_fingerprint'] == packet['packet_fingerprint'],
            'review note overlay schema or source fingerprint mismatch')
    items = notes['notes']
    require(type(items) is list and len(items) <= 75, 'note list invalid or too large')
    result = {}
    for row in items:
        require(type(row) is dict and set(row) == {'task_fingerprint', 'disposition', 'note', 'evidence_urls'},
                'unrecognized fields, including approval claims, in reviewer note')
        f, disposition, note, urls = (row[k] for k in ('task_fingerprint','disposition','note','evidence_urls'))
        require(isinstance(f, str) and f in known and f not in result,
                'unknown, replayed or duplicated task note')
        require(disposition in DISPOSITIONS,
                'notes cannot grant source, safety, QD or publication approval')
        require(type(note) is str and 12 <= len(note.strip()) <= 1200
                and not UNSAFE_TEXT.search(note), 'missing, overlong or active-content note')
        require(type(urls) is list and len(urls) <= 5 and len(set(urls)) == len(urls)
                and all(safe_evidence_url(u) for u in urls), 'unsafe or duplicate evidence URL')
        result[f] = row.copy()
    return result


def triage(packet: dict, notes: dict | None = None) -> dict:
    tools, history = validated_packet(packet)
    tasks = tools + history
    annotations = validate_notes(notes, packet, {t['review_fingerprint'] for t in tasks})
    rows = []
    for t in tasks:
        historical = t['type'] == 'historic_food_citation'
        family = t.get('tool') == 'family-reunification-card'
        shadow = t.get('interpretation_changed_by_shadow_origin') is True
        priority = 0 if historical else 1 if family else 2 if shadow else 3
        category = ('HISTORICAL_FOOD_SOURCE_AND_FOOD_SAFETY' if historical else
                    'FAMILY_REUNIFICATION_SOURCE_AND_PRIVACY' if family else
                    'SOURCE_INTERPRETATION_CHANGE' if shadow else 'TOOL_SOURCE_SCOPE')
        key = t['review_fingerprint']
        record = annotations.get(key)
        rows.append({'task_fingerprint': key, 'original_type': t['type'],
                     'original_identity': (t['article'] + '#' + str(t['occurrence'])) if historical
                     else (t['tool'] + '/' + t['source_id']),
                     'priority': priority, 'review_lane': category,
                     'source_url': None if historical else t['url'],
                     'source_interpretation_changed': shadow,
                     'note_status': 'NO_NOTE' if record is None else record['disposition'],
                     'reviewer_note': None if record is None else record['note'],
                     'evidence_urls_unverified': [] if record is None else record['evidence_urls'],
                     'qualified_source_review': False, 'medical_or_food_safety_approved': False,
                     'publication_allowed': False})
    rows.sort(key=lambda r: (r['priority'], r['original_identity'], r['task_fingerprint']))
    return {'schema': SCHEMA, 'decision': 'DRAFT_HARD_HOLD',
            'independent_qd_pass': False, 'qualified_source_review': False,
            'safety_approved': False, 'publication_authorized': False,
            'merchant_offer_verified': False, 'original_packet_fingerprint': packet['packet_fingerprint'],
            'notes_count': len(annotations), 'review_tasks_total': len(rows),
            'priority_hist_food': sum(r['priority'] == 0 for r in rows),
            'priority_reunification': sum(r['priority'] == 1 for r in rows),
            'priority_interpretation': sum(r['priority'] == 2 for r in rows),
            'remaining_tool_source': sum(r['priority'] == 3 for r in rows),
            'tasks': rows}


def authentic_packet(repo: Path) -> dict:
    source = repo / R153_PATH
    require(source.is_file() and not source.is_symlink()
            and git_blob(source.read_bytes()) == R153_BLOB,
            'R153 frozen gate Git blob missing or modified')
    spec = importlib.util.spec_from_file_location('r153_pinned', source)
    require(spec is not None and spec.loader is not None, 'cannot load R153 validator')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.real_packet(repo)  # R153/R152 perform exact Git source custody checks.


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, default=Path('.'))
    p.add_argument('--notes', type=Path, help='optional reviewer questions/proposed corrections (no approvals)')
    p.add_argument('--report', type=Path, help='new external JSON path, never inside the repo')
    a = p.parse_args(argv)
    try:
        root = a.repo.resolve()
        if a.notes:
            require(a.notes.is_file() and not a.notes.is_symlink(), 'missing reviewer notes')
            notes = json.loads(a.notes.read_text(encoding='utf-8'))
        else:
            notes = None
        result = triage(authentic_packet(root), notes)
        if a.report:
            path = a.report.resolve()
            require(not path.is_relative_to(root) and not path.exists(),
                    'report must be a new file outside the checkout')
            path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'decision': 'DRAFT_HARD_HOLD', 'tasks': 75,
                          'notes_count': result['notes_count'], 'qualified_source_review': False,
                          'independent_qd_pass': False}))
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError, UnicodeError) as exc:
        print(json.dumps({'decision': 'INVALID_HARD_HOLD', 'error': str(exc)}))
    return 2

if __name__ == '__main__':
    raise SystemExit(main())
