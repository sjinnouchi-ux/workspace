import datetime
import platform
import sys

print("=" * 40)
print("GitHub MCP 連携テスト")
print("=" * 40)
print(f"実行日時: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Python: {sys.version}")
print(f"OS: {platform.system()} {platform.release()}")
print("=" * 40)
print("✅ Cowork → GitHub MCP → CLI 連携成功！")
print("=" * 40)
