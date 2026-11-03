#!/bin/bash
cd "$(dirname "$0")"; export PYTHONUTF8=1; H=saved_live_home_2026-11-02T22-46.html
python harness.py --html $H --variants base,hoist_css --variant-file variants.py --runs 30 --mode light --wait 1500 --enc gzip --out runs/e5_gzip_hoist.jsonl > runs/e5.log 2>&1
python harness.py --html $H --variants base,hoist_css --variant-file variants.py --runs 30 --mode light --wait 1500 --out runs/e6_identity_hoist.jsonl > runs/e6.log 2>&1
python harness.py --html $H --variants live --live https://finalvestige.com/ --runs 30 --mode light --wait 1500 --out runs/e3b_live_light.jsonl > runs/e3b.log 2>&1
echo done > runs/queue2.done
