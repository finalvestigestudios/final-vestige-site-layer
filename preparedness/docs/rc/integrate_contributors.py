"""Reproducible integration of the seven contributor branches' newest commits onto the current tree.

For every path a contributor changed since its frozen (pinned) commit:
  - current copy equals the pinned copy  -> take the contributor's newest copy
  - current copy already equals newest   -> nothing to do
  - current copy differs from both       -> real three-way merge (base = pinned copy); conflicts are reported, never discarded
"Current copy" is the working file, so clusters merged earlier in the same run are never overwritten.
CRLF text is normalized to LF (the chain is LF and its custody gates are byte-pinned); binaries are untouched.
Nothing is committed, approved or re-pinned here. Usage (repo root): python integrate_contributors.py REPORT.json [skip-cluster ...]
"""
import json, subprocess, sys, tempfile
from pathlib import Path

CLUSTERS = [  # cluster, frozen (pinned) commit, newest commit
    ("shelter", "5daeaf2dd5ab71806a6b73c91edfb1d8df5da976", "6a5998ea"),
    ("start", "2122d856fce9f64887c16df3d52e64be9f59a55b", "2af10621"),
    ("food", "4b009361277ea1d4617b368f5d45104c7318b284", "f911ff7a655de8d81535ea86ec3d65a49ee76648"),
    ("health", "d2212d0ca0750817d3929865d3069835980faf20", "d5ef5bafd68361434dd1cc9209915b8e8a4eaf17"),
    ("hist-food", "2acf65ca3efa9b4b5db7976f379b9ea693be43a4", "67e116e536c7410bed30f8f3b1bb8c166f3c223d"),
    ("hist-home", "f654e600f89c321a480dd8f055be4d13d0673490", "7504a5f099594d635e3dd7332a33a2e1346c43a2"),
    ("hist-field", "a5ce8a62f168db05c95232e3eb385dccd0d19e7f", "4e5caf812727953aa45e3bda2d382f2c67b6a09c"),
]
TEXT = (".py", ".js", ".json", ".md", ".html", ".css", ".csv", ".txt", ".yml", ".yaml")
SKIP = set(sys.argv[2:])  # clusters deliberately not integrated (documented in the decision register)


def git(*a, check=True):
    r = subprocess.run(["git", *a], capture_output=True)
    if check and r.returncode:
        raise RuntimeError(r.stderr.decode("utf-8", "replace"))
    return r


def blob(ref, path):
    r = git("show", f"{ref}:{path}", check=False)
    return r.stdout if r.returncode == 0 else None


def norm(path, data):
    return data.replace(b"\r\n", b"\n") if data is not None and path.endswith(TEXT) else data


report = {"clusters": {}, "conflicts": [], "skipped_clusters": sorted(SKIP)}
for name, pinned, newest in CLUSTERS:
    newest = git("rev-parse", newest).stdout.decode().strip()
    rows = []
    if name in SKIP:
        report["clusters"][name] = {"pinned": pinned, "newest": newest, "files": [], "note": "NOT INTEGRATED (see decision register)"}
        continue
    changed = git("diff", "--name-status", "--no-renames", pinned, newest, "--", "preparedness").stdout.decode().splitlines()
    for line in changed:
        status, path = line.split("\t", 1)
        if status == "D":
            rows.append({"path": path, "action": "SKIP-deleted-by-contributor"}); continue
        p = Path(path)
        base, theirs, ours = norm(path, blob(pinned, path)), norm(path, blob(newest, path)), norm(path, p.read_bytes() if p.is_file() else None)
        if ours is None and base is None:
            action, out = "add", theirs
        elif ours == theirs:
            action, out = "already-current", None
        elif ours is not None and ours == base:
            action, out = "take-newest", theirs
        elif ours is None:
            action, out = "CONFLICT-deleted-in-chain", None
        elif base is None:
            action, out = "CONFLICT-add-add", None
        elif not path.endswith(TEXT):
            action, out = "CONFLICT-binary", None
        else:
            with tempfile.TemporaryDirectory() as td:
                a, b, c = Path(td, "ours"), Path(td, "base"), Path(td, "theirs")
                a.write_bytes(ours); b.write_bytes(base); c.write_bytes(theirs)
                r = subprocess.run(["git", "merge-file", "-p", "-L", "current", "-L", "pinned", "-L", f"{name}-newest", str(a), str(b), str(c)], capture_output=True)
                action, out = ("three-way-clean", r.stdout) if r.returncode == 0 else ("CONFLICT-three-way", None)
        if out is not None:
            p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(out)
            git("add", "--", path)
        if action.startswith("CONFLICT"):
            report["conflicts"].append({"cluster": name, "path": path, "kind": action})
        rows.append({"path": path, "action": action})
    report["clusters"][name] = {"pinned": pinned, "newest": newest, "files": rows}
Path(sys.argv[1]).write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8", newline="\n")
from collections import Counter
for name, v in report["clusters"].items():
    print(name, dict(Counter(r["action"] for r in v["files"])))
print("conflicts:", len(report["conflicts"]))
for c in report["conflicts"]:
    print("  ", c)
