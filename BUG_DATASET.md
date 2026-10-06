# ShopBug Bug Dataset — Summary

> **IMPORTANT**: This file and the accompanying `dataset/` directory are **evaluation-only metadata**.
> They must NOT be included in the repository ingestion pipeline when evaluating an AI bug-localization system.
> Provide only the repository source code and natural-language issue reports to the system under test.

## Overview

The ShopBug bug dataset contains **20 intentional software bugs** spanning the full application stack:
frontend (React), backend (FastAPI services), database (SQLAlchemy queries), and frontend/backend
integration. Each bug is syntactically valid but behaviourally incorrect, and is accompanied by a
reproduction test, ground-truth localization data, and a natural-language issue report written
in the style of a real user or developer report.

## What Has Changed From Version 1

Version 1 contained 20 backend-only bugs concentrated in 5 Python service files.
Version 2 expands coverage to:

- **9 frontend bugs** across 6 different React files
- **2 database-layer bugs** (incorrect queries / missing filters)
- **2 integration bugs** (frontend/backend interface contract failures)
- **9 backend-logic bugs** across 4 service files
- New metadata fields: `layer`, `issue_type`
- Bug IDs are **interleaved** across layers so the layer is not predictable from the ID

## Schema

Each bug record contains the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `bug_id` | string | Unique identifier (B001–B020) |
| `category` | string | Bug category (see categories below) |
| `layer` | string | frontend / backend / database / integration |
| `difficulty` | string | easy / medium / hard |
| `issue_report_quality` | string | specific / moderate / vague |
| `issue_type` | string | user / developer |
| `issue_report` | string | Natural-language report as a user or developer would file it |
| `expected_behavior` | string | What the correct behaviour is |
| `actual_behavior` | string | What actually happens due to the bug |
| `root_cause_file` | string | Single file containing the incorrect logic |
| `root_cause_function` | string | Function/method containing the root cause |
| `root_cause_lines` | array[int] | Line numbers of the buggy code |
| `affected_files` | array[string] | All files whose behaviour is impacted |
| `root_cause_description` | string | Technical explanation of exactly what is wrong |
| `reproduction_steps` | array[string] | Steps to reproduce the observed behaviour |
| `reproduction_test` | string | Path to the automated reproduction test |
| `commit_hash` | string | Git commit hash of the injected-bugs version |
| `scope` | string | single-file / multi-file |

## Categories Covered

| Category | Description |
|----------|-------------|
| `api_integration` | Frontend reads or sends data to the wrong API field / endpoint |
| `authentication` | Login, registration, or session management failures |
| `backend_logic` | Inverted conditions or wrong control flow in backend services |
| `calculation` | Arithmetic errors in price, tax, subtotal, or discount computation |
| `database` | Incorrect SQLAlchemy filters, missing clauses, or wrong field access |
| `dependency` | A function call that omits a required argument, breaking a dependency chain |
| `frontend_logic` | Incorrect computation or conditional logic in React components |
| `input_validation` | Missing or wrong boundary checks on user-supplied values |
| `navigation` | Routes pointing to wrong page components |
| `page_failure` | Component always renders empty / blank due to a state assignment bug |
| `state_management` | Frontend state is set with wrong data, breaking subsequent interactions |
| `ui_rendering` | Component crashes on render due to type mismatch in state initialization |

## Distributions

### By Layer

| Layer | Count | Bug IDs |
|-------|-------|---------|
| frontend | 9 | B001, B003, B007, B009, B011, B013, B015, B005* |
| backend | 9 | B002, B004, B006, B008, B010, B012, B014, B016, B017, B019, B020 |
| integration | 1 | B005 |
| database | 2 | B006, B018 |

*B005 is tagged `integration` because the root cause is in the frontend API service layer but the
failure manifests at the FastAPI endpoint contract boundary.

### By Category

