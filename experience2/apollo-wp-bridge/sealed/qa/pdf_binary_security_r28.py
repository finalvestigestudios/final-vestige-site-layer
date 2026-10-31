#!/usr/bin/env python3
"""Apollo R28: fail-closed binary safety and link/provenance audit of exported PDFs.

Scope: offline, staging only. This inspects the actual PDF object graph and
rendered-document metadata, beyond the text/URL annotations tested in R27.
It does not certify PDF/UA, legal rights, browser CSP, or WordPress deployment.

Requires pypdf==5.9.0 and Poppler pdfdetach; neither downloads content.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Iterable
from pypdf import PdfReader
from pypdf.generic import ArrayObject, BooleanObject, DictionaryObject, IndirectObject

NASA_PHOTOS = (
    'https://www.nasa.gov/image-detail/apollo-1-crew-honored/',
    'https://www.nasa.gov/image-detail/amf-s67-15717/',
    'https://www.nasa.gov/image-detail/amf-s66-58038/',
    'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/',
    'https://www.nasa.gov/image-detail/amf-s67-21294/',
    'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/',
)
NASA_REPORT = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
NASA_POLICY = 'https://www.nasa.gov/nasa-brand-center/images-and-media/'
ALLOWED = frozenset((*NASA_PHOTOS, NASA_REPORT, NASA_POLICY))
# Deny rich media, file launches, remote document actions, Javascript, and any
# attachment/embedded-file/interactive form facility. A URI hyperlink is the
# only approved action, and only with the eight exact NASA destinations above.
FORBIDDEN_KEYS = frozenset({
    '/OpenAction', '/AA', '/JavaScript', '/JS', '/EmbeddedFiles',
    '/AF', '/Collection', '/AcroForm', '/XFA', '/RichMedia', '/EF',
    '/Filespec', '/Launch', '/SubmitForm', '/ImportData', '/Rendition',
})
FORBIDDEN_TYPES = frozenset({'/FileAttachment', '/RichMedia', '/Movie', '/Screen', '/3D'})
FORBIDDEN_ACTIONS = frozenset({'/Launch', '/JavaScript', '/GoToR', '/GoToE', '/SubmitForm', '/ImportData', '/Rendition'})
MAX_VISITED = 7000

class PdfCustodyHold(ValueError):
    pass


def require(condition: bool, explanation: str) -> None:
    if not condition:
        raise PdfCustodyHold(explanation)


def _walk_reachable(root: object) -> Iterable[tuple[str, DictionaryObject]]:
    """Traverse all reachable PDF dictionaries with cycle and size guards."""
    todo: list[tuple[str, object]] = [('catalog', root)]
    indirect_seen: set[tuple[int, int]] = set()
    objects_seen: set[int] = set()
    visited = 0
    while todo:
        path, item = todo.pop()
        if isinstance(item, IndirectObject):
            identity = (item.idnum, item.generation)
            if identity in indirect_seen:
                continue
            indirect_seen.add(identity)
            try:
                item = item.get_object()
            except Exception as exc:
                raise PdfCustodyHold(f'Invalid indirect PDF object at {path}') from exc
        if isinstance(item, (DictionaryObject, ArrayObject)):
            identity = id(item)
            if identity in objects_seen:
                continue
            objects_seen.add(identity)
        visited += 1
        require(visited < MAX_VISITED, 'Unbounded PDF object graph')
        if isinstance(item, DictionaryObject):
            yield path, item
            for key, child in item.items():
                todo.append((f'{path}/{key}', child))
        elif isinstance(item, ArrayObject):
            for index, child in enumerate(item):
                todo.append((f'{path}[{index}]', child))


def audit_pdf_binary(path: Path) -> dict:
    """Return an evidence receipt or refuse the entire PDF on first violation."""
    path = Path(path)
    require(path.is_file() and 1_000 < path.stat().st_size < 4_000_000,
            'PDF absent or outside explicit staging size bounds')
    raw = path.read_bytes()
    require(raw.startswith(b'%PDF-'), 'Not a PDF file')
    try:
        pdf = PdfReader(path, strict=True)
        require(not pdf.is_encrypted, 'Encrypted PDF cannot be independently reviewed')
        root = pdf.trailer['/Root']
        require('/StructTreeRoot' in root, 'Missing actual PDF structure tree')
        structure = root['/StructTreeRoot']
        require('/K' in structure and '/ParentTree' in structure,
                'Incomplete PDF structure/parent tree')
        marked = root.get('/MarkInfo', {})
        require(isinstance(marked.get('/Marked'), BooleanObject) and marked['/Marked'].value is True, 'Tagged flag without MarkInfo/Marked true')
        require(root.get('/Lang') in ('en', 'en-US'), 'Missing English document language')
        require(isinstance(root.get('/ViewerPreferences', {}).get('/DisplayDocTitle'), BooleanObject) and root['/ViewerPreferences']['/DisplayDocTitle'].value is True,
                'Viewer not configured to display descriptive document title')
        require(1 <= len(pdf.pages) <= 6, 'Unexpected PDF pagination')
        require(pdf.metadata and 'Apollo 1' in (pdf.metadata.title or '') and
                'Final Vestige' in (pdf.metadata.title or ''), 'Missing accurate PDF title')
        require('/Encrypt' not in pdf.trailer, 'Encrypted PDF trailer detected')
    except PdfCustodyHold:
        raise
    except Exception as exc:
        raise PdfCustodyHold('PDF parser/catalog integrity failure') from exc

    reachable = 0
    for object_path, obj in _walk_reachable(root):
        reachable += 1
        illegal = FORBIDDEN_KEYS.intersection(str(key) for key in obj.keys())
        require(not illegal, f'Disallowed PDF object key {sorted(illegal)} at {object_path}')
        require(str(obj.get('/Subtype', '')) not in FORBIDDEN_TYPES,
                f'Disallowed PDF media/attachment annotation at {object_path}')
        require(str(obj.get('/S', '')) not in FORBIDDEN_ACTIONS,
                f'Disallowed active PDF action at {object_path}')
        if '/URI' in obj:
            require(str(obj['/URI']) in ALLOWED,
                    f'Unapproved PDF URI in reachable object at {object_path}')

    links: list[str] = []
    for n, page in enumerate(pdf.pages, start=1):
        require('/StructParents' in page, f'Page {n} missing structure-parent link')
        require(len(page.images) == 0, f'Page {n} embeds unapproved imagery')
        for annotation in page.get('/Annots', []):
            try:
                annotation = annotation.get_object()
                require(annotation.get('/Subtype') == '/Link', 'Non-link annotation not permitted')
                require('/StructParent' in annotation, 'Unstructured link annotation')
                action = annotation.get('/A')
                require(isinstance(action, DictionaryObject), 'PDF link lacks action object')
                require(action.get('/S') == '/URI', 'PDF link is not an ordinary URI action')
                require(set(str(k) for k in action.keys()) <= {'/Type', '/S', '/URI'},
                        'PDF link contains extra action instructions')
                url = str(action.get('/URI', ''))
                require(url in ALLOWED, 'PDF link leaves pinned NASA source/policy allowlist')
                links.append(url)
            except PdfCustodyHold:
                raise
            except Exception as exc:
                raise PdfCustodyHold(f'Could not validate page {n} link annotation') from exc
    counts = Counter(links)
    require(set(counts) == ALLOWED, 'Missing or unexpected source/report/policy annotation')
    require(all(counts[u] == 1 for u in NASA_PHOTOS),
            'One clickable annotation required per NASA photograph')
    require(1 <= counts[NASA_REPORT] <= 2 and 1 <= counts[NASA_POLICY] <= 2,
            'NASA report and policy each require 1–2 annotations')
    require(sum(counts.values()) in (8, 9, 10), 'Unexpected number of total PDF links')
    # Poppler catches attachments that PDF/A-like package features could hide
    # outside the ordinary document annotation inventory.
    try:
        detach = subprocess.run(['pdfdetach', '-list', str(path)],
                                capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise PdfCustodyHold('Required Poppler attachment checker unavailable') from exc
    require(detach.returncode == 0 and re.search(r'^0 embedded files\s*$', detach.stdout.strip()),
            'Embedded attachments present or attachment audit inconclusive')
    return {
        'status': 'PASS_OFFLINE_BINARY_SAFETY_ONLY',
        'pdf_sha256': sha256(raw).hexdigest(),
        'pdf_bytes': len(raw), 'pages': len(pdf.pages),
        'reachable_pdf_dictionaries': reachable, 'tag_tree_present': True,
        'document_language': str(root.get('/Lang')),
        'nasa_photo_annotations': len(NASA_PHOTOS),
        'report_and_policy_annotations': counts[NASA_REPORT] + counts[NASA_POLICY],
        'embedded_attachments': 0, 'embedded_images': 0,
        'active_or_non_http_actions': 0,
        'not_certified': ['PDF/UA', 'screen reader', 'axe-core', 'image reuse rights',
                          'WordPress staging', 'hosted browser HTTP CSP'],
    }


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print('Usage: python pdf_binary_security_r28.py PDF [PDF ...]', file=sys.stderr)
        return 2
    try:
        result = [audit_pdf_binary(Path(name)) for name in argv[1:]]
    except PdfCustodyHold as exc:
        print('RELEASE HOLD:', exc, file=sys.stderr)
        return 1
    print(json.dumps({'audited': len(result), 'results': result}, sort_keys=True, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
