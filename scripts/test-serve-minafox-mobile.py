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
        json.dumps(payload)

    def test_search_action_url_defaults_to_search_base_url(self) -> None:
        config = self.harness.RuntimeConfig(
            ai_broker_url="http://localhost:8765",
            search_base_url="http://localhost:8888/",
            mode="desktop-local",
        )

        self.assertEqual(config.as_dict()["searchActionUrl"], "http://localhost:8888/search")


if __name__ == "__main__":
    unittest.main(verbosity=2)
