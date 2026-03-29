# -*- coding: utf-8 -*-
"""Smoke tests for Agent Reach web UI."""

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from agent_reach.web.main import CommandResult, app


@pytest.fixture
def client(monkeypatch):
    sample_results = {
        "web": {
            "status": "ok",
            "name": "Web",
            "message": "Ready",
            "tier": 0,
            "backends": ["jina"],
        },
        "exa_search": {
            "status": "warn",
            "name": "Exa",
            "message": "Needs setup",
            "tier": 1,
            "backends": ["mcporter"],
        },
    }

    monkeypatch.setattr("agent_reach.web.main.AgentReach.doctor", lambda self: sample_results)
    return TestClient(app)


def test_index_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Agent Reach Control Deck" in response.text
    assert "Doctor Dashboard" in response.text


def test_index_renders_turkish(client):
    response = client.get("/?lang=tr")
    assert response.status_code == 200
    assert "Agent Reach Kontrol Paneli" in response.text
    assert "Durum Panosu" in response.text


def test_api_doctor_returns_json(client):
    response = client.get("/api/doctor")
    assert response.status_code == 200
    payload = response.json()
    assert "web" in payload
    assert payload["web"]["status"] == "ok"


def test_configure_requires_value(client):
    response = client.post("/ui/actions/configure", data={"key": "proxy", "value": ""})
    assert response.status_code == 200
    assert "Configuration value is required" in response.text


def test_configure_requires_value_turkish(client):
    response = client.post(
        "/ui/actions/configure",
        data={"key": "proxy", "value": "", "lang": "tr"},
    )
    assert response.status_code == 200
    assert "Yapılandırma değeri zorunludur" in response.text


def test_install_action_uses_cli_runner(client, monkeypatch):
    def fake_run(_args):
        return CommandResult(
            command="python -m agent_reach.cli install --env=auto --dry-run",
            return_code=0,
            stdout="ok",
            stderr="",
        )

    monkeypatch.setattr("agent_reach.web.main._run_cli", fake_run)

    response = client.post(
        "/ui/actions/install",
        data={"env": "auto", "dry_run": "on", "refresh_doctor": "on"},
    )
    assert response.status_code == 200
    assert "Install completed" in response.text
    assert "Exit code" in response.text
    assert "hx-swap-oob" in response.text
