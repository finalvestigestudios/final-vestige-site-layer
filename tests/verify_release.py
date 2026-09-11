#!/usr/bin/env python3
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import tempfile

root = pathlib.Path(__file__).resolve().parents[1]
manifest = json.loads((root / "release-manifest.json").read_text())
errors = []

for item in manifest["payloads"]:
    path = root / item["file"]
    if not path.is_file():
        errors.append(f"missing: {item['file']}")
        continue
    data = path.read_bytes()
    if len(data) != item["bytes"]:
        errors.append(f"size mismatch: {item['file']} expected={item['bytes']} actual={len(data)}")
    digest = hashlib.sha256(data).hexdigest()
    if digest != item["sha256"]:
        errors.append(f"sha mismatch: {item['file']} expected={item['sha256']} actual={digest}")
    text = data.decode("utf-8")
    if text.count("<!-- wp:html -->") != 1 or text.count("<!-- /wp:html -->") != 1:
        errors.append(f"wrapper mismatch: {item['file']}")
    scripts = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", text, flags=re.S | re.I)
    for idx, script in enumerate(scripts, start=1):
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
            fh.write(script)
            temp = pathlib.Path(fh.name)
        proc = subprocess.run(["node", "--check", str(temp)], capture_output=True, text=True)
        temp.unlink(missing_ok=True)
        if proc.returncode:
            errors.append(f"JS syntax failed: {item['file']} script {idx}: {proc.stderr.strip()}")

if errors:
    print("RELEASE VERIFY: FAIL")
    print("\n".join(errors))
    sys.exit(1)

print("RELEASE VERIFY: PASS")
for item in manifest["payloads"]:
    print(f"{item['name']}: {item['bytes']} bytes {item['sha256']}")
