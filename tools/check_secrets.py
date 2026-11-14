"""commit 前的金鑰檢查。找到任何一個就回傳 exit 1。

用法：
    python tools/check_secrets.py <私人資料夾>

<私人資料夾> 是有 data/.env 和 data/solge.db 的那個（例如 Desktop\\SolGeGoodShxt）。
它會拿裡面「真的」金鑰、LINE user id、網頁 token，逐一比對這個 repo 的每個檔案，
再加上常見金鑰格式的比對。只印出「在哪個檔案找到哪一種」，不印出金鑰本身。
"""
import re
import sqlite3
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PATTERNS = {
    "github_token": r"(ghp_|gho_|ghu_|ghs_|github_pat_)[A-Za-z0-9_]{20,}",
    "line_user_id": r"\bU[0-9a-f]{32}\b",
    "aws_key": r"AKIA[0-9A-Z]{16}",
    "private_key": r"-----BEGIN [A-Z ]*PRIVATE KEY",
    "assigned_secret": r"(?i)(secret|token|password|api_key)[ \t]*[=:][ \t]*[\"']?[A-Za-z0-9/+_\-]{16,}",
}


def real_secrets(private: Path) -> dict:
    found = {}
    env = private / "data" / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^\s*([A-Z_]+)\s*=\s*(.+)$", line)
            if m and m.group(1) != "PORT":
                for i, v in enumerate(m.group(2).strip().strip("\"'").split(",")):
                    if len(v.strip()) >= 8:
                        found[f"{m.group(1)}#{i}"] = v.strip()
    db = private / "data" / "solge.db"
    if db.exists():
        conn = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
        for uid, tok in conn.execute("SELECT line_user_id, web_token FROM users"):
            found[f"line_user_id:{uid[:3]}"] = uid
            found[f"web_token:{uid[:3]}"] = tok
    return found


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    secrets = real_secrets(Path(sys.argv[1]))
    if not secrets:
        sys.exit("找不到私人資料夾的 data/.env 或 solge.db，路徑對嗎？")
    hits = 0
    files = [f for f in REPO.rglob("*") if f.is_file() and ".git" not in f.parts]
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        rel = f.relative_to(REPO)
        for name, value in secrets.items():
            if value in text:
                print(f"LEAK  {name}  in {rel}")
                hits += 1
        for name, pat in PATTERNS.items():
            if re.search(pat, text):
                print(f"FORMAT  {name}  in {rel}")
                hits += 1
    print(f"比對 {len(secrets)} 個真金鑰、{len(files)} 個檔案，找到 {hits} 個")
    sys.exit(1 if hits else 0)


if __name__ == "__main__":
    main()
