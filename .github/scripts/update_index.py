#!/usr/bin/env python3
"""INDEX.json の last_updated を自動更新するスクリプト。

GitHub Actions の push トリガーから呼ばれる。
直前 commit (HEAD^) と現在 (HEAD) の差分ファイルを見て、
変更されたプロジェクトの last_updated を本日に書き換える。
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
INDEX_PATH = REPO_ROOT / "INDEX.json"

# トップレベルディレクトリ -> INDEX.json の projects キー
DIR_TO_PROJECT = {
    "dori-manga": "dori-manga",
    "code-exchange": "code-exchange",
    "codex": "codex",
    "k-alert-test": "k-alert-test",
    "api-monitor": "api-monitor",
    "company-settings": "company-settings",
    "taiwan-outreach": "taiwan-outreach",
    "yumekango-worker": "yumekango-worker",
}


def changed_files() -> list[str]:
    """直前 commit と現在の差分ファイル一覧を返す。"""
    try:
        out = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD^", "HEAD"],
            text=True,
            cwd=REPO_ROOT,
        )
    except subprocess.CalledProcessError as exc:
        print(f"git diff failed: {exc}", file=sys.stderr)
        return []
    return [line.strip() for line in out.splitlines() if line.strip()]


def main() -> int:
    files = changed_files()
    print(f"Changed files: {files}")

    affected: set[str] = set()
    for f in files:
        top = f.split("/", 1)[0]
        if top in DIR_TO_PROJECT:
            affected.add(DIR_TO_PROJECT[top])

    if not affected:
        print("No project-scoped change. Skip INDEX.json update.")
        return 0

    today = date.today().isoformat()

    with INDEX_PATH.open(encoding="utf-8") as fp:
        index = json.load(fp)

    for project in sorted(affected):
        if project in index["projects"]:
            old = index["projects"][project].get("last_updated")
            index["projects"][project]["last_updated"] = today
            print(f"  {project}: {old} -> {today}")
        else:
            print(f"  WARN: project '{project}' not found in INDEX.json")

    index["generated"] = today

    with INDEX_PATH.open("w", encoding="utf-8") as fp:
        json.dump(index, fp, ensure_ascii=False, indent=2)
        fp.write("\n")

    print("INDEX.json updated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
