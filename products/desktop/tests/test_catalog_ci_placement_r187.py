"""R187: require the R186 catalog preflight on BOTH independent CI runner jobs.

A successful Ubuntu test alone does not constitute Windows source or build
verification. Structural parsing is intentionally narrow, offline and fail-closed;
it does not evaluate arbitrary Actions expressions or approve a release.
"""
from __future__ import annotations

from pathlib import Path
import re
import unittest

GATE_NAME = "R186 six-app static catalog publication gate (38 cases, normal and -OO)"
TEST = "python -m unittest discover -s products/desktop/tests -p 'test_catalog_preflight_r186.py'"
OPTIMIZED = "python -OO -m unittest discover -s products/desktop/tests -p 'test_catalog_preflight_r186.py'"
PREFLIGHT = "python products/desktop/catalog_preflight_r186.py products/desktop/site/software-catalog.gutenberg.html"
COMMANDS = (TEST, OPTIMIZED, PREFLIGHT)


class JobScopeError(ValueError):
    """Missing or misplaced CI gate; fail closed, never imply Windows passed."""


def verify_job_scope(source: str) -> dict[str, int]:
    if type(source) is not str or len(source) > 200_000 or "\t" in source or "\r" in source:
        raise JobScopeError("Invalid workflow source")
    jobs_headers = list(re.finditer(r"(?m)^jobs: *$", source))
    if len(jobs_headers) != 1:
        raise JobScopeError("Missing unique jobs section")
    jobs_text = source[jobs_headers[0].end():]
    top = re.search(r"(?m)^[a-zA-Z][a-zA-Z_-]*: *$", jobs_text)
    if top:
        jobs_text = jobs_text[:top.start()]
    headers = list(re.finditer(r"(?m)^  ([a-z][a-z0-9-]*): *$", jobs_text))
    jobs: dict[str, str] = {}
    for index, h in enumerate(headers):
        name = h.group(1)
        if name in jobs:
            raise JobScopeError("Duplicate job")
        jobs[name] = jobs_text[h.end(): headers[index + 1].start() if index + 1 < len(headers) else len(jobs_text)]
    if set(jobs) != {"source-tests", "windows-build"}:
        raise JobScopeError("Unexpected job set")
    counts: dict[str, int] = {}
    for name, runner in (("source-tests", "ubuntu-24.04"), ("windows-build", "windows-latest")):
        body = jobs[name]
        if re.findall(r"(?m)^    runs-on: ([^\n]+)$", body) != [runner]:
            raise JobScopeError("Runner contract changed")
        steps = list(re.finditer(r"(?m)^      - (?:name|uses): ([^\n]+)$", body))
        gates = []
        for pos, step in enumerate(steps):
            if step.group(1) == GATE_NAME:
                gates.append(body[step.start(): steps[pos + 1].start() if pos + 1 < len(steps) else len(body)])
        if len(gates) != 1:
            raise JobScopeError("Catalog gate is not present exactly once per job")
        gate = gates[0]
        if len(re.findall(r"(?m)^        run: \|$", gate)) != 1:
            raise JobScopeError("Not an executable run step")
        if name == "windows-build":
            if "        shell: pwsh\n" not in gate or '          $env:PYTHONPATH = "products/desktop"\n' not in gate:
                raise JobScopeError("Windows Python/shell contract missing")
        else:
            if "        shell: pwsh" in gate or not re.search(r"(?m)^    env:\n      PYTHONPATH: products/desktop$", body):
                raise JobScopeError("Ubuntu Python environment contract missing")
        script_lines = [line.strip() for line in gate.splitlines() if line.startswith("          ")]
        commands = [line for line in script_lines if line.startswith("python ") or line.startswith("python -OO ")]
        if commands != list(COMMANDS):
            raise JobScopeError("Incomplete or reordered catalog test/preflight execution")
        if name == "windows-build":
            for command in COMMANDS:
                position = script_lines.index(command)
                if position + 1 >= len(script_lines) or not re.fullmatch(
                    r'if \(\$LASTEXITCODE -ne 0\) \{ throw "R186 [^"\n]+" \}',
                    script_lines[position + 1],
                ):
                    raise JobScopeError("Windows native command has no immediate failure guard")
        if "Install pinned local evidence crypto dependency" in body and body.index(GATE_NAME) > body.index("Install pinned local evidence crypto dependency"):
            raise JobScopeError("Catalog gate must run before later build steps")
        counts[name] = len(gates)
    return counts


