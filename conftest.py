"""Shared test loader; keep unchanged. Supports testing any supplied implementation."""

import importlib.util
from pathlib import Path
import sys

import pytest


def pytest_addoption(parser):
    parser.addoption("--alignment-file", default=None, help="Path to implementation to test")


@pytest.fixture(scope="session")
def align(request):
    specified = request.config.getoption("--alignment-file")
    path = Path(specified).resolve() if specified else Path(__file__).parent / "alignment.py"
    # Preserve helper-module imports beside the supplied implementation.
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("alignment", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        yield module.align_trajectory
    finally:
        sys.path.remove(str(path.parent))
