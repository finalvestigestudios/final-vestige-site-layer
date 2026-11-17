#!/usr/bin/env python3
"""Fetch exactly reviewed Apollo Research Desk Git blobs; never mutate WordPress.

Only GitHub's immutable blob endpoint is used. The checkout is refused on ANY
missing, changed, symlinked, truncated, or unreviewed source. No live URL fallback.
"""
from __future__ import annotations
import argparse, base64, hashlib, json, os, pathlib, tempfile, urllib.request

REPO = 'finalvestigestudios/final-vestige-site-layer'
BLOBS = {
 'experience2/research-desk/final-vestige-ex2-research-desk.php': 'd1879a90101b5475990132369178f42743f4b57c',
 'experience2/research-desk/templates/ledger.html': '403d128c57b9bc82dac7c619651689070edef86c',
 'experience2/research-desk/assets/source-ledger.css': 'b8cf00afeceba115a9e9d19044fc11dcf2890cbe',
 'experience2/research-desk/assets/source-ledger.js': '32e757cc4dc8708397ff65ac21e89dd319781d78',
 'experience2/apollo-r423/staging-research-desk-bridge.php': '1491e5eca2f749849136d0b41cc9a2ca7b255023',
 'experience2/apollo-r423/assets/bridge.css': 'ac6763aeee56b2e80277ccef4a13d126a4e7e977',
}
MAX_BLOB = 250_000

def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('redirect forbidden for pinned Git blob fetch')

def fetch_blob(sha: str, token: str | None = None) -> bytes:
    if len(sha) != 40 or any(c not in '0123456789abcdef' for c in sha):
        raise ValueError('invalid pinned SHA')
    url = f'https://api.github.com/repos/{REPO}/git/blobs/{sha}'
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'fv-apollo-r425-read-only', 'X-GitHub-Api-Version': '2022-11-28'}
    if token: headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.build_opener(NoRedirect()).open(req, timeout=15) as resp:
        raw = resp.read(2*MAX_BLOB + 4096)
        if len(raw) >= 2*MAX_BLOB + 4096: raise ValueError('oversize API response')
    record = json.loads(raw)
    if record.get('encoding') != 'base64' or record.get('sha') != sha:
        raise ValueError('GitHub blob identity or encoding mismatch')
    data = base64.b64decode(record['content'], validate=False)
    if len(data) > MAX_BLOB or record.get('size') != len(data) or git_blob(data) != sha:
        raise ValueError('wrong blob size or content')
    return data

def bootstrap(output: pathlib.Path, transport=fetch_blob, token: str | None=None) -> dict:
    output = pathlib.Path(output)
    if output.exists() or output.is_symlink(): raise ValueError('output must not exist; stale checkout prohibited')
    if any(p in ('.', '..') for rel in BLOBS for p in pathlib.PurePosixPath(rel).parts):
        raise ValueError('unsafe manifest path')
    # Fetch and validate everything BEFORE writing, to forbid partially trusted trees.
    verified = {}
    for rel, sha in BLOBS.items():
        data = transport(sha, token)
        if not isinstance(data, bytes) or len(data) > MAX_BLOB or git_blob(data) != sha:
            raise ValueError(f'identity validation failed: {rel}')
        verified[rel] = data
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.apollo-r425-', dir=output.parent) as temporary:
        staging = pathlib.Path(temporary) / 'checkout'
        for rel, data in verified.items():
            path=staging/rel
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(data)
        manifest = {
            'reviewed_pr158_commit':'250d7f05a4de037e73826dcf0cfaef0ec4c29383',
            'reviewed_r423_commit':'93dda51158453fbc8e2fcc353ef535490eac0d73',
            'purpose':'read-only authentic R424 QA checkout, not installed WordPress',
            'sources':{rel:{'git_blob':BLOBS[rel],'sha256':hashlib.sha256(verified[rel]).hexdigest(),'size':len(verified[rel])} for rel in sorted(verified)}
        }
        (staging/'source-manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf-8')
        staging.rename(output)
    return manifest

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=pathlib.Path,required=True)
    args=parser.parse_args()
    try:
        manifest=bootstrap(args.output,token=os.environ.get('GITHUB_TOKEN'))
        print(json.dumps({'result':'SOURCE_CHECKOUT_VERIFIED','manifest':manifest},sort_keys=True))
    except Exception as exc:
        print(json.dumps({'result':'HOLD','blocker':str(exc)},sort_keys=True))
        raise SystemExit(2)
