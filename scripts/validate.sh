#!/usr/bin/env bash
# Jason Stys: fail-fast portable tests, source contracts and repository privacy invariants; no uploads.
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# END CODE MAP
set -euo pipefail
python -m ruff check irkit scripts tests
python -m ruff format --check irkit scripts tests
python -m mypy
python scripts/code_map.py --check
python scripts/file_guide.py --check
python scripts/validate_repo.py
python -m pytest --cov --junitxml=out/tests.xml --cov-report=term --cov-report=json:out/coverage.json
python -m scripts.demo
