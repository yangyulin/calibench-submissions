#!/usr/bin/env python3
"""Re-run the Calibench evaluation on a submission's calibration OUTPUTS and emit result.json.

Usage: python scripts/evaluate.py submissions/<tool>-<config>/submission.json

STATUS — scaffold. `run_eval()` (the actual metric computation by the CamCalib
evaluation harness) is the remaining M3 wiring. Until it's implemented this passes
the submission through as a SELF-REPORTED row (empty CI metrics) so the pipeline is
testable end-to-end; the leaderboard labels such rows as not verified.
"""
import datetime
import hashlib
import json
import pathlib
import sys


def run_eval(submission, calib_path):
    """TODO(M3): compute metrics by re-running the Calibench evaluation harness.

    - install CamCalib (pip/git) and load the calibration output at `calib_path`
    - split == 'simulation': score vs the PRIVATE held-out ground truth
      (a repo secret / private source) -> returns metrics.simulation + verified
    - split == 'real': GT-free metrics (reprojection / IMU residual / cross-tool
      agreement vs the baseline set) -> returns metrics.real
    Returns (metrics: dict | None, verified: bool). None -> not evaluated yet.
    """
    return None, False


def build_result(submission, metrics, verified):
    s = submission
    split = s["dataset"]["split"]
    sid = hashlib.sha1(json.dumps(s, sort_keys=True).encode()).hexdigest()[:7]
    if metrics is None:
        status, note, metrics = "self_reported", \
            "CI re-run-eval not wired yet (M3) — published as self-reported.", {}
    else:
        status = "verified" if verified else "self_reported"
        note = ""
    return {
        "schema_version": "1.0",
        "id": f"{s['tool']['name']}-{s['dataset']['config']}-{s.get('date', 'NA')}-{sid}".lower().replace(" ", ""),
        "tool": s["tool"],
        "dataset": s["dataset"],
        "submitter": s["submitter"],
        "verification": {"status": status, "method": "re-run-eval", "notes": note},
        "metrics": {split: metrics},
        "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def main(sub_path):
    s = json.loads(pathlib.Path(sub_path).read_text())
    cal = s.get("calibration")
    calp = pathlib.Path(sub_path).parent / cal if isinstance(cal, str) else None
    metrics, verified = run_eval(s, calp)
    result = build_result(s, metrics, verified)
    pathlib.Path("result.json").write_text(json.dumps(result, indent=2))
    print(f"  wrote result.json  id={result['id']}  status={result['verification']['status']}")


if __name__ == "__main__":
    main(sys.argv[1])
