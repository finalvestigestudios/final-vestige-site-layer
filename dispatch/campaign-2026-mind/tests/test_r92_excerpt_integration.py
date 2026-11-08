"""Run the standalone R92 native tests in the canonical Dispatch test discovery lane."""
import importlib.util
import pathlib
import unittest

PATH = pathlib.Path(__file__).resolve().parents[1] / "r92-excerpt-mode-truth" / "tests" / "test_r92_excerpt_contract.py"

def load_tests(loader, standard_tests, pattern):
    spec = importlib.util.spec_from_file_location("r92_tests", PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    standard_tests.addTests(loader.loadTestsFromModule(module))
    return standard_tests
