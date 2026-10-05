#!/usr/bin/env python3
"""Validate the ShopBug bug dataset for completeness and consistency."""
import csv
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_JSON = os.path.join(BASE_DIR, "dataset", "bug_dataset.json")
DATASET_CSV = os.path.join(BASE_DIR, "dataset", "bug_dataset.csv")


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
    print("PASS: All bug IDs are unique")
    return True


def check_required_fields(records):
    required = ["issue_report", "category", "difficulty", "root_cause_file", "root_cause_function"]
    ok = True
    for r in records:
        for field in required:
            val = r.get(field, "")
            if isinstance(val, list):
                val = " ".join(str(v) for v in val)
            if not str(val).strip():
                print(f"FAIL: {r['bug_id']} has empty {field}")
                ok = False
    if ok:
        print("PASS: All required fields are non-empty")
    return ok


def check_root_cause_files_exist(records):
    ok = True
    for r in records:
        path = os.path.join(BASE_DIR, r["root_cause_file"])
        if not os.path.exists(path):
            print(f"FAIL: {r['bug_id']} root_cause_file does not exist: {r['root_cause_file']}")
            ok = False
    if ok:
        print("PASS: All root_cause_files exist on disk")
    return ok


def check_reproduction_tests_exist(records):
    ok = True
    for r in records:
        path = os.path.join(BASE_DIR, r["reproduction_test"])
        if not os.path.exists(path):
            print(f"FAIL: {r['bug_id']} reproduction_test does not exist: {r['reproduction_test']}")
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
            print(f"FAIL: IDs in JSON but not CSV: {missing_in_csv}")
        if missing_in_json:
            print(f"FAIL: IDs in CSV but not JSON: {missing_in_json}")
        return False
    print("PASS: JSON and CSV contain the same bug IDs")
    return True


def main():
    if not os.path.exists(DATASET_JSON):
        print(f"FAIL: {DATASET_JSON} not found")
        sys.exit(1)
    if not os.path.exists(DATASET_CSV):
        print(f"FAIL: {DATASET_CSV} not found")
        sys.exit(1)

    print(f"Loading {DATASET_JSON}...")
    json_records = load_json()
    print(f"  {len(json_records)} records loaded")

    print(f"Loading {DATASET_CSV}...")
    csv_records = load_csv()
    print(f"  {len(csv_records)} records loaded")

    print()
    all_ok = True
    all_ok &= check_unique_ids(json_records)
    all_ok &= check_required_fields(json_records)
    all_ok &= check_root_cause_files_exist(json_records)
    all_ok &= check_reproduction_tests_exist(json_records)
    all_ok &= check_json_csv_match(json_records, csv_records)

    print()
    if all_ok:
        print(f"All validation checks passed ({len(json_records)} bugs).")
        sys.exit(0)
    else:
        print("Validation FAILED — see errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
