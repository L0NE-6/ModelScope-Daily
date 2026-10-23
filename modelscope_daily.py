#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ModelScope（魔搭）国内版 / 国际版每日签到

签到方式：
  GET /api/v1/users/login/info，调用本身触发当日魔粒签到，重复调用幂等。

环境变量：
  MODELSCOPE_CN_TOKENS    国内版多账号，换行或 & 分隔：备注|ms-token
  MODELSCOPE_INTL_TOKENS  国际版多账号，换行或 & 分隔：备注|ms-token
  MODELSCOPE_CN_TOKEN     国内版单账号
  MODELSCOPE_INTL_TOKEN   国际版单账号
  MODELSCOPE_PROXY        代理
  MODELSCOPE_VERIFY_DELAY 国内站账单回读前的等待秒数（默认 2）
  MODELSCOPE_NO_NOTIFY=1  关闭推送

命令：
  python modelscope_daily.py
  python modelscope_daily.py --query
  python modelscope_daily.py --only 1
  python modelscope_daily.py --no-notify

依赖：requests
"""

import os
import re
import sys
import time

import requests
import urllib3

urllib3.disable_warnings()

try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass

REGIONS = {
    "cn": {
        "label": "国内版",
        "site": "https://modelscope.cn",
        "tokens_env": "MODELSCOPE_CN_TOKENS",
        "token_env": "MODELSCOPE_CN_TOKEN",
    },
    "intl": {
        "label": "国际版",
        "site": "https://www.modelscope.ai",
        "tokens_env": "MODELSCOPE_INTL_TOKENS",
        "token_env": "MODELSCOPE_INTL_TOKEN",
    },
}
LOGIN_INFO_PATH = "/api/v1/users/login/info"
BALANCE_PATH = "/openapi/v1/magicubes/balance"
TRANSACTIONS_PATH = "/openapi/v1/magicubes/transactions"
RATE_LIMIT_PATH = "/api/v1/inference/rate-limit"
DAILY_RULES = ("daily_active", "aliyun_bindlogin")


class ModelScopeError(Exception):
    pass


def log(message):
    print(str(message), flush=True)


def first_text(record, keys):
    for key in keys:
        value = record.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def parse_accounts(env_name, single_env):
    accounts = []
    raw = os.getenv(env_name, "").strip()
    if raw:
        for line in re.split(r"[\r\n&]+", raw):
            line = line.strip()
            if not line:
                continue
            if "|" in line:
                name, token = line.split("|", 1)
            else:
                name, token = "", line
            token = token.strip()
            if token:
                accounts.append(
                    {"name": name.strip() or ("账号%d" % (len(accounts) + 1)), "token": token}
                )
    if not accounts:
        token = os.getenv(single_env, "").strip()
        if token:
            accounts.append({"name": "账号1", "token": token})
    return accounts


def envelope_data(payload):
    value = payload.get("Data", payload.get("data"))
    return value if isinstance(value, dict) else {}


def envelope_message(payload):
    return str(
        payload.get("Message")
        or payload.get("message")
        or payload.get("msg")
        or ""
    ).strip()


def envelope_ok(payload):
    if "Success" in payload and isinstance(payload.get("Success"), bool):
        return payload["Success"]
    if "success" in payload and isinstance(payload.get("success"), bool):
        return payload["success"]
    code = payload.get("Code", payload.get("code"))
    if code is None:
        return True
    try:
        return int(code) == 200
    except Exception:
        return False


def today_cn():
    """ModelScope 账单使用北京时间自然日，不依赖宿主机时区。"""
    return time.strftime("%Y-%m-%d", time.gmtime(time.time() + 8 * 3600))


def daily_records_for_day(records, day):
    result = []
    for record in records if isinstance(records, list) else []:
        if not isinstance(record, dict):
            continue
        if str(record.get("type") or "").upper() != "EARN":
            continue
        if str(record.get("gmt_created") or "")[:10] != day:
            continue
        if str(record.get("rule_key") or "").lower() not in DAILY_RULES:
            continue
        result.append(record)
    return result


class ModelScopeClient:
    def __init__(self, region, account):
        self.region = region
        self.config = REGIONS[region]
        self.name = account["name"]
        self.token = account["token"]
        self.session = requests.Session()
        self.session.verify = False
        proxy = os.getenv("MODELSCOPE_PROXY", "").strip()
        if proxy:
            self.session.proxies.update({"http": proxy, "https": proxy})

    def get(self, path, what):
        try:
            response = self.session.get(
                self.config["site"] + path,
                headers={"Cookie": "m_session_id=" + self.token},
                timeout=30,
            )
        except Exception as exc:
            raise ModelScopeError("%s失败：%s" % (what, exc))
        try:
            payload = response.json()
        except Exception:
            payload = {}
        if response.status_code in (401, 403):
            raise ModelScopeError(
                "%s：令牌失效或不属于%s站点（HTTP %s）"
                % (what, self.config["label"], response.status_code)
            )
        if response.status_code < 200 or response.status_code >= 300:
            raise ModelScopeError("%s失败 HTTP %s" % (what, response.status_code))
        return payload

    def login_info(self):
        return self.get(LOGIN_INFO_PATH, "每日签到")

    def balance(self):
        payload = self.get(BALANCE_PATH, "魔粒余额查询")
        if not envelope_ok(payload):
            raise ModelScopeError(
                "魔粒余额查询失败：%s" % (envelope_message(payload) or "上游返回失败")
            )
        data = envelope_data(payload)
        return {
            "available": data.get("available_balance", 0),
            "total": data.get("total_balance"),
            "frozen": data.get("frozen_amount", 0),
        }

    def used_today(self):
        try:
            payload = self.get(RATE_LIMIT_PATH, "今日用量查询")
            if not envelope_ok(payload):
                return None
            value = envelope_data(payload).get("currentUsagePerDay")
            return value
        except Exception:
            return None

    def transactions(self):
        payload = self.get(
            TRANSACTIONS_PATH + "?page=1&page_size=50", "魔粒账单查询")
        if not envelope_ok(payload):
            raise ModelScopeError(
                "魔粒账单查询失败：%s"
                % (envelope_message(payload) or "上游返回失败"))
        data = envelope_data(payload)
        records = data.get("records")
        if records is None:
            return []
        if not isinstance(records, list):
            raise ModelScopeError("魔粒账单格式异常：records 不是列表")
        return records

    def daily_earn(self):
        return daily_records_for_day(self.transactions(), today_cn())

    def run(self, query_only=False):
        before = []
        before_error = ""
        if self.region == "cn":
            try:
                before = self.daily_earn()
            except Exception as exc:
                before_error = str(exc)[:120]

        payload = self.login_info()
        if not envelope_ok(payload):
            raise ModelScopeError(
                "每日签到失败：%s" % (envelope_message(payload) or "上游返回失败")
            )
        identity = envelope_data(payload)
        display = first_text(
            identity, ("NickName", "Name", "nickname", "name", "HavanaId")
        )
        parts = []
        confirmed = True
        if self.region == "cn":
            daily = list(before)
            after_error = ""
            if not daily:
                try:
                    daily = self.daily_earn()
                    if not daily:
                        try:
                            delay = max(
                                0, int(os.getenv("MODELSCOPE_VERIFY_DELAY", "2")))
                        except ValueError:
                            delay = 2
                        if delay:
                            time.sleep(delay)
                        daily = self.daily_earn()
                except Exception as exc:
                    after_error = str(exc)[:120]
            credit = sum(
                float(record.get("total_amount") or 0)
                for record in daily
                if isinstance(record, dict)
            )
            if daily:
                titles = [
                    str(record.get("title") or record.get("rule_key") or "").strip()
                    for record in daily if isinstance(record, dict)
                ]
                titles = [title for title in titles if title]
                label = "今日已领取" if before else "签到到账"
                parts.append("%s %s 魔粒%s" % (
                    label, int(credit) if credit == int(credit) else credit,
                    "（%s）" % " + ".join(titles) if titles else ""))
            else:
                confirmed = False
                why = after_error or before_error
                parts.append(
                    "登录已触达，但今日未查到到账记录%s"
                    % ("（账单查询失败：%s）" % why if why else
                       "（账号可能不在活动范围）"))
        elif query_only:
            parts.append("登录态有效")
        else:
            parts.append("每日签到已触发（国际站无账单回读）")
        if display:
            parts.append(display)
        try:
            wallet = self.balance()
            parts.append("可用魔粒 %s" % wallet["available"])
            if wallet["total"] is not None:
                parts.append("总计 %s" % wallet["total"])
        except Exception as exc:
            parts.append("余额查询失败：%s" % str(exc)[:80])
        used = self.used_today()
        if used is not None:
            parts.append("今日已用 %s 次" % used)
        return confirmed, "；".join(parts)


def post_json(url, payload):
    try:
        response = requests.post(url, json=payload, timeout=15, verify=False)
        response.raise_for_status()
        return True
    except Exception as exc:
        log("推送失败：%s" % exc)
        return False


def notify(text, title="ModelScope 每日签到"):
    if os.getenv("MODELSCOPE_NO_NOTIFY", "").strip() == "1":
        return
    content = text[:1800]
    token = os.getenv("PLUSPLUS_TOKEN", "").strip()
    if token:
        post_json(
            "https://www.pushplus.plus/send",
            {"token": token, "title": title, "content": content, "template": "txt"},
        )
    bark = os.getenv("BARK_URL", "").strip()
    if bark:
        post_json(
            bark.rstrip("/") + "/" + requests.utils.quote(title, safe=""),
            {"body": content},
        )
    wecom = os.getenv("WECOM_WEBHOOK", "").strip() or os.getenv("QYWX_TOKEN", "").strip()
    if wecom:
        if "key=" not in wecom and "/send?" not in wecom:
            wecom = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=" + wecom
        post_json(wecom, {"msgtype": "text", "text": {"content": title + "\n" + content}})
    ding = os.getenv("DINGTALK_WEBHOOK", "").strip()
    if ding:
        post_json(ding, {"msgtype": "text", "text": {"content": title + "\n" + content}})


def main():
    only = ""
    query_only = False
    no_notify = os.getenv("MODELSCOPE_NO_NOTIFY", "").strip() == "1"
    args = sys.argv[1:]
    for index, arg in enumerate(args):
        if arg == "--only" and index + 1 < len(args):
            only = args[index + 1]
        elif arg == "--query":
            query_only = True
        elif arg == "--no-notify":
            no_notify = True

    jobs = []
    for region in ("cn", "intl"):
        config = REGIONS[region]
        for account in parse_accounts(config["tokens_env"], config["token_env"]):
            jobs.append((region, account))
    if not jobs:
        log("未配置 MODELSCOPE_CN_TOKENS 或 MODELSCOPE_INTL_TOKENS。")
        return 1

    lines = []
    succeeded = 0
    selected = 0
    for index, (region, account) in enumerate(jobs, 1):
        if only and str(index) != str(only):
            continue
        selected += 1
        client = ModelScopeClient(region, account)
        label = "%s/%s" % (client.config["label"], client.name)
        try:
            confirmed, message = client.run(query_only=query_only)
            if confirmed:
                succeeded += 1
                line = "成功 %s：%s" % (label, message)
            else:
                line = "未确认 %s：%s" % (label, message)
        except Exception as exc:
            line = "失败 %s：%s" % (label, str(exc)[:240])
        lines.append(line)
        log(line)
        if index < len(jobs):
            time.sleep(1.0)
    if selected == 0:
        log("没有匹配的账号")
        return 1
    summary = "\n".join(lines)
    log("\n===== ModelScope 签到汇总 =====\n" + summary)
    if not no_notify:
        notify(summary)
    return 0 if succeeded else 1


if __name__ == "__main__":
    sys.exit(main())
