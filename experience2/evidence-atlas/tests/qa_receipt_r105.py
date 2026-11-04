#!/usr/bin/env python3
"""R105 crash-safe, non-secret evidence receipts for genuine WordPress browser QA.

An evidence journal, never authorization to publish. No historical claims,
hosted network calls, or WordPress content/settings writes.
"""
import hashlib
import json
import os
import re
from pathlib import Path

SCHEMA = 'fv.apollo.r105.partial-evidence.v1'
FILENAME = 'R105_QA_PROGRESS.json'
CHECKPOINT = re.compile(r'^[a-z0-9][a-z0-9:._=-]{0,99}$')


class EvidenceJournal:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / FILENAME

    def _write(self, payload):
        data = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + '\n'
        temp = self.path.with_suffix('.json.tmp')
        with temp.open('w', encoding='utf-8') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, self.path)

    def _read(self):
        if self.path.is_file():
            return json.loads(self.path.read_text(encoding='utf-8'))
        return {'schema': SCHEMA, 'release': 'STAGING_HOLD', 'status': 'not_started'}

    def checkpoint(self, record, stage):
        if not CHECKPOINT.fullmatch(stage):
            raise ValueError('R105_INVALID_STAGE')
        counts = {
            'browser_cases': len(record.get('r103_interaction_cases', [])),
            'axe_scans': len(record.get('axe', [])),
            'lab_samples': len(record.get('performance_lab_samples', [])),
            'screenshots': len(record.get('screenshots_sha256', {})),
            'pdf_files': len(record.get('pdf_sha256', {})),
        }
        self._write({'schema': SCHEMA, 'release': 'STAGING_HOLD',
                     'status': 'in_progress', 'last_checkpoint': stage,
                     'counts': counts, 'lab_observations': [
                         {'width': s.get('width'), 'trial': s.get('trial'),
                          'lcp_ms': s.get('lcp_ms'), 'cls': s.get('cls')}
                         for s in record.get('performance_lab_samples', [])],
                     'complete': False,
                     'contains_private_credentials': False,
                     'note': 'Progress only; no WordPress or publication approval.'})

    def fail(self, exception_type):
        # Never serialize Playwright exceptions: they may contain URLs,
        # cookies, form fields, credentials or HTML page content.
        safe_type = exception_type if re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,59}', exception_type) else 'UnknownError'
        payload = self._read()
        if payload.get('status') == 'completed':
            raise ValueError('R105_COMPLETED_RECEIPT_IMMUTABLE')
        payload.update(status='failed', complete=False, exception_type=safe_type)
        self._write(payload)

    def complete(self, record):
        if len(record.get('r103_interaction_cases', [])) != 10 or any(not c.get('passed') for c in record['r103_interaction_cases']):
            raise ValueError('R105_INCOMPLETE_BROWSER_MATRIX')
        if len(record.get('axe', [])) != 2 or any(a.get('violations') for a in record['axe']):
            raise ValueError('R105_INCOMPLETE_AXE')
        samples = record.get('performance_lab_samples', [])
        if len(samples) != 6 or any(not isinstance(s.get('cls'), (int, float)) or s['cls'] > 0.1 or s['cls'] < 0 for s in samples):
            raise ValueError('R105_INCOMPLETE_CLS')
        for width in (390, 1440):
            group = [s for s in samples if s.get('width') == width]
            if sorted(s.get('trial') for s in group) != [1, 2, 3]:
                raise ValueError('R105_MISSING_LAB_TRIAL')
            seen = [s['lcp_ms'] for s in group if isinstance(s.get('lcp_ms'), (int, float))]
            if not seen or any(v < 0 or v > 2500 for v in seen):
                raise ValueError('R105_MISSING_OR_FAILED_LCP')
        images = record.get('screenshots_sha256', {})
        documents = record.get('pdf_sha256', {})
        if len(images) != 4 or len(documents) != 1:
            raise ValueError('R105_INCOMPLETE_ARTIFACT_SET')
        for name, expected in {**images, **documents}.items():
            if not re.fullmatch(r'R104_REAL_WP_[A-Z0-9_]+\.(?:png|pdf)', name):
                raise ValueError('R105_INVALID_ARTIFACT_NAME')
            file = self.directory / name
            if not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest() != expected:
                raise ValueError('R105_ARTIFACT_HASH_MISMATCH')
        self.checkpoint(record, 'all-gates-verified')
        payload = self._read()
        payload.update(status='completed', complete=True,
                       artifact_sha256={**images, **documents},
                       note='R104 isolated WordPress QA complete; release remains STAGING HOLD.')
        self._write(payload)
