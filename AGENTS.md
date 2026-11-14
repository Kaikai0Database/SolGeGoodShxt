# AGENTS.md：給 AI 的工作規則

這個 repo 只放 SolGeGoodShxt 的「模式與想法」和一個公開知識庫網頁。
真正的程式、金鑰、資料庫在作者電腦的另一個私人資料夾，**永遠不進這個 repo**。

## 1. 這個 repo 有什麼

```text
README.md               想法、流程、設計（給人看）
AGENTS.md / CLAUDE.md   這份規則（給 AI 看）
docs/                   GitHub Pages 網站，網址固定：https://kaikai0database.github.io/SolGeGoodShxt/
  index.html            首頁：repo 卡片、搜尋、煉金點子
  style.css             全站共用樣式（顏色、卡片、深色模式）
  data.json             由 export_pages.py 產生，不要手改
  .nojekyll             讓 GitHub 直接送出檔案，不要刪
tools/
  export_pages.py       私人 solge.db → docs/data.json（白名單匯出）
  check_secrets.py      commit 前的金鑰檢查
```

沒有建置步驟。網站是純 HTML + CSS + 原生 JS，推到 `main` 就會上線。

## 2. 三條紅線（違反就停下來問）

1. **不放私人資料**。不能出現：LINE user id（`U` 開頭 33 碼）、`web_token`、`reply_token`、
   聊天內容、`items.source_url`、`.env` 的任何值、作者電腦路徑。
2. **資料只走白名單**。網頁要用新欄位時，加進 `export_pages.py` 的 `REPO_COLS` / `ALCHEMY_COLS`，
   不能改成 `SELECT *`。`users`、`jobs`、`items`、`notes` 四張表不能匯出。
3. **commit 前一定跑金鑰檢查**，結果不是 0 就不能 commit：
   ```
   python tools/check_secrets.py <私人資料夾路徑>
   ```

## 3. 要新增一個頁面

照這個順序做：

1. 建 `docs/<名稱>.html`，例如 `docs/stats.html`。檔名用英文小寫加 `-`。
2. 開頭照抄 `index.html` 的 `<head>`：`lang="zh-Hant"`、`charset`、`viewport`、
   `<title>` 寫「頁面名 · SolGeGoodShxt」、`<link rel="stylesheet" href="style.css">`。
3. 版面用現有的 class：`.wrap`（置中寬度）、`.grid` + `.card`（卡片）、`.chip`（小標籤）、
   `.meta`、`.sum`、`.aud`。**不要在頁面裡寫新的顏色**，需要新顏色就加到 `style.css` 的
   `:root`，而且淺色、深色兩組都要加。
4. 資料一律 `fetch('data.json')`。不要把資料直接寫死在 HTML 裡。
5. 文字一律用 `textContent` 或 `el()` 小工具放進畫面，**不要用 `innerHTML` 放資料**
   （資料是 AI 產生的，可能夾帶 HTML）。唯一例外是 mermaid 產生的 SVG。
6. 外部套件只能從 `cdn.jsdelivr.net` 載入，而且要寫死版本，例如 `mermaid@11.4.1`。
7. 在 `index.html` 的 header 和新頁面都放互相連結，讓人點得到。
8. 手機寬度（360px）也要能看，不能出現橫向捲軸。

## 4. 要新增一種內容

- **私人資料庫已經有的欄位**（例如 `repos.topics`）：加進 `export_pages.py` 白名單 →
  重跑匯出 → 在頁面上顯示。
- **資料庫沒有的新內容**（例如「本週精選」）：放 `docs/<名稱>.json`，人工維護，
  格式寫在檔案旁邊的說明裡。不要塞進 `data.json`，因為那個檔每次匯出都會被蓋掉。
- 更新知識庫：
  ```
  python tools/export_pages.py <私人資料夾>/data/solge.db
  ```

## 5. 做完怎麼驗收

1. 本機預覽：`python -m http.server 8765 --directory docs`，打開 <http://127.0.0.1:8765/>。
2. 看三件事就好：頁面有出來、資料數量對、瀏覽器 console 沒有紅字（`favicon.ico` 404 可以忽略）。
3. 跑 `tools/check_secrets.py`，要是 0。
4. 推上去後等一兩分鐘，打開正式網址再看一次。

## 6. Commit 規則

- 一件事一個 commit，訊息用中文，第一行說「做了什麼」。
- 只動跟這次任務有關的檔案。
- 推到 `main` 之前，先讓作者確認。
