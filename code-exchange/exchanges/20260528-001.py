"""20260528-001: api-monitor Phase 1〜2 セットアップ＆DB初期化スクリプト.

実行内容:
  1. requirements.txt をインストール (pip --break-system-packages)
  2. .env が無ければ .env.example をコピー
  3. SQLite DB を初期化 (api_call_logs / api_keys / api_settings)
  4. 主要モジュールの py_compile チェック

このスクリプトはCLI側で実行する想定。
"""

from __future__ import annotations

import compileall
import os
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]   # ~/sjinnouchi-ux-workspace
PROJECT   = REPO_ROOT / "api-monitor"


def step(title: str) -> None:
    print(f"\n=== {title} ===")


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)


def install_requirements() -> None:
    step("1. pip install -r requirements.txt --break-system-packages")
    req = PROJECT / "requirements.txt"
    if not req.exists():
        raise FileNotFoundError(req)
    run([sys.executable, "-m", "pip", "install", "-r", str(req), "--break-system-packages"])


def ensure_env_file() -> None:
    step("2. .env を準備")
    env_path     = PROJECT / ".env"
    env_template = PROJECT / ".env.example"
    if env_path.exists():
        print(f"スキップ: {env_path} は既に存在します。")
        return
    if not env_template.exists():
        raise FileNotFoundError(env_template)
    shutil.copy2(env_template, env_path)
    print(f"作成: {env_path}（APIキーは陣内さんが後で記入）")


def init_database() -> None:
    step("3. SQLite DB 初期化")
    sys.path.insert(0, str(PROJECT))
    try:
        import db  # api-monitor/db.py
    finally:
        # do not pollute later imports
        pass
    db.init_db()
    print(f"DB 初期化完了: {db.get_db_path()}")


def syntax_check() -> None:
    step("4. py_compile による構文チェック")
    targets = [
        PROJECT / "app.py",
        PROJECT / "db.py",
        PROJECT / "monitor.py",
        PROJECT / "settings.py",
        PROJECT / "api_clients" / "__init__.py",
        PROJECT / "api_clients" / "openai_client.py",
        PROJECT / "api_clients" / "claude_client.py",
        PROJECT / "api_clients" / "gemini_client.py",
    ]
    all_ok = True
    for path in targets:
        ok = compileall.compile_file(str(path), quiet=1, force=True)
        mark = "OK" if ok else "NG"
        print(f"  [{mark}] {path.relative_to(REPO_ROOT)}")
        all_ok = all_ok and bool(ok)
    if not all_ok:
        raise RuntimeError("構文エラーがあります。上の [NG] を確認してください。")


def main() -> None:
    print(f"REPO_ROOT = {REPO_ROOT}")
    print(f"PROJECT   = {PROJECT}")

    install_requirements()
    ensure_env_file()
    init_database()
    syntax_check()

    print("\n========================================")
    print("セットアップ完了")
    print("========================================")
    print("次の手順:")
    print(f"  1) nano {PROJECT / '.env'}  でAPIキーを記入")
    print(f"  2) cd {PROJECT} && streamlit run app.py")
    print( "  3) ブラウザで http://localhost:8501 を開く")


if __name__ == "__main__":
    main()
