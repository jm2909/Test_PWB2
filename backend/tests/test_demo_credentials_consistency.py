"""Seed constants == frontend demo-credentials.ts == README (one canonical source)."""

from __future__ import annotations

import re
from pathlib import Path

from app.seeds.constants import ASHA_EMAIL, DEMO_PASSWORD, ROHAN_EMAIL

ROOT = Path(__file__).resolve().parents[2]


def test_frontend_constants_match_seed():
    text = (ROOT / "frontend/src/lib/demo-credentials.ts").read_text()
    found = dict(re.findall(r"export const (\w+) = '([^']*)'", text))
    assert found["DEMO_PASSWORD"] == DEMO_PASSWORD
    assert found["DEMO_ASHA_EMAIL"] == ASHA_EMAIL
    assert found["DEMO_ROHAN_EMAIL"] == ROHAN_EMAIL


def test_readme_documents_seed_credentials():
    readme = (ROOT / "README.md").read_text()
    for value in (ASHA_EMAIL, ROHAN_EMAIL, DEMO_PASSWORD):
        assert value in readme


def test_e2e_specs_use_seed_credentials():
    for spec in (ROOT / "frontend/e2e").glob("*.spec.ts"):
        text = spec.read_text()
        for password in re.findall(r"PASSWORD = '([^']*)'", text):
            assert password == DEMO_PASSWORD, spec.name
