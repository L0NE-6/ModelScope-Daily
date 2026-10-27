import importlib.util
import os
import unittest
from pathlib import Path
from unittest.mock import patch


SOURCE_PATH = Path(__file__).resolve().parents[1] / "modelscope_daily.py"
SPEC = importlib.util.spec_from_file_location("modelscope_daily", SOURCE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self.payload = payload

    def json(self):
        return self.payload


class StubClient(MODULE.ModelScopeClient):
    def __init__(self, region, daily_sequence=None, login_payload=None):
        self.region = region
        self.config = MODULE.REGIONS[region]
        self.name = "测试账号"
        self.daily_sequence = list(daily_sequence or [])
        self.login_payload = login_payload or {
            "success": True,
            "data": {"NickName": "单走一个6"},
        }

    def login_info(self):
        return self.login_payload

    def daily_earn(self):
        return self.daily_sequence.pop(0) if self.daily_sequence else []

    def balance(self):
        return {"available": 250, "total": 250, "frozen": 0}

    def used_today(self):
        return None


class ModelScopeCoreTests(unittest.TestCase):
    def setUp(self):
        self.old_delay = os.environ.get("MODELSCOPE_VERIFY_DELAY")
        os.environ["MODELSCOPE_VERIFY_DELAY"] = "0"

    def tearDown(self):
        if self.old_delay is None:
            os.environ.pop("MODELSCOPE_VERIFY_DELAY", None)
        else:
            os.environ["MODELSCOPE_VERIFY_DELAY"] = self.old_delay

    def test_daily_records_filter_rule_type_and_server_day(self):
        records = [
            {"type": "EARN", "gmt_created": "2026-10-23 10:00:00",
             "rule_key": "daily_active", "total_amount": 200},
            {"type": "EARN", "gmt_created": "2026-10-23 10:01:00",
             "rule_key": "aliyun_bindlogin", "total_amount": 50},
            {"type": "EARN", "gmt_created": "2026-10-22 10:00:00",
             "rule_key": "daily_active", "total_amount": 200},
            {"type": "SPEND_CONFIRM", "gmt_created": "2026-10-23 10:02:00",
             "rule_key": "daily_active", "total_amount": 20},
            {"type": "EARN", "gmt_created": "2026-10-23 10:03:00",
             "rule_key": "other", "total_amount": 999},
        ]
        selected = MODULE.daily_records_for_day(records, "2026-10-23")
        self.assertEqual(2, len(selected))
        self.assertEqual(250, sum(row["total_amount"] for row in selected))

    def test_cn_run_confirms_from_transaction_ledger(self):
        client = StubClient("cn", daily_sequence=[
            [],
            [{"type": "EARN", "gmt_created": MODULE.today_cn(),
              "rule_key": "daily_active", "total_amount": 200,
              "title": "注册并登录"}],
        ])
        confirmed, message = client.run()
        self.assertTrue(confirmed)
        self.assertIn("签到到账 200 魔粒", message)
        self.assertIn("注册并登录", message)

    def test_cn_run_does_not_claim_success_without_ledger_record(self):
        client = StubClient("cn", daily_sequence=[[], [], []])
        confirmed, message = client.run()
        self.assertFalse(confirmed)
        self.assertIn("未查到到账记录", message)

    def test_intl_run_keeps_login_only_confirmation(self):
        client = StubClient("intl", login_payload={
            "success": True,
            "data": {"NickName": "国际账号"},
        })
        confirmed, message = client.run()
        self.assertTrue(confirmed)
        self.assertIn("国际站无账单回读", message)

    def test_http_401_is_auth_failure(self):
        client = MODULE.ModelScopeClient("cn", {"name": "测试账号", "token": "ms-test"})
        with patch.object(client.session, "get", return_value=FakeResponse(401, {})):
            with self.assertRaises(MODULE.ModelScopeAuthError) as caught:
                client.get("/api/v1/users/login/info", "每日签到")
        self.assertIn("HTTP 401", str(caught.exception))
        self.assertIn("令牌失效", str(caught.exception))

    def test_http_403_is_risk_control_not_login_death(self):
        client = MODULE.ModelScopeClient("cn", {"name": "测试账号", "token": "ms-test"})
        with patch.object(client.session, "get", return_value=FakeResponse(403, {})):
            with self.assertRaises(MODULE.ModelScopeRiskControlError) as caught:
                client.get("/api/v1/users/login/info", "每日签到")
        message = str(caught.exception)
        self.assertIn("HTTP 403", message)
        self.assertIn("风控", message)
        self.assertNotIn("令牌失效", message)

    def test_balance_missing_data_is_an_error_not_zero(self):
        client = MODULE.ModelScopeClient("cn", {"name": "测试账号", "token": "ms-test"})
        with patch.object(client, "get", return_value={"success": True}):
            with self.assertRaises(MODULE.ModelScopeError) as caught:
                client.balance()
        self.assertIn("缺少 data", str(caught.exception))

    def test_balance_non_envelope_is_an_error(self):
        client = MODULE.ModelScopeClient("cn", {"name": "测试账号", "token": "ms-test"})
        with patch.object(client, "get", return_value={"unexpected": "proxy page"}):
            with self.assertRaises(MODULE.ModelScopeError) as caught:
                client.balance()
        self.assertIn("上游返回失败", str(caught.exception))

    def test_balance_non_dict_json_is_an_error(self):
        client = MODULE.ModelScopeClient("cn", {"name": "测试账号", "token": "ms-test"})
        with patch.object(client, "get", return_value=[]):
            with self.assertRaises(MODULE.ModelScopeError) as caught:
                client.balance()
        self.assertIn("上游返回失败", str(caught.exception))

    def test_balance_zero_is_still_a_valid_balance(self):
        client = MODULE.ModelScopeClient("cn", {"name": "测试账号", "token": "ms-test"})
        with patch.object(client, "get", return_value={
            "success": True,
            "data": {"available_balance": 0, "total_balance": 0, "frozen_amount": 0},
        }):
            wallet = client.balance()
        self.assertEqual(0, wallet["available"])
        self.assertEqual(0, wallet["total"])

    def test_transactions_readback_is_preserved(self):
        records = [
            {"type": "EARN", "gmt_created": "2026-10-27 09:00:00",
             "rule_key": "daily_active", "total_amount": 200},
        ]
        client = MODULE.ModelScopeClient("cn", {"name": "测试账号", "token": "ms-test"})
        with patch.object(client, "get", return_value={
            "success": True,
            "data": {"records": records},
        }):
            self.assertEqual(records, client.transactions())


if __name__ == "__main__":
    unittest.main()
