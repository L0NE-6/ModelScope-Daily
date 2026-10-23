import importlib.util
import os
import unittest
from pathlib import Path


SOURCE_PATH = Path(__file__).resolve().parents[1] / "modelscope_daily.py"
SPEC = importlib.util.spec_from_file_location("modelscope_daily", SOURCE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


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


if __name__ == "__main__":
    unittest.main()
