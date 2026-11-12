#!/usr/bin/env python3
"""R317 read-only AST safety gate: Preparedness tests must not write source inputs.

This detector is intentionally conservative. It never executes imported tests or
modifies the checkout. Positive detection is a review hold, not proof of misuse.
"""
from __future__ import annotations
import argparse
import ast
import json
from pathlib import Path

SCHEMA = 'fv-preparedness-r317-test-source-mutation-hold-v1'
SOURCE_COMPONENTS = {'sources', 'content', 'assets', 'tools', 'build'}
ROOT_FILES = {'taxonomy.json', 'slate.json', 'validate.py', 'build.py'}
REQUIRED_TESTS = {'test_preparedness.py', 'test_r316_authentic_41_export_parity_hold.py'}
MUTATORS = {'write_text', 'write_bytes', 'unlink', 'rename', 'replace', 'rmdir',
            'mkdir', 'touch', 'chmod', 'symlink_to', 'hardlink_to'}

def literal_part(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None

def path_origin(node: ast.AST, aliases: dict[str, tuple[str, ...]]) -> tuple[str, ...] | None:
    """Resolve only explicit ROOT-derived path operations, not arbitrary names."""
    if isinstance(node, ast.Name):
        return ('ROOT',) if node.id == 'ROOT' else aliases.get(node.id)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        base = path_origin(node.left, aliases)
        part = literal_part(node.right)
        return base + (part,) if base is not None and part is not None else None
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        if node.func.attr == 'joinpath':
            base = path_origin(node.func.value, aliases)
            parts = [literal_part(v) for v in node.args]
            return base + tuple(parts) if base is not None and all(p is not None for p in parts) else None
    return None

def is_canonical_source(parts: tuple[str, ...] | None) -> bool:
    return bool(parts and parts[0] == 'ROOT' and (any(p in SOURCE_COMPONENTS for p in parts[1:]) or any(p in ROOT_FILES for p in parts[1:])))

class Checker(ast.NodeVisitor):
    def __init__(self):
        self.scope: list[dict[str, tuple[str, ...]]] = [{}]
        self.findings: list[dict] = []
    def aliases(self) -> dict[str, tuple[str, ...]]:
        d = {}
        for s in self.scope:
            d.update(s)
        return d
    def visit_FunctionDef(self, node):
        self.scope.append({}); self.generic_visit(node); self.scope.pop()
    visit_AsyncFunctionDef = visit_FunctionDef
    def visit_Assign(self, node):
        self.visit(node.value)
        path = path_origin(node.value, self.aliases())
        for target in node.targets:
            if isinstance(target, ast.Name):
                if path: self.scope[-1][target.id] = path
                else: self.scope[-1].pop(target.id, None)
    def visit_AnnAssign(self, node):
        if node.value: self.visit(node.value)
        if isinstance(node.target, ast.Name):
            path = path_origin(node.value, self.aliases()) if node.value else None
            if path: self.scope[-1][node.target.id] = path
            else: self.scope[-1].pop(node.target.id, None)
    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            name = node.func.attr
            target = path_origin(node.func.value, self.aliases())
            write_open = name == 'open' and (any(
                isinstance(a, ast.Constant) and isinstance(a.value, str) and
                any(c in a.value for c in 'wax+') for a in node.args[:1]) or any(
                kw.arg == 'mode' and isinstance(kw.value, ast.Constant) and
                isinstance(kw.value.value, str) and any(c in kw.value.value for c in 'wax+')
                for kw in node.keywords))
            if (name in MUTATORS or write_open) and is_canonical_source(target):
                self.findings.append({'line':node.lineno,'operation':name,'source_path':'/'.join(target)})
        self.generic_visit(node)

def audit_test_text(source: str, filename: str) -> list[dict]:
    tree = ast.parse(source, filename=filename)
    checker = Checker(); checker.visit(tree)
    return [{'file': filename, **f} for f in checker.findings]

def scan_tree(root: Path) -> dict:
    tests = root / 'preparedness' / 'tests'
    errors, findings, count = [], [], 0
    if not tests.is_dir() or tests.is_symlink():
        errors.append('MISSING_OR_LINKED_TEST_DIRECTORY')
    else:
        for path in sorted(tests.glob('test_*.py')):
            count += 1
            if path.is_symlink():
                errors.append('LINKED_TEST_FILE:' + path.name); continue
            try:
                findings += audit_test_text(path.read_text(encoding='utf-8'), str(path.relative_to(root)))
            except (SyntaxError, UnicodeError, OSError):
                errors.append('UNREADABLE_OR_INVALID_TEST:' + path.name)
        if not count: errors.append('NO_TESTS_DISCOVERED')
        missing = REQUIRED_TESTS - {p.name for p in tests.glob('test_*.py')}
        if missing: errors.append('MISSING_CORE_TEST_FILES:' + ','.join(sorted(missing)))
    if findings: errors.append('DIRECT_MUTATION_OF_CANONICAL_SOURCE_IN_TEST')
    return {'schema':SCHEMA,'state':'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
            'tests_inspected':count,'findings':findings,'errors':sorted(errors),
            'independent_qd_pass':False,'publication_authorized':False,
            'paid_conversion_verified':False}

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]); args=ap.parse_args()
    result=scan_tree(args.root)
    print(json.dumps(result,indent=2,sort_keys=True))
    return 1 if result['state']=='INVALID_HARD_HOLD' else 2
if __name__ == '__main__': raise SystemExit(main())
