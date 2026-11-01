"""Deterministic ZIP creator for private R35 QA evidence; no network or uploads.

Usage: python tests/build_r35_archive.py /path/to/r35_workspace /path/to/output.zip
Workspace contains experience2/research-desk source and optional qa/ receipts.
"""
import hashlib
import json
import pathlib
import sys
import zipfile

FIXED = (1980, 1, 1, 0, 0, 0)
INCLUDE = ("experience2/research-desk", "qa")


def build(workspace: pathlib.Path, output: pathlib.Path):
    inputs = sorted((p for folder in INCLUDE for p in (workspace / folder).rglob('*') if p.is_file()
                     and '__pycache__' not in p.parts and 'browser_repeat' not in p.parts
                     and p.suffix not in {'.pyc', '.zip'}), key=lambda p: p.relative_to(workspace).as_posix())
    manifest = {p.relative_to(workspace).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for path, data in [(p.relative_to(workspace).as_posix(), p.read_bytes()) for p in inputs] + [
            ('SHA256_MANIFEST.json', (json.dumps(manifest, indent=2, sort_keys=True) + '\n').encode())]:
            info = zipfile.ZipInfo(path, date_time=FIXED)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    print(json.dumps({'archive':str(output),'files':len(manifest)+1,'sha256':hashlib.sha256(output.read_bytes()).hexdigest()}, sort_keys=True))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('usage: python build_r35_archive.py WORKSPACE OUTPUT.zip')
    build(pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]))
