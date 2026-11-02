"""Discover nested R69 scenario tests from the campaign's existing test entrypoint.
The Actions workflow discovers campaign/tests/, not nested r69 directories.
"""
import importlib.util
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "r69-channel-reality" / "tests" / "test_r69_channel_reality.py"
assert SOURCE.is_file(), "R69 nested QA module is missing"
spec = importlib.util.spec_from_file_location("fv_dispatch_r69_channel_reality", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
ReleaseTests = module.ReleaseTests
