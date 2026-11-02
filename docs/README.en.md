<div align="center">

<sub><strong>L0NE-6 · DAILY SIGNAL</strong></sub>

# ModelScope Daily

**A single-file daily check-in script for ModelScope CN and International, with separate tokens, credit-ledger verification, balance readback, and usage reporting.**

[简体中文](../README.md) | [English](README.en.md) | [繁體中文](README.zh-Hant.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português (BR)](README.pt-BR.md)

<img src="https://img.shields.io/github/v/release/L0NE-6/ModelScope-Daily?style=for-the-badge&label=Release&color=2ea44f&logo=github" />
<img src="https://img.shields.io/github/stars/L0NE-6/ModelScope-Daily?style=for-the-badge&label=Stars&color=FFC75F&logo=github" />
<img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" />

</div>

> The complete Chinese documentation is available in [../README.md](../README.md).

## ✨ Core capabilities

- Keeps CN and International credentials separate.
- Triggers the daily check-in through `GET /api/v1/users/login/info`.
- Verifies CN credit receipt through `/openapi/v1/magicubes/transactions`.
- Aggregates same-day `daily_active` and `aliyun_bindlogin` earnings.
- Reads total, available, and frozen credits plus today's inference usage.
- Handles both upper- and lower-case response envelopes.
- Distinguishes HTTP `401` authentication failures from HTTP `403` risk-control blocks.

## 🧭 How it works

ModelScope has no standalone check-in button. A login-info request triggers the daily credit check-in and repeated requests are idempotent.

```text
ms- token
  → Cookie: m_session_id=<token>
  → GET /api/v1/users/login/info
  → CN: verify today's credit ledger entries
  → read balance and usage
  → report confirmed / already claimed / unconfirmed / failed
```

`--query` still calls the login-info endpoint and therefore still triggers the check-in. There is no fully read-only local query mode.

## 🚀 Quick start

Install dependencies from the repository root:

```bash
python -m pip install -r requirements.txt
```

Create an `ms-` access token in the corresponding ModelScope console. The token can be used both as an inference Bearer token and as the `m_session_id` web cookie.

Single account:

```text
MODELSCOPE_CN_TOKEN=ms-CN_TOKEN
MODELSCOPE_INTL_TOKEN=ms-INTL_TOKEN
```

You may configure only one region.

Multiple accounts:

```text
MODELSCOPE_CN_TOKENS=
CN Main|ms-CN_TOKEN
CN Alt|ms-CN_TOKEN

MODELSCOPE_INTL_TOKENS=
Intl Main|ms-INTL_TOKEN
```

Run:

```bash
python modelscope_daily.py
python modelscope_daily.py --only 1
python modelscope_daily.py --no-notify
```

## 🐧 Qinglong

```bash
pip3 install requests
```

Set `MODELSCOPE_CN_TOKENS` and/or `MODELSCOPE_INTL_TOKENS`, then create:

```text
30 8 * * * python3 modelscope_daily.py
```

Use `--only` for the first validation run when you want to inspect each token individually.

## ☁️ GitHub Actions

The workflow is [../.github/workflows/daily.yml](../.github/workflows/daily.yml). Manual execution is enabled; the schedule block is commented out by default.

| Secret | Required | Purpose |
| :--- | :---: | :--- |
| `MODELSCOPE_CN_TOKENS` | One of two | CN multi-account tokens |
| `MODELSCOPE_INTL_TOKENS` | One of two | International multi-account tokens |
| `MODELSCOPE_CN_TOKEN` | One of two | CN single-account token |
| `MODELSCOPE_INTL_TOKEN` | One of two | International single-account token |
| `MODELSCOPE_PROXY` | Optional | HTTP(S) / SOCKS proxy |
| `PLUSPLUS_TOKEN`, `BARK_URL`, `WECOM_WEBHOOK`, `DINGTALK_WEBHOOK` | Optional | Notifications |

To enable the schedule, uncomment its two lines. `30 0 * * *` uses UTC and corresponds to 08:30 Beijing time.

## 🔧 Key environment variables

| Variable | Required | Description |
| :--- | :---: | :--- |
| `MODELSCOPE_CN_TOKENS` | Multi | CN records in `name\|ms-token` format |
| `MODELSCOPE_INTL_TOKENS` | Multi | International records in `name\|ms-token` format |
| `MODELSCOPE_CN_TOKEN` | Single | CN single-account token |
| `MODELSCOPE_INTL_TOKEN` | Single | International single-account token |
| `MODELSCOPE_PROXY` | Optional | HTTP(S) / SOCKS proxy |
| `MODELSCOPE_VERIFY_DELAY` | Optional | Delay before reading the CN ledger again; default `2` seconds |
| `MODELSCOPE_NO_NOTIFY` | Optional | Set to `1` to disable notifications |

## 📊 Success criteria

| Case | Result |
| :--- | :--- |
| HTTP `401` | Token invalid or used on the wrong site |
| HTTP `403` | Risk-control block, not automatically an expired login |
| Missing balance data | Query failure, never reported as a zero balance |
| CN ledger | Must contain today's `type=EARN` record with `daily_active` or `aliyun_bindlogin` |
| CN ledger initially empty | Retry once after `MODELSCOPE_VERIFY_DELAY` |
| International site | No standalone button protocol; report by login-trigger semantics |

Without a matching CN ledger entry, the account is reported as unconfirmed, not successful.

## 📦 Release context

The current release is `v1.0.2`. It separates `401` and `403`, and fails instead of displaying zero when the balance envelope is incomplete. The changelog records seven new offline tests and eleven passing tests in total. It also states that the release round did not use a real account or send live check-in requests.

## 🔒 Privacy

- The project does not collect or upload account data.
- Logs never print a complete `ms-` token.
- Keep `.env` and log files out of Git.
- Store tokens only in local environment variables, GitHub Secrets, or Qinglong variables.
- Remove tokens, nicknames, account IDs, and ledger details before opening an issue.

## 🔗 Project links

- [Releases](https://github.com/L0NE-6/ModelScope-Daily/releases)
- [Issues](https://github.com/L0NE-6/ModelScope-Daily/issues)
- [Changelog](../CHANGELOG.md)
- [License](../LICENSE)
