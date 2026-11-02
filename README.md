<div align="center">

<sub><strong>L0NE-6 · DAILY SIGNAL</strong></sub>

# 🌐 ModelScope Daily

**ModelScope 国内版 / 国际版每日签到单文件脚本，分开管理令牌、回读魔粒余额与调用额度。**

[简体中文](README.md) | [English](docs/README.en.md) | [繁體中文](docs/README.zh-Hant.md) | [日本語](docs/README.ja.md) | [한국어](docs/README.ko.md) | [Português (BR)](docs/README.pt-BR.md)

<a href="https://github.com/L0NE-6/ModelScope-Daily/releases"><img src="https://img.shields.io/github/v/release/L0NE-6/ModelScope-Daily?style=for-the-badge&label=Release&color=2ea44f&logo=github" alt="Release" /></a>
<img src="https://img.shields.io/github/stars/L0NE-6/ModelScope-Daily?style=for-the-badge&label=Stars&color=FFC75F&logo=github" alt="Stars" />
<img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/%E9%9D%92%E9%BE%99-Ready-4EAA25?style=for-the-badge" alt="Qinglong" />
<a href="https://github.com/L0NE-6/ModelScope-Daily/actions/workflows/daily.yml"><img src="https://img.shields.io/github/actions/workflow/status/L0NE-6/ModelScope-Daily/daily.yml?branch=main&style=for-the-badge&label=Actions&logo=githubactions&logoColor=white" alt="GitHub Actions" /></a>
<img src="https://img.shields.io/github/license/L0NE-6/ModelScope-Daily?style=for-the-badge&label=License&color=F472B6" alt="License" />
<a href="https://github.com/L0NE-6/ModelScope-Daily/releases"><img src="https://img.shields.io/badge/%E2%AC%87%20Releases-%E4%B8%8B%E8%BD%BD-2ea44f?style=for-the-badge&logo=github&logoColor=white" alt="Releases Download" /></a>

