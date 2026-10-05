# ShopBug Dataset

> **EVALUATION-ONLY**: This directory contains ground-truth metadata for research evaluation. It must NOT be provided to the AI bug-localization system being evaluated.

## Purpose

This dataset provides a rigorous, reproducible ground truth for evaluating AI-based software bug localization systems. Each of the 20 bugs has a known root-cause location, affected files, a natural-language issue report, and an automated reproduction test.

## Contents

| File | Description |
|------|-------------|
| `bug_dataset.json` | Complete dataset in JSON format (20 records) |
| `bug_dataset.csv` | Same data in CSV format for spreadsheet analysis |
| `bug_reports/B001.md`–`B020.md` | Individual bug report files |

## Dataset Statistics

- **Total bugs**: 20
- **Categories**: 10 (arithmetic, logic, boundary, input_validation, search_filter, data_handling, dependency, authentication, multi_interaction, edge_case)
- **Difficulty**: 6 easy, 8 medium, 6 hard
- **Issue report quality**: 7 specific, 7 moderate, 6 vague
- **Scope**: 14 single-file, 6 multi-file

## How Bugs Are Reproduced

Each bug has a corresponding reproduction test at `tests/reproduction_tests/test_B{NNN}.py`. These tests assert the **expected (correct)** behavior. On the buggy codebase, they **fail**, confirming the bug is active.

```bash
pytest tests/reproduction_tests/ -v
```

All 20 tests should fail on the buggy version and pass on the corrected version.

## How Ground Truth Is Defined

For each bug, the **root-cause location** is the exact file and function where the incorrect logic resides. The **affected files** are other files whose behavior is impacted by the bug (but do not contain the root cause).

Evaluation should primarily use the **root-cause location** as the ground truth.

## How to Use for Evaluation

1. Provide the AI system with:
   - The repository source code (excluding this `dataset/` directory, `BUG_DATASET.md`, and `scripts/`)
   - A natural-language issue report from `bug_reports/`

2. The AI system predicts the most likely buggy file and function.

3. Compare the prediction against `root_cause_file` and `root_cause_function` in `bug_dataset.json`.

4. Metrics: file-level accuracy, function-level accuracy, top-k accuracy.

## Disclaimer

This is a controlled research dataset for initial experimentation and evaluation. It is not scientifically representative of real-world software or real-world bug distributions.