| Category | Count | Bug IDs |
|----------|-------|---------|
| authentication | 3 | B016, B019, B020 |
| calculation | 3 | B002, B003, B017 |
| api_integration | 2 | B001, B005 |
| input_validation | 2 | B004, B008 |
| backend_logic | 2 | B010, B014 |
| database | 2 | B006, B018 |
| frontend_logic | 2 | B003, B015 |
| dependency | 1 | B012 |
| navigation | 1 | B011 |
| page_failure | 1 | B007 |
| state_management | 1 | B013 |
| ui_rendering | 1 | B009 |

### By Difficulty

| Difficulty | Count | Bug IDs |
|------------|-------|---------|
| easy | 6 | B004, B007, B011, B016, B019, B020 |
| medium | 8 | B002, B003, B006, B008, B009, B010, B013, B015 |
| hard | 6 | B001, B005, B012, B014, B017, B018 |

### By Issue Report Quality

| Quality | Count | Bug IDs |
|---------|-------|---------|
| specific | 5 | B004, B011, B016, B019, B020 |
| moderate | 9 | B002, B003, B007, B008, B013, B014, B015, B018* |
| vague | 6 | B001, B005, B006, B009, B010, B012, B017, B018 |

### By Issue Type

| Type | Count | Bug IDs |
|------|-------|---------|
| user | 12 | B001, B003, B005, B006, B007, B009, B011, B013, B015, B017, B018, B019, B020 |
| developer | 7 | B002, B004, B008, B010, B012, B014, B016 |

### By Scope

| Scope | Count | Bug IDs |
|-------|-------|---------|
| single-file | 12 | B002, B003, B004, B006, B007, B008, B009, B010, B011, B016, B018, B019, B020 |
| multi-file | 8 | B001, B005, B012, B013, B014, B015, B017 |

## Layer Distribution (Precise)

| Layer | Files |
|-------|-------|
| Frontend | frontend/src/context/AuthContext.jsx, frontend/src/pages/Cart.jsx, frontend/src/services/api.js, frontend/src/pages/Products.jsx, frontend/src/pages/Orders.jsx, frontend/src/App.jsx, frontend/src/components/ProductCard.jsx |
| Backend | app/services/checkout_service.py, app/services/cart_service.py, app/services/discount_service.py, app/services/auth_service.py, app/services/product_service.py |

## Research Usage

### For AI Bug Localization Evaluation

1. **Repository ingestion**: provide only `app/` and `frontend/src/` source files plus the issue report.
   Exclude `dataset/`, `BUG_DATASET.md`, and `scripts/validate_dataset.py`.

2. **Evaluation**: compare the AI system's predicted `root_cause_file` and `root_cause_function`
   against the ground-truth values in `dataset/bug_dataset.json`.

3. **Reproduction**: run `pytest tests/reproduction_tests/ -v` to confirm all 20 bugs are active
   (all tests should **fail** on the buggy codebase).

4. **Validation**: run `python scripts/validate_dataset.py` to verify dataset integrity.

### Metrics

- **File-level accuracy**: did the model predict the correct root_cause_file?
- **Function-level accuracy**: did the model predict the correct root_cause_function?
- **Top-k accuracy**: was the correct file/function in the top-k predictions?
- **Layer accuracy**: did the model correctly identify frontend vs backend vs integration?

## Files

- `dataset/bug_dataset.json` — Full dataset in JSON format (20 records)
- `dataset/bug_dataset.csv` — Same data in CSV format for spreadsheet analysis
- `dataset/bug_reports/B001.md`–`B020.md` — Individual natural-language bug reports
- `tests/reproduction_tests/test_B001.py`–`test_B020.py` — Automated reproduction tests
- `scripts/validate_dataset.py` — Integrity validator

## Design Principles

- Every bug is **syntactically valid** (no parse errors)
- Every bug is **independently reproducible** where possible
- Root cause is always **one minimal change** from the correct code
- Issue reports describe **symptoms**, not root causes
- Bug IDs are **interleaved** across layers to prevent positional bias
- No comments, function names, or variable names reveal the bug location

## Disclaimer

This is a controlled research dataset for initial experimentation. It is not scientifically
representative of real-world software bug distributions.