[✨ 30 秒速览](#-30-秒速览) · [🚀 快速开始](#-快速开始) · [🐧 青龙部署](#-青龙部署) · [☁️ GitHub Actions](#-github-actions) · [🔧 环境变量](#-环境变量) · [❓ 常见问题](#-常见问题) · [🚫 使用边界](#usage-policy) · [✦ 星轨](#-星轨-star-trail)

</div>

---

## ✨ 30 秒速览

| 维度 | 说明 |
| :--- | :--- |
| **用途** | 触发 ModelScope 国内站 / 国际站每日签到，并回读账号身份、魔粒余额和调用用量。 |
| **输入** | 国内站、国际站各自的 `ms-` 访问令牌；可用单账号或多账号格式。 |
| **输出** | 账号身份、当日魔粒到账、可用/总额/冻结余额、今日已用调用次数。 |
| **部署** | 青龙面板、GitHub Actions、Windows / Linux 本地运行。 |
| **依赖** | Python 3 + `requests`；仓库 Actions 使用 Python 3.11。 |
| **成功判据** | 国内站需查到当日有效魔粒账单；国际站按登录接口触达口径。查不到时明确标记“未确认”。 |

**核心能力**

- 国内站与国际站分开配置，令牌互不混用。
- 通过 `GET /api/v1/users/login/info` 触发当日签到。
- 国内站读取 `/openapi/v1/magicubes/transactions` 确认当日到账。
- 汇总 `daily_active` / `aliyun_bindlogin` 两类魔粒收入。
- 回读魔粒总额、可用、冻结余额和今日已用调用次数。
- 兼容大小写两套上游响应信封，区分 `401` 登录失效与 `403` 风控。

## 🧭 签到机制

ModelScope 没有独立的“签到按钮”接口。调用一次登录信息接口就会触发当日魔粒签到，重复调用保持幂等。

```text
ms- token
  → Cookie: m_session_id=<token>
  → GET /api/v1/users/login/info
  → 国内站：查询魔粒账单并匹配北京时间当日 EARN 记录
  → 回读余额与调用额度
  → 分账号输出已到账 / 今日已领取 / 未确认 / 失败
```

> `--query` 同样会调用登录信息接口，因此也会触发签到。该接口本身就是签到机制，不存在完全只读的本地查询方式。

## 🚀 快速开始

**1. 安装依赖**

```bash
python -m pip install -r requirements.txt
```

**2. 创建访问令牌**

在对应 ModelScope 控制台创建以 `ms-` 开头的访问令牌。同一个令牌既可作为推理 Bearer，也可作为网页站 Cookie `m_session_id`。

国内站令牌不能用于国际站网页签到，国际站令牌也不能反过来使用。

**3. 配置单账号**

```text
MODELSCOPE_CN_TOKEN=ms-CN_TOKEN
MODELSCOPE_INTL_TOKEN=ms-INTL_TOKEN
```

可以只配置其中一个站点。

**4. 配置多账号**

```text
MODELSCOPE_CN_TOKENS=
国内主号|ms-CN_TOKEN
国内小号|ms-CN_TOKEN

MODELSCOPE_INTL_TOKENS=
国际主号|ms-INTL_TOKEN
```

**5. 运行**

```bash
python modelscope_daily.py
python modelscope_daily.py --only 1
python modelscope_daily.py --no-notify
```

## ⌨️ 命令行

| 命令 | 作用 |
| :--- | :--- |
| `python modelscope_daily.py` | 触发签到并回读到账、余额与用量 |
| `python modelscope_daily.py --only 1` | 只处理按国内站、国际站顺序展开后的第 1 个账号 |
| `python modelscope_daily.py --query` | 保留参数，但仍会触发登录信息接口 |
| `python modelscope_daily.py --no-notify` | 本轮不发送通知 |

退出码：`0` 表示至少一个账号确认成功；`1` 表示没有配置账号、指定账号不存在，或所有账号都失败 / 未确认。

## 🐧 青龙部署

```bash
pip3 install requests
```

在青龙环境变量中填写 `MODELSCOPE_CN_TOKENS` 和/或 `MODELSCOPE_INTL_TOKENS`，再创建任务：

```text
30 8 * * * python3 modelscope_daily.py
```

建议首次运行先保留 `--only`，逐个确认站点令牌与账号状态。脚本不会写账号令牌到仓库；运行日志只输出脱敏身份信息。

## ☁️ GitHub Actions

工作流位于 [`.github/workflows/daily.yml`](.github/workflows/daily.yml)。**默认只有手动触发**，定时段目前被注释。

在仓库 Secrets 中配置：

| Secret | 必填 | 说明 |
| :--- | :---: | :--- |
| `MODELSCOPE_CN_TOKENS` | 二选一 | 国内站多账号令牌 |
| `MODELSCOPE_INTL_TOKENS` | 二选一 | 国际站多账号令牌 |
| `MODELSCOPE_CN_TOKEN` | 二选一 | 国内站单账号令牌 |
| `MODELSCOPE_INTL_TOKEN` | 二选一 | 国际站单账号令牌 |
| `MODELSCOPE_PROXY` | 否 | HTTP(S) / SOCKS 代理 |
| `PLUSPLUS_TOKEN` | 否 | PushPlus 推送令牌 |
| `BARK_URL` | 否 | Bark 推送地址 |
| `WECOM_WEBHOOK` | 否 | 企业微信机器人 webhook |
| `DINGTALK_WEBHOOK` | 否 | 钉钉机器人 webhook |

需要定时运行时，取消 workflow 中 schedule 两行的注释。示例 `30 0 * * *` 使用 UTC，对应北京时间 08:30。

工作流没有默认透传 `MODELSCOPE_VERIFY_DELAY` 和 `MODELSCOPE_NO_NOTIFY`；可以在本地 / 青龙中使用，或自行在 workflow 中显式添加映射。

## 🔧 环境变量

### 账号

| 变量 | 必填 | 说明 |
| :--- | :---: | :--- |
| `MODELSCOPE_CN_TOKENS` | 多账号 | 国内版，每行 `备注\|ms-token` |
| `MODELSCOPE_INTL_TOKENS` | 多账号 | 国际版，每行 `备注\|ms-token` |
| `MODELSCOPE_CN_TOKEN` | 单账号 | 国内版单账号令牌 |
| `MODELSCOPE_INTL_TOKEN` | 单账号 | 国际版单账号令牌 |

### 运行与通知

| 变量 | 说明 |
| :--- | :--- |
| `MODELSCOPE_PROXY` | HTTP(S) / SOCKS 代理 |
| `MODELSCOPE_VERIFY_DELAY` | 国内站账单回读间隔秒数，默认 `2` |
| `MODELSCOPE_NO_NOTIFY` | 设为 `1` 时关闭推送 |
| `PLUSPLUS_TOKEN` | PushPlus 令牌 |
| `BARK_URL` | Bark 服务地址 |
| `WECOM_WEBHOOK` | 企业微信机器人 webhook，或仅填 key |
| `QYWX_TOKEN` | 企业微信 key 的兼容变量名 |
| `DINGTALK_WEBHOOK` | 钉钉机器人 webhook |

## 📊 判定规则

| 场景 | 判定 |
| :--- | :--- |
| HTTP `401` | 令牌失效或站点不匹配 |
| HTTP `403` | 魔搭风控拦截，不等同于登录失效 |
| 响应信封 | 同时兼容 `Code/Success/Data/Message` 与 `code/success/data/msg` |
| 余额字段缺失 | 按查询失败处理，不显示成 0 余额 |
| 国内站到账 | 必须是北京时间当日、`type=EARN` 且 `rule_key=daily_active / aliyun_bindlogin` |
| 初次账单为空 | 默认等待 `MODELSCOPE_VERIFY_DELAY` 秒后复查一次 |
| 国际站 | 没有独立按钮接口，按登录触发口径报告 |

国内站未查到到账记录时显示“未确认”，不会把登录接口成功冒充为签到成功。余额接口失败会降级展示，不影响已经确认的签到结果。

## 📦 版本说明

当前发布版为 `v1.0.2`。该版本修复了 `401/403` 混淆和余额字段缺失误显示为 0 的问题。CHANGELOG 记录本轮新增 7 项离线回归、共 11 项测试通过；同时明确说明该轮没有使用真实账号发送真实签到请求。

## ❓ 常见问题

<details>
<summary><b>为什么 --query 也会签到？</b></summary>

ModelScope 的登录信息接口本身触发签到，本项目没有可绕开签到的只读查询接口。
</details>

<details>
<summary><b>为什么国内站显示未确认？</b></summary>

登录触达不代表魔粒已经写入账单。需要查到当日符合规则的 `EARN` 记录才算国内站确认到账。
</details>

<details>
<summary><b>HTTP 403 是否就是令牌过期？</b></summary>

不是。`401` 才是令牌失效或站点不匹配；`403` 表示魔搭风控拦截，应先降低频率并稍后重试。
</details>

<details>
<summary><b>国际站和国内站令牌可以混用吗？</b></summary>

不可以。两个站点的网页登录态不通用，必须分别配置。
</details>

## 🔒 隐私说明

- 不收集、不上传账号数据；
- 日志不输出完整 `ms-` 令牌；
- `.env` 与日志已加入 `.gitignore`；
- 只把令牌放在本地环境变量、GitHub Secrets 或青龙环境变量中；
- 不要提交魔粒账单截图、完整昵称或账号 ID 到公开 Issue。

<a id="usage-policy"></a>
## 🚫 使用边界与转载声明

本项目仓库、脚本、部署说明和 Release 下载始终免费公开。未经作者明确书面许可，禁止将本项目包装为付费资源、内部版、独家版、会员权益、收费课程、付费部署或包更新服务；禁止搬运到其他账号、群组、频道、网盘、电商或付费平台进行涨粉、截流、倒卖和引流；禁止删除作者与版权信息后冒充原创；禁止使用作者昵称、头像、二维码和项目名称制造官方授权假象。

> 如需商业合作、品牌授权、联合分发或使用作者名义提供付费服务，请先取得作者明确书面授权。完整规则、收款码防诈骗说明和违规处理方式见 **[NOTICE.md](NOTICE.md)**。

> 官方仓库和 Release 始终免费。第三方以“下载费 / 激活费 / 内部版 / 代部署 / 会员门槛”等名义收费，均与作者无关，请停止付款并保留证据。

> 对上述违规行为，作者有权要求立即停止传播、删除内容并下架相关商品或页面；并可视情况暂停更新、归档或删除本仓库及相关 Release、向平台投诉或采取进一步必要措施。

## ☕ 支持与反馈

脚本免费使用，不含账号数据。如果它对你有帮助，可以自愿扫码支持：

<p align="center">
  <img src="assets/donate-wechat.png" width="260" alt="微信赞赏码" />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="assets/donate-alipay.jpg" width="260" alt="支付宝收款码" />
</p>

> ⚠️ 收款码仅用于向作者自愿赞赏。任何第三方以代下载、代部署、内部资源或会员群为由收费，均与作者无关，请停止付款并保留证据。

反馈问题时请删除令牌、昵称、账号 ID 和账单明细，再通过 [Issues](https://github.com/L0NE-6/ModelScope-Daily/issues) 提交；版本变化见 [Releases](https://github.com/L0NE-6/ModelScope-Daily/releases)。

## ✦ 星轨 Star Trail

让每日签到沿着稳定轨道前行，每一次 Star 都是新的定位信号。

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=L0NE-6/ModelScope-Daily&type=Date&theme=dark" />
  <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=L0NE-6/ModelScope-Daily&type=Date&theme=light" />
  <img alt="ModelScope Daily Star Trail" src="https://api.star-history.com/svg?repos=L0NE-6/ModelScope-Daily&type=Date&theme=light" />
</picture>

<div align="center">

[Releases](https://github.com/L0NE-6/ModelScope-Daily/releases) · [Issues](https://github.com/L0NE-6/ModelScope-Daily/issues) · [⭐ Star](https://github.com/L0NE-6/ModelScope-Daily)

</div>
