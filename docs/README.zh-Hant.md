<div align="center">

<sub><strong>L0NE-6 · DAILY SIGNAL</strong></sub>

# ModelScope Daily

**ModelScope 國內版 / 國際版每日簽到單檔腳本，分開管理權杖、回讀魔粒餘額與呼叫額度。**

[简体中文](../README.md) | [English](README.en.md) | [繁體中文](README.zh-Hant.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português (BR)](README.pt-BR.md)

<img src="https://img.shields.io/github/v/release/L0NE-6/ModelScope-Daily?style=for-the-badge&label=Release&color=2ea44f&logo=github" />
<img src="https://img.shields.io/github/stars/L0NE-6/ModelScope-Daily?style=for-the-badge&label=Stars&color=FFC75F&logo=github" />
<img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" />

</div>

> 完整中文文件請見 [../README.md](../README.md)。

## ✨ 核心能力

- 國內站與國際站分開配置，權杖不混用。
- 透過 `GET /api/v1/users/login/info` 觸發每日簽到。
- 國內站讀取 `/openapi/v1/magicubes/transactions` 確認到帳。
- 彙總當日 `daily_active` 與 `aliyun_bindlogin` 魔粒收入。
- 回讀總額、可用、凍結魔粒與今日呼叫次數。
- 相容大小寫兩套上游回應信封。
- 區分 HTTP `401` 登入失效與 HTTP `403` 風控攔截。

## 🧭 簽到方式

ModelScope 沒有獨立簽到按鈕，呼叫一次登入資訊介面就會觸發當日簽到；重複呼叫保持冪等。

```text
ms- token
  → Cookie: m_session_id=<token>
  → GET /api/v1/users/login/info
  → 國內站：查詢當日魔粒帳單
  → 回讀餘額與用量
  → 標記已到帳 / 今日已領 / 未確認 / 失敗
```

`--query` 也會呼叫登入資訊介面，因此同樣會觸發簽到。

## 🚀 最短可行設定

```bash
python -m pip install -r requirements.txt
```

在對應的 ModelScope 控制台建立 `ms-` 存取權杖。

單帳號：

```text
MODELSCOPE_CN_TOKEN=ms-CN_TOKEN
MODELSCOPE_INTL_TOKEN=ms-INTL_TOKEN
```

多帳號：

```text
MODELSCOPE_CN_TOKENS=
國內主號|ms-CN_TOKEN
國內小號|ms-CN_TOKEN

MODELSCOPE_INTL_TOKENS=
國際主號|ms-INTL_TOKEN
```

執行：

```bash
python modelscope_daily.py
python modelscope_daily.py --only 1
python modelscope_daily.py --no-notify
```

## 🐧 青龍面板

```bash
pip3 install requests
```

設定 `MODELSCOPE_CN_TOKENS` 和/或 `MODELSCOPE_INTL_TOKENS`，建立任務：

```text
30 8 * * * python3 modelscope_daily.py
```

首次驗證可用 `--only` 逐個檢查權杖。

## ☁️ GitHub Actions

工作流為 [../.github/workflows/daily.yml](../.github/workflows/daily.yml)。目前啟用手動觸發，排程預設為註解。

| Secret | 必填 | 用途 |
| :--- | :---: | :--- |
| `MODELSCOPE_CN_TOKENS` | 二選一 | 國內多帳號權杖 |
| `MODELSCOPE_INTL_TOKENS` | 二選一 | 國際多帳號權杖 |
| `MODELSCOPE_CN_TOKEN` | 二選一 | 國內單帳號權杖 |
| `MODELSCOPE_INTL_TOKEN` | 二選一 | 國際單帳號權杖 |
| `MODELSCOPE_PROXY` | 否 | 代理 |
| `PLUSPLUS_TOKEN` / `BARK_URL` / `WECOM_WEBHOOK` / `DINGTALK_WEBHOOK` | 否 | 通知 |

若要啟用排程，取消兩行註解。`30 0 * * *` 使用 UTC，對應北京時間 08:30。

## 🔧 關鍵環境變數

| 變數 | 說明 |
| :--- | :--- |
| `MODELSCOPE_CN_TOKENS` | 國內多帳號：`備註\|ms-token` |
| `MODELSCOPE_INTL_TOKENS` | 國際多帳號：`備註\|ms-token` |
| `MODELSCOPE_CN_TOKEN` | 國內單帳號 |
| `MODELSCOPE_INTL_TOKEN` | 國際單帳號 |
| `MODELSCOPE_PROXY` | HTTP(S) / SOCKS 代理 |
| `MODELSCOPE_VERIFY_DELAY` | 國內帳單重查間隔，預設 `2` 秒 |
| `MODELSCOPE_NO_NOTIFY` | `1` 關閉通知 |

## 📊 成功判據

| 情況 | 判定 |
| :--- | :--- |
| HTTP `401` | 權杖失效或站點不匹配 |
| HTTP `403` | 風控攔截，不等同登入失效 |
| 餘額缺少 `data` / `available_balance` | 查詢失敗，不顯示為 0 |
| 國內站 | 當日必須有 `type=EARN` 且 `rule_key=daily_active / aliyun_bindlogin` 的帳單 |
| 帳單初次為空 | 等待 `MODELSCOPE_VERIFY_DELAY` 後重查一次 |
| 國際站 | 沒有獨立按鈕介面，按登入觸發口徑報告 |

國內站查不到有效帳單時會標記「未確認」，不會把登入成功冒充為簽到成功。

## 📦 版本說明

目前發布版為 `v1.0.2`，區分 `401/403` 並修正餘額欄位缺失誤顯示為 0。CHANGELOG 記錄新增 7 項離線回歸、共 11 項測試通過，同時說明該輪沒有使用真實帳號發送真實簽到請求。

## 🔒 隱私

- 不收集或上傳帳號資料。
- 日誌不輸出完整 `ms-` 權杖。
- `.env` 與日誌不要提交到 Git。
- 權杖只放在本機環境變數、GitHub Secrets 或青龍環境變數。
- 回報問題前請移除權杖、暱稱、帳號 ID 與帳單明細。

## 🔗 專案連結

- [Releases](https://github.com/L0NE-6/ModelScope-Daily/releases)
- [Issues](https://github.com/L0NE-6/ModelScope-Daily/issues)
- [Changelog](../CHANGELOG.md)
- [License](../LICENSE)
