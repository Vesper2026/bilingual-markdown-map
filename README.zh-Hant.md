# 雙語 Markdown 結構對照

[English](README.md) · [網站](https://markdown.vesperai.space/zh-Hant/)

按章節順序或明確的一對一索引映射，對照兩份本機 Markdown，檢查結構遺漏；不翻譯、不評分語意。

## 執行

需要 Python 3.10+。clone 後在儲存庫根目錄操作：

```sh
git clone https://github.com/Vesper2026/bilingual-markdown-map.git
cd bilingual-markdown-map
# No runtime dependencies; Python 3.10+ is sufficient.
python bilingual_map.py examples/source.md examples/zh-Hant.md --output examples/output
```

不需要第三方執行期套件。也可在本專案的 venv 內安裝 `.` 以取得 CLI 入口；直接執行腳本不必安裝。

## 輸入與真實範例輸出

```text
source.md: # Methods + image / # Results
zh-Hant.md: # 方法 (image and Results intentionally omitted)
```

隨附完整範例（不只是上面的縮寫說明）會產生：

```text
1 section pairs; 1 source / 0 target unpaired. No semantic scoring.
```

輸出 `comparison.json` 與 `comparison.md`。範例配對 Methods ↔ 方法，提示 `images` 差異，Results 未配對。加上 `--map examples/mapping.json` 可指定 `[[1,1]]`；章節重排可用 `[[1,2],[2,1]]`。每個識別到的 ATX 標題依出現順序從 1 編號，包括空標題與重複標題。前言為索引 0；空文件沒有章節。預設只將前言配前言，其餘按順序配對。明確模式只配列出的索引，重複或未知索引會報錯。每個標題開始新章節，子節物件不向父節重複累計。

## 核心測試

```sh
python -m unittest discover -p "test_*.py"
```

測試驗證核心規則與合成範例，不驗證使用者文件的事實或翻譯品質。

## 限制與資料處理

不是完整 CommonMark 解析器，也不是單文件 lint。支援最多三個前導空格的 ATX 標題、反引號／波浪號圍欄、獨立 $$ 區塊與簡單行內連結／圖片目的網址。比較標題層級、程式語言多重集合、公式區塊數及連結／圖片目標多重集合。不支援 Setext、參照式連結、原始 HTML、巢狀括號網址、表格與行內公式；行內程式碼處理有限，也不 lint 未閉合圍欄。範例圖片只是符號引用。中間漏節會造成順序配對錯位，應閱讀標題或提供映射。結構相同不代表翻譯正確。

## 本工具的獨立雙語站

```sh
python site/build.py
python -m http.server 8090 --directory docs
```

開啟 http://localhost:8090/zh-Hant/ 或 /en/。來源在 `site/`，輸出在 `docs/`，範例複製到 `docs/downloads/`。每種語言有兩篇原創文章，以及獨立 hostname、canonical、sitemap、robots 與 CNAME；沒有追蹤分析或上傳表單。

## 實用工具

[KolmoPDF](https://www.kolmopdf.com/pdf-to-markdown) 可搭配本工具使用。KolmoPDF 雲端服務會上傳文件，本機開源 CLI 不取代其專有解析器。

## 授權

自有程式、合成資料、文件與靜態站來源採 MIT，見 LICENSE；第三方依賴保留原授權。
