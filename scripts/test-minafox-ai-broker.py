#!/usr/bin/env python3
"""Unit tests for the MinaFox local AI broker."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
BROKER_PATH = ROOT / "scripts" / "minafox-ai-broker.py"


def load_broker():
    spec = importlib.util.spec_from_file_location("minafox_ai_broker", BROKER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["minafox_ai_broker"] = module
    spec.loader.exec_module(module)
    return module


class MinaFoxAIBrokerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.broker = load_broker()

    def test_ollama_provider_is_enabled_only_when_local_tags_endpoint_responds(self) -> None:
        with mock.patch.object(self.broker, "ollama_request", return_value={"available": True, "models": ["llama3.1:8b"]}), \
             mock.patch.object(self.broker, "hermes_request", return_value={"available": False}):
            providers = self.broker.build_providers()

        ollama = next(provider for provider in providers if provider["id"] == "ollama")
        self.assertTrue(ollama["enabled"])
        self.assertTrue(ollama["available"])
        self.assertEqual(ollama["status"], "ready")
        self.assertEqual(ollama["models"], ["llama3.1:8b"])

    def test_ollama_chat_proxies_to_loopback_ollama_without_cloud_or_hermes(self) -> None:
        captured: dict[str, object] = {}

        def fake_ollama_request(path: str, payload: dict[str, object] | None = None, timeout: float = 20.0):
            captured["path"] = path
            captured["payload"] = payload
            return {
                "available": True,
                "data": {"message": {"content": "hej Mina 🌙"}, "done": True},
            }

        with mock.patch.dict(os.environ, {"MINAFOX_AI_ENABLE_OLLAMA_CHAT": "1"}, clear=False), \
             mock.patch.object(self.broker, "ollama_request", side_effect=fake_ollama_request):
            status, body = self.broker.handle_chat_payload({
                "provider": "ollama",
                "model": "llama3.1:8b",
                "prompt": "say hi",
            })

        self.assertEqual(status, 200)
        self.assertEqual(body["provider"], "ollama")
        self.assertEqual(body["message"], "hej Mina 🌙")
        self.assertEqual(captured["path"], "/api/chat")
        self.assertEqual(captured["payload"], {
            "model": "llama3.1:8b",
            "messages": [{"role": "user", "content": "say hi"}],
            "stream": False,
        })

    def test_ollama_chat_offline_returns_friendly_message(self) -> None:
        with mock.patch.dict(os.environ, {"MINAFOX_AI_ENABLE_OLLAMA_CHAT": "1"}, clear=False), \
             mock.patch.object(self.broker, "ollama_request", return_value={"available": False, "error": "ConnectionRefusedError"}):
            status, body = self.broker.handle_chat_payload({
                "provider": "ollama",
                "prompt": "say hi",
            })

        self.assertEqual(status, 503)
        self.assertEqual(body["error"], "ollama_unavailable")
        self.assertIn("Ollama is offline", body["message"])
        self.assertNotIn("ollama_unavailable", body["message"])

    def test_chat_rejects_hermes_gateway_even_when_chat_flag_is_enabled(self) -> None:
        with mock.patch.dict(os.environ, {"MINAFOX_AI_ENABLE_OLLAMA_CHAT": "1"}, clear=False):
            status, body = self.broker.handle_chat_payload({
                "provider": "hermes_gateway",
                "prompt": "run an agent",
            })

        self.assertEqual(status, 403)
        self.assertEqual(body["error"], "provider_disabled")
        self.assertIn("tool-capable", body["safety"])

    def test_chat_rejects_empty_or_oversized_prompt(self) -> None:
        status, body = self.broker.handle_chat_payload({"provider": "ollama", "prompt": "   "})
        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "invalid_prompt")

        status, body = self.broker.handle_chat_payload({"provider": "ollama", "prompt": "x" * (self.broker.MAX_PROMPT_CHARS + 1)})
        self.assertEqual(status, 413)
        self.assertEqual(body["error"], "prompt_too_large")


if __name__ == "__main__":
    unittest.main(verbosity=2)
