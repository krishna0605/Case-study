from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
PART3_APP_PATH = ROOT / "Part 3" / "app.py"


def load_part3_module():
    spec = importlib.util.spec_from_file_location("part3_app", PART3_APP_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def part3_module():
    return load_part3_module()


@pytest.fixture
def client(part3_module):
    app = part3_module.create_app()
    return app.test_client()
