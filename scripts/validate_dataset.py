#!/usr/bin/env python3
"""
Validate the ShopBug bug dataset for completeness and consistency.

Checks:
  1. All bug IDs are unique.
  2. Every required field is non-empty.
  3. Every root_cause_file exists on disk.
  4. Every reproduction_test file exists on disk.
  5. JSON and CSV contain the same set of bug IDs.
  6. Every layer value is one of: frontend / backend / database / integration.
  7. Every issue_type value is one of: user / developer.
  8. Every difficulty value is one of: easy / medium / hard.
  9. Every scope value is one of: single-file / multi-file.
 10. root_cause_lines is a non-empty list of integers (JSON only).
"""
import csv
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_JSON = os.path.join(BASE_DIR, "dataset", "bug_dataset.json")
DATASET_CSV = os.path.join(BASE_DIR, "dataset", "bug_dataset.csv")

VALID_LAYERS = {"frontend", "backend", "database", "integration"}
VALID_ISSUE_TYPES = {"user", "developer"}
VALID_DIFFICULTIES = {"easy", "medium", "hard"}
VALID_QUALITIES = {"specific", "moderate", "vague"}
VALID_SCOPES = {"single-file", "multi-file"}


def load_json():
    with open(DATASET_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def load_csv():
    records = []
    with open(DATASET_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    return records


def check_unique_ids(records):
    ids = [r["bug_id"] for r in records]
    duplicates = [i for i in ids if ids.count(i) > 1]
    if duplicates:
        print(f"FAIL: Duplicate bug IDs: {set(duplicates)}")
        return False
    print(f"PASS: All {len(ids)} bug IDs are unique")
    return True


def check_required_fields(records):
    required = [
        "bug_id", "category", "layer", "difficulty", "issue_report_quality",
        "issue_type", "issue_report", "expected_behavior", "actual_behavior",
        "root_cause_file", "root_cause_function",
    ]
    ok = True
    for r in records:
        for field in required:
            val = r.get(field, "")
            if isinstance(val, list):
                val = " ".join(str(v) for v in val)
            if not str(val).strip():
                print(f"FAIL: {r['bug_id']} has empty required field '{field}'")
                ok = False
    if ok:
        print("PASS: All required fields are non-empty")
    return ok


def check_enum_fields(records):
    ok = True
    for r in records:
        bid = r["bug_id"]
        if r.get("layer") not in VALID_LAYERS:
            print(f"FAIL: {bid} layer='{r.get('layer')}' not in {VALID_LAYERS}")
            ok = False
        if r.get("issue_type") not in VALID_ISSUE_TYPES:
            print(f"FAIL: {bid} issue_type='{r.get('issue_type')}' not in {VALID_ISSUE_TYPES}")
            ok = False
        if r.get("difficulty") not in VALID_DIFFICULTIES:
            print(f"FAIL: {bid} difficulty='{r.get('difficulty')}' not in {VALID_DIFFICULTIES}")
            ok = False
        if r.get("issue_report_quality") not in VALID_QUALITIES:
            print(f"FAIL: {bid} issue_report_quality='{r.get('issue_report_quality')}' not in {VALID_QUALITIES}")
            ok = False
        if r.get("scope") not in VALID_SCOPES:
            print(f"FAIL: {bid} scope='{r.get('scope')}' not in {VALID_SCOPES}")
            ok = False
    if ok:
        print("PASS: All enum fields have valid values")
    return ok


def check_root_cause_files_exist(records):
    ok = True
    for r in records:
        path = os.path.join(BASE_DIR, r["root_cause_file"])
        if not os.path.exists(path):
            print(f"FAIL: {r['bug_id']} root_cause_file not found: {r['root_cause_file']}")
            ok = False
    if ok:
        print("PASS: All root_cause_files exist on disk")
    return ok


def check_reproduction_tests_exist(records):
    ok = True
    for r in records:
        path = os.path.join(BASE_DIR, r["reproduction_test"])
        if not os.path.exists(path):
            print(f"FAIL: {r['bug_id']} reproduction_test not found: {r['reproduction_test']}")
            ok = False
    if ok:
        print("PASS: All reproduction_test files exist on disk")
    return ok


def check_json_csv_match(json_records, csv_records):
    json_ids = set(r["bug_id"] for r in json_records)
    csv_ids = set(r["bug_id"] for r in csv_records)
    if json_ids != csv_ids:
        missing_in_csv = json_ids - csv_ids
        missing_in_json = csv_ids - json_ids
        if missing_in_csv:
            print(f"FAIL: IDs in JSON but not in CSV: {sorted(missing_in_csv)}")
        if missing_in_json:
            print(f"FAIL: IDs in CSV but not in JSON: {sorted(missing_in_json)}")
        return False
    print(f"PASS: JSON and CSV both contain the same {len(json_ids)} bug IDs")
    return True


def check_root_cause_lines(records):
    """JSON-only: root_cause_lines must be a non-empty list of integers."""
    ok = True
    for r in records:
        lines = r.get("root_cause_lines")
        if not isinstance(lines, list) or len(lines) == 0:
            print(f"FAIL: {r['bug_id']} root_cause_lines must be a non-empty list, got: {lines!r}")
            ok = False
        elif not all(isinstance(ln, int) for ln in lines):
            print(f"FAIL: {r['bug_id']} root_cause_lines must contain only integers, got: {lines}")
            ok = False
    if ok:
        print("PASS: All root_cause_lines are non-empty integer lists")
    return ok


def check_affected_files(records):
    """JSON-only: affected_files must be a non-empty list and include root_cause_file."""
    ok = True
    for r in records:
        af = r.get("affected_files", [])
        rcf = r.get("root_cause_file", "")
        if not isinstance(af, list) or len(af) == 0:
            print(f"FAIL: {r['bug_id']} affected_files must be a non-empty list")
            ok = False
        elif rcf not in af:
            print(f"FAIL: {r['bug_id']} root_cause_file '{rcf}' not in affected_files {af}")
            ok = False
    if ok:
        print("PASS: All affected_files are valid and include root_cause_file")
    return ok


def main():
    for path, label in [(DATASET_JSON, "JSON"), (DATASET_CSV, "CSV")]:
        if not os.path.exists(path):
            print(f"FAIL: {label} file not found: {path}")
            sys.exit(1)

    print(f"Loading {DATASET_JSON}...")
    json_records = load_json()
    print(f"  {len(json_records)} records loaded")

    print(f"Loading {DATASET_CSV}...")
    csv_records = load_csv()
    print(f"  {len(csv_records)} records loaded")

    print()
    results = [
        check_unique_ids(json_records),
        check_required_fields(json_records),
        check_enum_fields(json_records),
        check_root_cause_files_exist(json_records),
        check_reproduction_tests_exist(json_records),
        check_json_csv_match(json_records, csv_records),
        check_root_cause_lines(json_records),
        check_affected_files(json_records),
    ]

    print()
    total = len(json_records)
    passed = sum(results)
    failed = len(results) - passed

    if all(results):
        print(f"All {len(results)} validation checks passed ({total} bugs).")
        sys.exit(0)
    else:
        print(f"{failed} check(s) FAILED — see errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
