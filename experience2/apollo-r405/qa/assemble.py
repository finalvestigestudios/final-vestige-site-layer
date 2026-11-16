#!/usr/bin/env python3
"""Offline verified stage bundle; never writes WordPress/GitHub or fetches the web."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXPECT = {
    'templates/ledger.html': ('research', 'templates/ledger.html', '403d128c57b9bc82dac7c619651689070edef86c'),
    'assets/source-ledger.css': ('research', 'assets/source-ledger.css', 'b8cf00afeceba115a9e9d19044fc11dcf2890cbe'),
    'assets/research-desk-resilient.js': ('r404', 'assets/research-desk-resilient.js', '4f2d41dc1dc3d5e321b36a422cefd06a0ecd6760'),
    'assets/research-desk-resilient.css': ('r404', 'assets/research-desk-resilient.css', '2c99fdeecd4d4245908c0f52f6a679c6f5d7718a'),
}

def git_blob(payload: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(payload)).encode('ascii') + b'\x00' + payload).hexdigest()

def assemble(research: Path, r404: Path) -> bytes:
    files = {'staging-shortcode.php': (ROOT / 'staging-shortcode.php').read_bytes()}
    for destination, (source, relpath, expected) in EXPECT.items():
        item = (research if source == 'research' else r404) / relpath
        data = item.read_bytes()  # fails closed on missing source checkout
        found = git_blob(data)
        if found != expected:
            raise ValueError(f'Git blob mismatch for {destination}: expected {expected}, got {found}')
        files[destination] = data
    manifest = {
        'build': 'Apollo R405 STAGING OFFLINE candidate only; not approved for install',
        'source_pr': {'research_desk': 158, 'resilience': 2728},
        'files': {path: {'git_blob': git_blob(payload), 'sha256': hashlib.sha256(payload).hexdigest()}
                  for path, payload in sorted(files.items())},
        'status': 'NOT_INSTALLED',
    }
    files['MANIFEST.json'] = (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode()
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, content in sorted(files.items()):
            info = zipfile.ZipInfo('fv-apollo-r405/' + name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return out.getvalue()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--research-desk-dir', type=Path, required=True, help='An exact PR #158 checkout directory')
    ap.add_argument('--r404-dir', type=Path, required=True, help='R404 source directory')
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    data = assemble(args.research_desk_dir, args.r404_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)
    print(json.dumps({'status': 'BUILT_OFFLINE_NOT_INSTALLED', 'bytes': len(data),
                      'sha256': hashlib.sha256(data).hexdigest(), 'output': str(args.output)}))

if __name__ == '__main__':
    main()
