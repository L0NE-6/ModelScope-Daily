<div align="center">

<sub><strong>L0NE-6 · DAILY SIGNAL</strong></sub>

# ModelScope Daily

**ModelScope 中国版・国際版のデイリーチェックイン用単一ファイルスクリプトです。トークンを分離し、魔粒クレジットの台帳確認、残高、利用量を取得します。**

[简体中文](../README.md) | [English](README.en.md) | [繁體中文](README.zh-Hant.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português (BR)](README.pt-BR.md)

<img src="https://img.shields.io/github/v/release/L0NE-6/ModelScope-Daily?style=for-the-badge&label=Release&color=2ea44f&logo=github" />
<img src="https://img.shields.io/github/stars/L0NE-6/ModelScope-Daily?style=for-the-badge&label=Stars&color=FFC75F&logo=github" />
<img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" />

</div>

> 完全な中国語ドキュメントは [../README.md](../README.md) を参照してください。

## ✨ 主な機能

- 中国版と国際版の認証情報を分離します。
- `GET /api/v1/users/login/info` でデイリーチェックインを発生させます。
- 中国版では `/openapi/v1/magicubes/transactions` でクレジット到着を確認します。
- 同日の `daily_active` と `aliyun_bindlogin` を集計します。
- 総クレジット、利用可能、凍結中、当日の推論回数を取得します。
- 大文字・小文字の両方のレスポンス形式に対応します。
- HTTP `401` の認証失敗と HTTP `403` のリスク管理ブロックを区別します。

## 🧭 仕組み

ModelScope には独立したチェックインボタンがありません。ログイン情報 API の呼び出しがデイリーチェックインを発生させ、繰り返し呼び出しても冪等です。

```text
ms- token
  → Cookie: m_session_id=<token>
  → GET /api/v1/users/login/info
  → 中国版は当日のクレジット台帳を確認
  → 残高と利用量を取得
  → 成功 / 受領済み / 未確認 / 失敗を表示
```

`--query` もログイン情報 API を呼ぶため、チェックインを発生させます。完全な読み取り専用モードはありません。

## 🚀 最短セットアップ

```bash
python -m pip install -r requirements.txt
```

対応する ModelScope コンソールで `ms-` アクセストークンを作成します。

単一アカウント：

```text
MODELSCOPE_CN_TOKEN=ms-CN_TOKEN
MODELSCOPE_INTL_TOKEN=ms-INTL_TOKEN
```

複数アカウント：

```text
MODELSCOPE_CN_TOKENS=
中国版メイン|ms-CN_TOKEN
中国版サブ|ms-CN_TOKEN

MODELSCOPE_INTL_TOKENS=
国際版メイン|ms-INTL_TOKEN
```

実行：

```bash
python modelscope_daily.py
python modelscope_daily.py --only 1
python modelscope_daily.py --no-notify
```

## 🐧 Qinglong

```bash
pip3 install requests
```

`MODELSCOPE_CN_TOKENS` と `MODELSCOPE_INTL_TOKENS` を設定し、タスクを作成します。

```text
30 8 * * * python3 modelscope_daily.py
```

初回確認では `--only` を使って 1 アカウントずつ検証できます。

## ☁️ GitHub Actions

ワークフローは [../.github/workflows/daily.yml](../.github/workflows/daily.yml) です。手動実行が有効で、スケジュールは既定でコメントアウトされています。

| Secret | 必須 | 用途 |
| :--- | :---: | :--- |
| `MODELSCOPE_CN_TOKENS` | いずれか | 中国版の複数アカウント |
| `MODELSCOPE_INTL_TOKENS` | いずれか | 国際版の複数アカウント |
| `MODELSCOPE_CN_TOKEN` | いずれか | 中国版の単一アカウント |
| `MODELSCOPE_INTL_TOKEN` | いずれか | 国際版の単一アカウント |
| `MODELSCOPE_PROXY` | 任意 | プロキシ |
| `PLUSPLUS_TOKEN` / `BARK_URL` / `WECOM_WEBHOOK` / `DINGTALK_WEBHOOK` | 任意 | 通知 |

定時実行を有効にする場合はコメントを外します。`30 0 * * *` は UTC で、北京時間 08:30 に相当します。

## 🔧 主な環境変数

| 変数 | 説明 |
| :--- | :--- |
| `MODELSCOPE_CN_TOKENS` | 中国版の複数アカウント：`名前\|ms-token` |
| `MODELSCOPE_INTL_TOKENS` | 国際版の複数アカウント：`名前\|ms-token` |
| `MODELSCOPE_CN_TOKEN` | 中国版の単一アカウント |
| `MODELSCOPE_INTL_TOKEN` | 国際版の単一アカウント |
| `MODELSCOPE_PROXY` | HTTP(S) / SOCKS プロキシ |
| `MODELSCOPE_VERIFY_DELAY` | 中国版台帳の再確認待ち時間。既定 `2` 秒 |
| `MODELSCOPE_NO_NOTIFY` | `1` で通知を無効化 |

## 📊 成功条件

| 状況 | 判定 |
| :--- | :--- |
| HTTP `401` | トークン無効、または別サイトのトークン |
| HTTP `403` | リスク管理ブロック。ログイン失効とは限らない |
| 残高データ不足 | 取得失敗。0 残高として表示しない |
| 中国版 | 当日の `type=EARN` と `daily_active / aliyun_bindlogin` が必要 |
| 台帳が最初は空 | `MODELSCOPE_VERIFY_DELAY` 後に 1 回再試行 |
| 国際版 | 独立ボタン API はなく、ログイン発生ベースで報告 |

中国版で有効な台帳記録がない場合は「未確認」と表示し、ログイン成功をチェックイン成功として扱いません。

## 📦 リリース情報

現在のリリースは `v1.0.2` です。`401` と `403` を分離し、残高データ不足時に 0 と表示しないよう修正しました。CHANGELOG には新しいオフラインテスト 7 件、合計 11 件の成功が記録されています。また、その回は実アカウントで実際のチェックイン要求を送っていないことも明記されています。

## 🔒 プライバシー

- アカウントデータを収集・アップロードしません。
- ログに完全な `ms-` トークンを出力しません。
- `.env` とログファイルを Git にコミットしないでください。
- トークンはローカル環境変数、GitHub Secrets、Qinglong の変数にだけ保存してください。
- Issue を投稿する前にトークン、名前、アカウント ID、台帳明細を削除してください。

## 🔗 リンク

- [Releases](https://github.com/L0NE-6/ModelScope-Daily/releases)
- [Issues](https://github.com/L0NE-6/ModelScope-Daily/issues)
- [Changelog](../CHANGELOG.md)
- [License](../LICENSE)
