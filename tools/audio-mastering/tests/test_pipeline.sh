#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
./tests/make_test_assets.sh
rm -rf build/test-podcast build/test-youtube
python3 src/master_audio.py examples/mix.example.json --profile podcast --out-dir build/test-podcast
python3 src/master_audio.py examples/mix.example.json --profile youtube --out-dir build/test-youtube
python3 - <<'PY'
import json
from pathlib import Path
for p in [Path('build/test-podcast/POD-001_podcast_master_qc.json'), Path('build/test-youtube/POD-001_youtube_master_qc.json')]:
    d=json.loads(p.read_text())
    assert d['status']=='PASS', d
    assert d['required_layers']['music'] is True
    assert d['required_layers']['sfx_count'] >= 1
print('Final Vestige audio lane tests: PASS')
PY
