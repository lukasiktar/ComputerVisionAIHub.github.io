#!/usr/bin/env python3
"""
Validate docs/models.json.

Run locally before committing:
    python scripts/validate_models.py              # schema only
    python scripts/validate_models.py --check-links  # also verify download URLs resolve

Exit code is non-zero if any ERROR is found, so CI can block the merge.
Uses only the Python standard library (no pip install needed).
"""
import argparse
import json
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

MANIFEST = Path(__file__).resolve().parents[1] / "docs" / "models.json"

REQUIRED_STR = ["id", "name", "base_model", "task", "download"]
KNOWN_TASKS = {"detection", "segmentation", "classification", "pose", "obb"}
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")  # lowercase slug, e.g. traffic-signs-v1

errors = []
warnings = []


def err(model_id, msg):
    errors.append(f"[{model_id}] {msg}")


def warn(model_id, msg):
    warnings.append(f"[{model_id}] {msg}")


def is_https(u):
    return isinstance(u, str) and u.startswith("https://")


def url_ok(url):
    """Return (ok, detail). 404 -> hard fail; network/timeout -> soft (None)."""
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=20) as resp:
            return (200 <= resp.status < 400, f"HTTP {resp.status}")
    except urllib.error.HTTPError as e:
        if e.code in (403, 405):  # some hosts reject HEAD; treat as inconclusive
            return (None, f"HTTP {e.code} (HEAD not allowed)")
        return (False, f"HTTP {e.code}")
    except Exception as e:  # noqa: BLE001 - network issues shouldn't hard-fail CI
        return (None, f"unreachable: {e}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-links", action="store_true", help="verify download/onnx URLs resolve")
    args = ap.parse_args()

    # 1. file loads as JSON
    try:
        data = json.loads(MANIFEST.read_text())
    except FileNotFoundError:
        print(f"ERROR: {MANIFEST} not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: models.json is not valid JSON: {e}")
        sys.exit(1)

    models = data.get("models")
    if not isinstance(models, list):
        print('ERROR: top-level "models" must be a list')
        sys.exit(1)

    seen_ids = set()

    for i, m in enumerate(models):
        mid = m.get("id", f"#{i}")

        if not isinstance(m, dict):
            err(mid, "entry is not an object")
            continue

        # required string fields
        for f in REQUIRED_STR:
            if not isinstance(m.get(f), str) or not m[f].strip():
                err(mid, f'missing or empty required field "{f}"')

        # id format + uniqueness
        if isinstance(m.get("id"), str):
            if not ID_RE.match(m["id"]):
                err(mid, 'id must be a lowercase slug (a-z, 0-9, hyphens)')
            if m["id"] in seen_ids:
                err(mid, "duplicate id")
            seen_ids.add(m["id"])

        # task
        if m.get("task") not in KNOWN_TASKS:
            warn(mid, f'unusual task "{m.get("task")}" (known: {sorted(KNOWN_TASKS)})')

        # classes
        if not isinstance(m.get("classes"), list) or not m["classes"]:
            err(mid, '"classes" must be a non-empty list')

        # metrics in range
        metrics = m.get("metrics", {})
        if metrics:
            for k in ("mAP50", "mAP50_95"):
                v = metrics.get(k)
                if v is not None and not (isinstance(v, (int, float)) and 0 <= v <= 1):
                    err(mid, f'metrics.{k} must be a number between 0 and 1')

        # URLs are https
        for f in ("download", "onnx", "dataset"):
            if m.get(f) and not is_https(m[f]):
                err(mid, f'"{f}" must be an https URL')

        # dataset license present (warn only)
        if not m.get("dataset_license"):
            warn(mid, "no dataset_license set — users won't know usage terms")

        # optional link check
        if args.check_links:
            for f in ("download", "onnx"):
                if is_https(m.get(f, "")):
                    ok, detail = url_ok(m[f])
                    if ok is False:
                        err(mid, f'{f} link broken ({detail}): {m[f]}')
                    elif ok is None:
                        warn(mid, f'{f} link not verified ({detail})')

    # report
    for w in warnings:
        print(f"WARNING {w}")
    for e in errors:
        print(f"ERROR   {e}")

    n = len(models)
    if errors:
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s) across {n} model(s). FAILED.")
        sys.exit(1)
    print(f"\nOK: {n} model(s) valid, {len(warnings)} warning(s).")


if __name__ == "__main__":
    main()