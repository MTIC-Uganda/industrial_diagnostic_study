"""Tests for scripts/midd_notify.py (ADR-018).

The notifier must be OPT-IN (silent unless MIDD_NOTIFY is truthy) and FAIL-SAFE
(never raises, swallows any bridge error) so it can be wired into the live upload
pipeline without ever slowing or breaking an ingestion.
"""
import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
import midd_notify as mn  # noqa: E402


class _FakeResp:
    """Minimal context-manager stand-in for an http response."""

    def __init__(self, status=200):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_disabled_by_default(monkeypatch):
    monkeypatch.delenv("MIDD_NOTIFY", raising=False)
    calls = []
    monkeypatch.setattr(mn.urllib.request, "urlopen", lambda *a, **k: calls.append(1))
    assert mn.notify_group("hi") is False
    assert calls == []  # disabled -> never touches the network


@pytest.mark.parametrize(
    "val,expected",
    [("1", True), ("true", True), ("YES", True), ("on", True),
     ("0", False), ("", False), ("off", False), ("no", False)],
)
def test_enabled_flag(monkeypatch, val, expected):
    monkeypatch.setenv("MIDD_NOTIFY", val)
    assert mn.enabled() is expected


def test_sends_correct_payload(monkeypatch):
    monkeypatch.setenv("MIDD_NOTIFY", "1")
    monkeypatch.setenv("MIDD_GROUP_JID", "grp@g.us")
    monkeypatch.setenv("MIDD_BRIDGE_URL", "http://bridge/api/send")
    captured = {}

    def fake_urlopen(req, timeout=10):
        captured["url"] = req.full_url
        captured["method"] = req.get_method()
        captured["headers"] = req.headers
        captured["body"] = json.loads(req.data.decode())
        return _FakeResp(200)

    monkeypatch.setattr(mn.urllib.request, "urlopen", fake_urlopen)
    assert mn.notify_group("hello team") is True
    assert captured["url"] == "http://bridge/api/send"
    assert captured["method"] == "POST"
    assert captured["body"] == {"recipient": "grp@g.us", "message": "hello team"}


def test_custom_recipient_overrides_env(monkeypatch):
    monkeypatch.setenv("MIDD_NOTIFY", "1")
    monkeypatch.setenv("MIDD_GROUP_JID", "grp@g.us")
    captured = {}

    def fake_urlopen(req, timeout=10):
        captured.update(json.loads(req.data.decode()))
        return _FakeResp(200)

    monkeypatch.setattr(mn.urllib.request, "urlopen", fake_urlopen)
    mn.notify_group("hi", recipient="someone@s.whatsapp.net")
    assert captured["recipient"] == "someone@s.whatsapp.net"


def test_non_2xx_returns_false(monkeypatch):
    monkeypatch.setenv("MIDD_NOTIFY", "1")
    monkeypatch.setattr(mn.urllib.request, "urlopen", lambda *a, **k: _FakeResp(500))
    assert mn.notify_group("hi") is False


def test_never_raises_on_error(monkeypatch):
    monkeypatch.setenv("MIDD_NOTIFY", "1")

    def boom(*a, **k):
        raise OSError("bridge down")

    monkeypatch.setattr(mn.urllib.request, "urlopen", boom)
    assert mn.notify_group("hi") is False  # swallowed, not raised
