#!/usr/bin/env python3
"""R105 crash-safe, non-secret evidence receipts for genuine WordPress browser QA.

An evidence journal, never authorization to publish. No historical claims,
hosted network calls, or WordPress content/settings writes.
"""
import hashlib
import json
import math
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
        if self._read().get('status') == 'completed':
            raise ValueError('R106_COMPLETED_RECEIPT_IMMUTABLE')
        if not isinstance(stage, str) or not CHECKPOINT.fullmatch(stage):
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
        """Certify *complete* isolated-browser evidence, never production readiness.

        Reject plausible looking but incomplete / forged matrix entries, non-finite
        numbers, missing LCP observations and artifact substitution. All values are
        evaluated from the test harness' in-memory record, not untrusted web input.
        """
        if self._read().get('status') == 'completed':
            raise ValueError('R106_COMPLETED_RECEIPT_IMMUTABLE')
        if (record.get('schema') != 'fv.apollo.r104.real-wp-gallery.v1'
                or record.get('release') != 'STAGING_HOLD'
                or record.get('real_wordpress_core_http') is not True
                or record.get('hosted_wordpress_or_assembler_verified') is not False
                or record.get('production_core_web_vitals') is not False):
            raise ValueError('R106_SCOPE_MISMATCH')

        cases = record.get('r103_interaction_cases', [])
        expected = {(width, js) for width in (320, 390, 768, 1440, 1920)
                    for js in (False, True)}
        observed = set()
        if len(cases) != len(expected):
            raise ValueError('R106_INCOMPLETE_BROWSER_MATRIX')
        for case in cases:
            if not isinstance(case, dict):
                raise ValueError('R106_INCOMPLETE_BROWSER_MATRIX')
            key = (case.get('width'), case.get('javascript_enabled'))
            if (type(key[0]) is not int or type(key[1]) is not bool
                    or key not in expected or key in observed
                    or case.get('passed') is not True
                    or case.get('actual_wordpress_http') is not True
                    or case.get('reduced_motion') is not True
                    or case.get('forced_colors') is not (key[0] == 320)):
                raise ValueError('R106_INCOMPLETE_BROWSER_MATRIX')
            observed.add(key)
        if observed != expected:
            raise ValueError('R106_INCOMPLETE_BROWSER_MATRIX')

        axe = record.get('axe', [])
        if len(axe) != 2 or {a.get('width') for a in axe if isinstance(a, dict)} != {390, 1440}:
            raise ValueError('R106_INCOMPLETE_AXE')
        for scan in axe:
            if (scan.get('state') != 'selected_two_sources'
                    or type(scan.get('passes')) is not int or scan['passes'] <= 0
                    or scan.get('violations') != []):
                raise ValueError('R106_INCOMPLETE_AXE')

        samples = record.get('performance_lab_samples', [])
        expected_trials = {(width, trial) for width in (390, 1440) for trial in (1, 2, 3)}
        observed_trials = set()
        if len(samples) != 6:
            raise ValueError('R106_INCOMPLETE_LAB_MATRIX')
        for sample in samples:
            if not isinstance(sample, dict):
                raise ValueError('R106_INCOMPLETE_LAB_MATRIX')
            key = (sample.get('width'), sample.get('trial'))
            if (type(key[0]) is not int or type(key[1]) is not int
                    or key not in expected_trials or key in observed_trials):
                raise ValueError('R106_MISSING_LAB_TRIAL')
            observed_trials.add(key)
            cls = sample.get('cls')
            if (type(cls) not in (int, float) or not math.isfinite(cls)
                    or cls < 0 or cls > 0.1):
                raise ValueError('R106_INVALID_OR_FAILED_CLS')
            lcp = sample.get('lcp_ms')
            if (type(lcp) not in (int, float) or not math.isfinite(lcp)
                    or lcp <= 0 or lcp > 2500):
                raise ValueError('R106_MISSING_OR_FAILED_LCP')
        if observed_trials != expected_trials:
            raise ValueError('R106_MISSING_LAB_TRIAL')

        images = record.get('screenshots_sha256', {})
        documents = record.get('pdf_sha256', {})
        expected_images = {f'R104_REAL_WP_SELECTED_{width}.png' for width in (320, 390, 1440)}
        expected_images.add('R104_REAL_WP_NOJS_390.png')
        expected_documents = {'R104_REAL_WP_PRINT.pdf'}
        if set(images) != expected_images or set(documents) != expected_documents:
            raise ValueError('R106_INCOMPLETE_ARTIFACT_SET')
        for name, digest in {**images, **documents}.items():
            if not isinstance(digest, str) or not re.fullmatch(r'[a-f0-9]{64}', digest):
                raise ValueError('R106_INVALID_ARTIFACT_HASH')
            file = self.directory / name
            if not file.is_file():
                raise ValueError('R106_MISSING_ARTIFACT')
            content = file.read_bytes()
            if (name.endswith('.png') and not content.startswith(b'\\x89PNG\\r\\n\\x1a\\n')) or (name.endswith('.pdf') and not content.startswith(b'%PDF-')):
                raise ValueError('R106_INVALID_ARTIFACT_TYPE')
            if hashlib.sha256(content).hexdigest() != digest:
                raise ValueError('R106_ARTIFACT_HASH_MISMATCH')
        self.checkpoint(record, 'all-gates-verified')
        payload = self._read()
        payload.update(status='completed', complete=True,
                       artifact_sha256={**images, **documents},
                       note='Isolated WordPress QA evidence complete; release remains STAGING HOLD.')
        self._write(payload)
