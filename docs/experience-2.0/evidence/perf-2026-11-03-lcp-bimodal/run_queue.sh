#!/bin/bash
# sequential experiment queue (never run two browsers at once: they contend for CPU and perturb each other)
cd "$(dirname "$0")"; export PYTHONUTF8=1; H=saved_live_home_2026-11-02T22-46.html
while pgrep -f "harness.py" >/dev/null; do sleep 5; done
python harness.py --html $H --variants base --runs 16 --mode rich --wait 1500 --out runs/e4_identity_rich.jsonl > runs/e4.log 2>&1
python harness.py --html $H --variants base,hoist_css --variant-file variants.py --runs 30 --mode light --wait 1500 --enc gzip --out runs/e5_gzip_hoist.jsonl > runs/e5.log 2>&1
python harness.py --html $H --variants base,hoist_css --variant-file variants.py --runs 30 --mode light --wait 1500 --out runs/e6_identity_hoist.jsonl > runs/e6.log 2>&1
python harness.py --html $H --variants base --runs 20 --mode light --wait 1500 --enc gzip --cache warm --out runs/e7_gzip_warm.jsonl > runs/e7.log 2>&1
python harness.py --html $H --variants base --runs 20 --mode light --wait 1500 --enc gzip --cpu 6 --out runs/e8_gzip_cpu6.jsonl > runs/e8.log 2>&1
python harness.py --html $H --variants base --runs 20 --mode light --wait 1500 --enc gzip --cpu 2 --out runs/e9_gzip_cpu2.jsonl > runs/e9.log 2>&1
python harness.py --html $H --variants base --runs 20 --mode light --wait 1500 --enc gzip --net 0.8 --out runs/e10_gzip_net08.jsonl > runs/e10.log 2>&1
echo queue-done > runs/queue.done
