"""把 solge.db 的公開內容匯出成 docs/data.json，給 GitHub Pages 用。

用法：
    python tools/export_pages.py <solge.db 路徑>

只匯出白名單欄位：
- repos：公開 GitHub repo 的白話分析（不含 README 原文、不含 embedding）
- alchemy：A+B 煉金點子（不含 user_id）
users / jobs / items / notes 一律不匯出（有 LINE user id、網頁 token、聊天內容）。
"""
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_COLS = [
    "full_name", "html_url", "description", "stars", "license", "language",
    "topics", "summary", "audience", "use_cases", "mermaid", "analyzed_at",
]
ALCHEMY_COLS = ["full_names", "title", "pitch", "audience", "how", "mermaid", "prd_md", "created_at"]
JSON_COLS = {"topics", "use_cases", "full_names"}


def load(v, col):
    if col in JSON_COLS and isinstance(v, str):
        try:
            return json.loads(v)
        except json.JSONDecodeError:
            return v
    return v


def rows(conn, table, cols, order):
    sql = f"SELECT {', '.join(cols)} FROM {table} ORDER BY {order}"
    return [{c: load(r[c], c) for c in cols} for r in conn.execute(sql)]


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    db = Path(sys.argv[1]).resolve()
    conn = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    data = {
        "exported_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repos": rows(conn, "repos", REPO_COLS, "analyzed_at DESC"),
        "alchemy": rows(conn, "alchemy", ALCHEMY_COLS, "created_at DESC"),
    }
    out = Path(__file__).resolve().parent.parent / "docs" / "data.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(data['repos'])} repos, {len(data['alchemy'])} alchemy -> {out}")


if __name__ == "__main__":
    main()
