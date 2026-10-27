# ModelScope 国内版 / 国际版每日签到

> 当前版本：**v1.0.2**（2026-10-27）

单文件 Python 青龙脚本。ModelScope 没有独立签到按钮接口，调用一次登录信息接口就会触发当日魔粒签到。

## 功能

- 国内站与国际站分开配置、互不混用令牌。
- 每日签到触发、国内站账单到账回读与账号身份回读。
- 魔粒总额、可用、冻结余额。
- 今日已用调用次数。
- 多账号、代理、多通道推送。

## 令牌

在对应 ModelScope 控制台创建以 `ms-` 开头的访问令牌。同一个令牌既可用于推理 Bearer，也可作为网页站 Cookie `m_session_id`。

国内站令牌不能用于国际站网页签到，国际站令牌也不能反过来使用。

## 环境变量

| 变量 | 说明 |
| :--- | :--- |
| `MODELSCOPE_CN_TOKENS` | 国内版多账号，每行 `备注\|ms-token` |
| `MODELSCOPE_INTL_TOKENS` | 国际版多账号，每行 `备注\|ms-token` |
| `MODELSCOPE_CN_TOKEN` | 国内版单账号 |
| `MODELSCOPE_INTL_TOKEN` | 国际版单账号 |
| `MODELSCOPE_PROXY` | HTTP(S)/SOCKS 代理 |
| `MODELSCOPE_VERIFY_DELAY` | 国内站账单回读间隔秒数，默认 `2` |
| `MODELSCOPE_NO_NOTIFY=1` | 关闭推送 |

示例：

```text
MODELSCOPE_CN_TOKENS=
国内主号|ms-xxxxxxxx
国内小号|ms-yyyyyyyy

MODELSCOPE_INTL_TOKENS=
国际主号|ms-zzzzzzzz
```

## 运行

```bash
python modelscope_daily.py
python modelscope_daily.py --only 1
python modelscope_daily.py --query
python modelscope_daily.py --no-notify
```

`--query` 同样会调用登录信息接口，因此也会触发签到。该接口本身就是签到机制，不存在完全只读的本地查询方式。

## 青龙

```bash
pip3 install requests
```

```text
30 8 * * * python3 modelscope_daily.py
```

## GitHub Actions

工作流位于 `.github/workflows/daily.yml`。配置：

- `MODELSCOPE_CN_TOKENS`
- `MODELSCOPE_INTL_TOKENS`
- 可选推送密钥

## 判定规则

- 响应同时兼容 `Code/Success/Data/Message` 与 `code/success/data/msg`。
- HTTP `401` 表示令牌失效或站点不匹配；HTTP `403` 是魔搭风控拦截，不等同于登录失效。
- 余额响应必须包含 `data` 与 `available_balance`；缺少字段或没有 ModelScope 响应信封时按查询失败处理，不会显示成 0 余额。
- 国内站会读取 `/openapi/v1/magicubes/transactions`，只有当日 `type=EARN` 且 `rule_key=daily_active / aliyun_bindlogin` 的账单存在时才确认到账；初次为空会在 `MODELSCOPE_VERIFY_DELAY` 秒后复查一次。
- 国内站未查到到账记录时显示“未确认”，不会把登录接口成功冒充为签到成功；国际站没有账单协议，保持登录触发口径。
- 余额接口失败会降级展示，不影响签到成功。

## 隐私

- 不收集、不上传账号数据；
- 日志不输出完整令牌；
- `.env` 与日志已加入 `.gitignore`。

## ☕ 支持与投喂

<p align="center">
  <img src="assets/donate-wechat.png" width="260" alt="微信赞赏码" />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="assets/donate-alipay.jpg" width="260" alt="支付宝收款码" />
</p>

## License

MIT