class CatalogCIPlacementR187(unittest.TestCase):
    @staticmethod
    def fixture() -> str:
        ubuntu = "\n".join("          " + command for command in COMMANDS)
        win = "\n".join(
            "          " + command + "\n          if ($LASTEXITCODE -ne 0) { throw \"R186 gate failed\" }"
            for command in COMMANDS
        )
        return ("name: Desktop suite build (internal)\n"
                "jobs:\n"
                "  source-tests:\n"
                "    runs-on: ubuntu-24.04\n"
                "    env:\n"
                "      PYTHONPATH: products/desktop\n"
                "    steps:\n"
                f"      - name: {GATE_NAME}\n"
                "        run: |\n" + ubuntu + "\n"
                "      - name: Install pinned local evidence crypto dependency\n"
                "        run: python -m pip install cryptography\n"
                "  windows-build:\n"
                "    runs-on: windows-latest\n"
                "    steps:\n"
                f"      - name: {GATE_NAME}\n"
                "        shell: pwsh\n"
                "        run: |\n"
                '          $env:PYTHONPATH = "products/desktop"\n' + win + "\n"
                "      - name: Install pinned local evidence crypto dependency\n"
                "        run: python -m pip install cryptography\n")

    def rejected(self, data: str):
        with self.assertRaises(JobScopeError):
            verify_job_scope(data)

    def test_valid_dual_runner_contract(self):
        self.assertEqual(verify_job_scope(self.fixture()), {"source-tests": 1, "windows-build": 1})

    def test_real_tracked_workflow(self):
        path = Path(__file__).resolve().parents[3] / '.github' / 'workflows' / 'desktop-build.yml'
        self.assertEqual(verify_job_scope(path.read_text(encoding='utf-8')), {"source-tests": 1, "windows-build": 1})

    def test_reject_previous_windows_step_misplaced_in_ubuntu(self):
        src = self.fixture()
        start = src.index('      - name: ' + GATE_NAME, src.index('  windows-build:'))
        self.rejected(src[:start] + src[src.index('      - name: Install pinned local evidence crypto dependency', start):])

    def test_reject_missing_ubuntu_gate(self):
        self.rejected(self.fixture().replace('      - name: ' + GATE_NAME, '      - name: Missing gate', 1))

    def test_reject_duplicate_ubuntu_gate(self):
        src = self.fixture()
        block = src[src.index('      - name: ' + GATE_NAME):src.index('      - name: Install pinned local evidence crypto dependency')]
        self.rejected(src.replace(block, block + block, 1))

    def test_reject_missing_optimized_windows(self):
        src = self.fixture()
        pivot = src.index('  windows-build:')
        self.rejected(src[:pivot] + src[pivot:].replace('          ' + OPTIMIZED + '\n', '', 1))

    def test_reject_missing_windows_preflight(self):
        src = self.fixture()
        pivot = src.index('  windows-build:')
        self.rejected(src[:pivot] + src[pivot:].replace('          ' + PREFLIGHT + '\n', '', 1))

    def test_reject_missing_ubuntu_normal_test(self):
        self.rejected(self.fixture().replace('          ' + TEST + '\n', '', 1))

    def test_reject_windows_no_exit_check(self):
        src = self.fixture()
        pivot = src.index('  windows-build:')
        self.rejected(src[:pivot] + src[pivot:].replace('          if ($LASTEXITCODE -ne 0) { throw "R186 gate failed" }\n', '', 1))

    def test_reject_windows_wrong_shell(self):
        self.rejected(self.fixture().replace('        shell: pwsh\n', '        shell: bash\n'))

    def test_reject_windows_wrong_runner(self):
        self.rejected(self.fixture().replace('runs-on: windows-latest', 'runs-on: ubuntu-24.04'))

    def test_reject_missing_ubuntu_environment(self):
        self.rejected(self.fixture().replace('      PYTHONPATH: products/desktop\n', ''))

    def test_reject_window_command_reorder(self):
        src = self.fixture()
        pivot = src.index('  windows-build:')
        self.rejected(src[:pivot] + src[pivot:].replace(OPTIMIZED, 'python -OO -m unittest discover -s other -p missing.py'))

    def test_reject_duplicated_windows_job(self):
        src = self.fixture()
        win = src[src.index('  windows-build:'):]
        self.rejected(src + win)

    def test_reject_early_invalid_type(self):
        with self.assertRaises(JobScopeError):
            verify_job_scope(b'jobs:')

    def test_reject_large_workflow(self):
        self.rejected(self.fixture() + ' ' * 200_001)


if __name__ == '__main__':
    unittest.main()
