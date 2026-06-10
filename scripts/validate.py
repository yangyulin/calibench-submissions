#!/usr/bin/env python3
"""Validate submission.json files against the Calibench submission schema.

Usage: python scripts/validate.py [submission.json ...]
With no args, validates every submissions/**/submission.json.
"""
import glob
import json
import pathlib
import sys

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = pathlib.Path(__file__).resolve().parent.parent
sub = json.loads((ROOT / "schemas/submission.schema.json").read_text())
res = json.loads((ROOT / "schemas/result.schema.json").read_text())
registry = Registry().with_resources([
    (sub["$id"], Resource.from_contents(sub)),
    (res["$id"], Resource.from_contents(res)),
])
validator = Draft202012Validator(sub, registry=registry)


def main(paths):
    paths = paths or glob.glob(str(ROOT / "submissions/**/submission.json"), recursive=True)
    fail = 0
    for p in paths:
        try:
            data = json.loads(pathlib.Path(p).read_text())
            validator.validate(data)
            cal = data.get("calibration")
            if isinstance(cal, str):
                calp = pathlib.Path(p).parent / cal
                if not calp.exists():
                    raise FileNotFoundError(f"calibration output '{cal}' not found next to submission")
            print(f"  OK   {p}")
        except Exception as e:
            print(f"  FAIL {p}: {e}")
            fail += 1
    if fail:
        sys.exit(f"\n{fail} submission(s) failed validation")
    print(f"\n{len(paths)} submission(s) valid")


if __name__ == "__main__":
    main(sys.argv[1:])
