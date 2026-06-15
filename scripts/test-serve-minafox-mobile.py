#!/usr/bin/env python3
"""Unit tests for the MinaFox Android/LAN UX harness."""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS_PATH = ROOT / "scripts" / "serve-minafox-mobile.py"


def load_harness():
    spec = importlib.util.spec_from_file_location("serve_minafox_mobile", HARNESS_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["serve_minafox_mobile"] = module
    spec.loader.exec_module(module)
    return module


class MinaFoxMobileHarnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.harness = load_harness()

    def test_runtime_config_script_is_injected_before_start_page_script(self) -> None:
        config = self.harness.RuntimeConfig(
            ai_broker_url="http://192.0.2.10:8765",
            search_base_url="http://192.0.2.10:8888",
            mode="lan-test",
        )

        html = self.harness.render_start_page(config)

        self.assertIn("window.MINAFOX_RUNTIME_CONFIG", html)
        self.assertLess(html.index("window.MINAFOX_RUNTIME_CONFIG"), html.index("const actionStatus"))
        self.assertIn('"aiBrokerUrl": "http://192.0.2.10:8765"', html)
        self.assertIn('"searchBaseUrl": "http://192.0.2.10:8888"', html)
        self.assertIn('"searchActionUrl": "http://192.0.2.10:8888/search"', html)
        self.assertIn('"harnessUrl": "http://192.0.2.10:8766"', html)
        self.assertIn('"healthUrl": "http://192.0.2.10:8766/health"', html)
        self.assertIn('"androidChecklistUrl": "http://192.0.2.10:8766/android-checklist"', html)
        self.assertIn('"mode": "lan-test"', html)

    def test_runtime_config_rejects_non_http_urls(self) -> None:
        with self.assertRaises(ValueError):
            self.harness.RuntimeConfig(
                ai_broker_url="file:///tmp/broker",
                search_base_url="http://192.0.2.10:8888",
                mode="lan-test",
            )

    def test_health_payload_uses_configured_urls(self) -> None:
        config = self.harness.RuntimeConfig(
            ai_broker_url="http://localhost:8765",
            search_base_url="http://localhost:8888/",
            search_action_url="http://localhost:8888/search?language=auto",
            mode="desktop-local",
        )

        payload = self.harness.health_payload(config)

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["service"], "minafox-mobile-harness")
        self.assertEqual(payload["config"]["searchActionUrl"], "http://localhost:8888/search?language=auto")
        self.assertEqual(payload["config"]["healthUrl"], "http://127.0.0.1:8766/health")
        json.dumps(payload)

    def test_search_action_url_defaults_to_search_base_url(self) -> None:
        config = self.harness.RuntimeConfig(
            ai_broker_url="http://localhost:8765",
            search_base_url="http://localhost:8888/",
            mode="desktop-local",
        )

        self.assertEqual(config.as_dict()["searchActionUrl"], "http://localhost:8888/search")

    def test_config_payload_exposes_android_endpoints(self) -> None:
        config = self.harness.RuntimeConfig(
            ai_broker_url="http://192.0.2.20:8765",
            search_base_url="http://192.0.2.20:8888",
            mode="tailscale-test",
            harness_url="http://minafox-tail:8766",
        )

        payload = self.harness.config_payload(config)

        self.assertEqual(payload["config"]["harnessUrl"], "http://minafox-tail:8766")
        self.assertEqual(payload["config"]["healthUrl"], "http://minafox-tail:8766/health")
        self.assertEqual(payload["config"]["androidChecklistUrl"], "http://minafox-tail:8766/android-checklist")
        self.assertIn("trusted LAN/Tailscale", payload["warning"])

    def test_android_checklist_payload_is_phone_friendly(self) -> None:
        config = self.harness.RuntimeConfig(
            ai_broker_url="http://192.0.2.20:8765",
            search_base_url="http://192.0.2.20:8888",
            mode="lan-test",
            harness_url="http://192.0.2.20:8766",
        )

        payload = self.harness.android_checklist_payload(config)

        self.assertEqual(payload["service"], "minafox-mobile-harness")
        self.assertEqual(payload["url"], "http://192.0.2.20:8766/")
        self.assertGreaterEqual(len(payload["checklist"]), 5)
        self.assertTrue(any("360" in item for item in payload["checklist"]))
        self.assertTrue(any("127.0.0.1" in item for item in payload["checklist"]))

    def test_request_host_can_drive_phone_visible_harness_url(self) -> None:
        config = self.harness.RuntimeConfig(
            ai_broker_url="http://127.0.0.1:8765",
            search_base_url="http://127.0.0.1:8888",
            mode="lan-test",
        )

        request_config = self.harness.config_for_request(config, "192.0.2.55:8766")

        self.assertEqual(request_config.as_dict()["harnessUrl"], "http://192.0.2.55:8766")
        self.assertEqual(request_config.as_dict()["healthUrl"], "http://192.0.2.55:8766/health")

    def test_request_host_drives_search_and_ai_urls_for_lan_or_tailscale(self) -> None:
        config = self.harness.RuntimeConfig(
            ai_broker_url="http://192.168.31.67:8765",
            search_base_url="http://192.168.31.67:8888",
            search_action_url="http://192.168.31.67:8888/search",
            harness_url="http://192.168.31.67:8766",
            mode="tailscale-test",
        )

        request_config = self.harness.config_for_request(config, "100.64.12.34:8766")
        runtime = request_config.as_dict()

        self.assertEqual(runtime["harnessUrl"], "http://100.64.12.34:8766")
        self.assertEqual(runtime["healthUrl"], "http://100.64.12.34:8766/health")
        self.assertEqual(runtime["searchBaseUrl"], "http://100.64.12.34:8888")
        self.assertEqual(runtime["searchActionUrl"], "http://100.64.12.34:8888/search")
        self.assertEqual(runtime["aiBrokerUrl"], "http://100.64.12.34:8765")


if __name__ == "__main__":
    unittest.main(verbosity=2)
