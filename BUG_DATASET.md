# ShopBug Bug Dataset — Summary

> **IMPORTANT**: This file and the accompanying `dataset/` directory are **evaluation-only metadata**. They must NOT be included in the repository ingestion pipeline when evaluating an AI bug-localization system. The future AI application should receive only the repository source code and natural-language issue reports.

## Overview

The ShopBug bug dataset contains **20 intentional software bugs** injected into a controlled e-commerce backend. Each bug is designed to be syntactically valid but behaviorally incorrect, and is accompanied by a reproduction test, ground-truth localization data, and a natural-language issue report.

## Schema

Each bug record contains the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `bug_id` | string | Unique identifier (B001–B020) |
| `category` | string | Bug category (see distribution below) |
| `difficulty` | string | easy, medium, or hard |
| `issue_report_quality` | string | specific, moderate, or vague |
| `issue_report` | string | Natural-language user observation |
| `expected_behavior` | string | What should happen |
| `actual_behavior` | string | What actually happens due to the bug |
| `root_cause_file` | string | File containing the incorrect logic |
| `root_cause_function` | string | Function containing the incorrect logic |
| `root_cause_lines` | array[int] | Line numbers of the buggy code |
| `affected_files` | array[string] | All files whose behavior is affected |
| `root_cause_description` | string | Technical description of the root cause |
| `reproduction_steps` | array[string] | Steps to reproduce the bug |
| `reproduction_test` | string | Path to the reproduction test file |
| `commit_hash` | string | Git commit hash of the buggy version |
| `scope` | string | single-file or multi-file |

## Distribution

### By Category (10 categories)

| Category | Count | Bug IDs |
|----------|-------|---------|
| arithmetic | 3 | B001, B002, B009 |
| logic | 4 | B003, B010, B014, B020 |
| boundary | 3 | B004, B008, B018 |
| input_validation | 2 | B005, B015 |
| search_filter | 2 | B006, B017 |
| data_handling | 2 | B007, B016 |
| dependency | 1 | B012 |
| authentication | 1 | B011 |
| multi_interaction | 1 | B019 |
| edge_case | 1 | B013 |

### By Difficulty

| Difficulty | Count |
|------------|-------|
| easy | 6 |
| medium | 8 |
| hard | 6 |

### By Issue Report Quality

| Quality | Count |
|---------|-------|
| specific | 7 |
| moderate | 7 |
| vague | 6 |

### By Scope

| Scope | Count |
|-------|-------|
| single-file | 14 |
| multi-file | 6 |

## How to Use

1. **Repository ingestion**: Provide only the source code (`app/` directory) and the issue report to the AI system being evaluated. Exclude `dataset/`, `BUG_DATASET.md`, and `scripts/validate_dataset.py`.

2. **Evaluation**: Compare the AI system's predicted buggy file/function against the `root_cause_file` and `root_cause_function` fields in `dataset/bug_dataset.json`.

3. **Reproduction**: Run `pytest tests/reproduction_tests/ -v` to confirm all 20 bugs are active (all tests should fail).

4. **Validation**: Run `python scripts/validate_dataset.py` to verify dataset integrity.

## Files

- `dataset/bug_dataset.json` — Full dataset in JSON format
- `dataset/bug_dataset.csv` — Same data in CSV format
- `dataset/bug_reports/B001.md`–`B020.md` — Individual bug reports
- `tests/reproduction_tests/test_B001.py`–`test_B020.py` — Reproduction tests

## Disclaimer

This is a controlled research dataset for initial experimentation. It is not scientifically representative of real-world software or real-world bug distributions.
