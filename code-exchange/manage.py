#!/usr/bin/env python3
"""
code-exchange 管理スクリプト

使い方:
  python manage.py list                    # 実行待ち一覧表示
  python manage.py new "タスク名"          # 新しいやり取りを作成
  python manage.py complete <id>           # 完成報告（JSONを削除してpush）
  python manage.py show <id>               # 指定IDの内容を表示
"""

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

EXCHANGES_DIR = Path(__file__).parent / "exchanges"


def today_prefix() -> str:
    return date.today().strftime("%Y%m%d")


def next_id() -> str:
    prefix = today_prefix()
    existing = [
        f.stem for f in EXCHANGES_DIR.glob(f"{prefix}-*.json")
    ]
    if not existing:
        return f"{prefix}-001"
    nums = [int(s.split("-")[1]) for s in existing if re.match(r"\d{8}-\d{3}", s)]
    nxt = max(nums) + 1 if nums else 1
    return f"{prefix}-{nxt:03d}"


def cmd_list():
    jsons = sorted(EXCHANGES_DIR.glob("*.json"))
    if not jsons:
        print("実行待ちのコードはありません。")
        return
    print(f"{'ID':<18} {'タイトル':<30} {'作成日'}")
    print("-" * 65)
    for jf in jsons:
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
            print(f"{data['id']:<18} {data['title'][:28]:<30} {data['created']}")
        except Exception:
            print(f"{jf.stem:<18} (読み込みエラー)")


def cmd_new(title: str):
    eid = next_id()
    md_path = EXCHANGES_DIR / f"{eid}.md"
    json_path = EXCHANGES_DIR / f"{eid}.json"

    template = (EXCHANGES_DIR / "template.md").read_text(encoding="utf-8")
    content = template.replace("[タスクタイトル]", title)
    md_path.write_text(content, encoding="utf-8")

    meta = {
        "id": eid,
        "title": title,
        "status": "pending",
        "created": today_prefix(),
        "md_file": md_path.name,
    }
    json_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"作成しました: {eid}")
    print(f"  md  : exchanges/{md_path.name}")
    print(f"  json: exchanges/{json_path.name}")
    print(f"\nコードを記入後、git add/commit/push してください。")


def cmd_complete(eid: str):
    json_path = EXCHANGES_DIR / f"{eid}.json"
    if not json_path.exists():
        print(f"エラー: {eid}.json が見つかりません（すでに完了済みか、IDを確認してください）")
        sys.exit(1)

    data = json.loads(json_path.read_text(encoding="utf-8"))
    title = data.get("title", "")

    json_path.unlink()
    print(f"完了: {eid} ({title}) のJSONを削除しました。")

    _git_push(f"complete: {eid} ({title})")


def cmd_show(eid: str):
    md_path = EXCHANGES_DIR / f"{eid}.md"
    if not md_path.exists():
        print(f"エラー: {eid}.md が見つかりません")
        sys.exit(1)
    print(md_path.read_text(encoding="utf-8"))


def _git_push(message: str):
    root = Path(__file__).parent
    try:
        subprocess.run(["git", "add", "-A"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", message], cwd=root, check=True)
        subprocess.run(["git", "push"], cwd=root, check=True)
        print("GitHubにpushしました。")
    except subprocess.CalledProcessError as e:
        print(f"git操作でエラーが発生しました: {e}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "list":
        cmd_list()
    elif cmd == "new":
        if len(sys.argv) < 3:
            print("使い方: python manage.py new \"タスク名\"")
            sys.exit(1)
        cmd_new(sys.argv[2])
    elif cmd == "complete":
        if len(sys.argv) < 3:
            print("使い方: python manage.py complete <id>")
            sys.exit(1)
        cmd_complete(sys.argv[3] if len(sys.argv) > 3 else sys.argv[2])
    elif cmd == "show":
        if len(sys.argv) < 3:
            print("使い方: python manage.py show <id>")
            sys.exit(1)
        cmd_show(sys.argv[2])
    else:
        print(f"不明なコマンド: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
