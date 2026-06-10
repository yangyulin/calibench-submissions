#!/usr/bin/env python3
"""Publish result.json(s) to the calibench-vi/results dataset.

Usage: HF_TOKEN=... python scripts/publish.py [result.json ...]
Needs a Hugging Face token with WRITE access to the calibench-vi org.
"""
import os
import pathlib
import sys

from huggingface_hub import HfApi

REPO = "calibench-vi/results"


def main(files):
    token = os.environ.get("HF_TOKEN")
    if not token:
        sys.exit("HF_TOKEN not set (add it as a GitHub Actions secret)")
    api = HfApi(token=token)
    files = files or ["result.json"]
    for f in files:
        name = pathlib.Path(f).name
        api.upload_file(path_or_fileobj=f, path_in_repo=name,
                        repo_id=REPO, repo_type="dataset",
                        commit_message=f"add leaderboard result {name}")
        print(f"  published {name} -> {REPO}")


if __name__ == "__main__":
    main(sys.argv[1:])
