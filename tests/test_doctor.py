from toolkit.doctor import build_doctor_data


def test_build_doctor_data_shape():
    dashboard_data = {
        "model": {
            "provider": "openrouter",
            "default": "qwen/qwen3-coder",
        },
        "provider_label": "OpenRouter",
        "settings": {
            "max_turns": 30,
            "max_live_sessions": 4,
            "context_file_max_chars": 60000,
            "file_read_max_chars": 50000,
            "protect_last_n": 8,
            "resume_exchanges": 6,
        },
        "session_reset_mode": "idle",
        "session_reset_idle": 30,
        "avg_cache": 90.0,
        "avg_in": 25000.0,
    }

    cfg = {
        "model": {
            "provider": "openrouter",
            "default": "qwen/qwen3-coder",
        }
    }

    data = build_doctor_data(dashboard_data, cfg)

    assert data["doctor_checks"]
    assert data["doctor_categories"]
    assert data["doctor_summary"]
    assert data["recommendations"]
    assert data["diagnostic_generated_at"]

    assert set(data["doctor_summary"]) == {"good", "warn", "bad"}

    category_ids = [category["id"] for category in data["doctor_categories"]]
    assert category_ids == [
        "environment",
        "configuration",
        "runtime",
        "connectivity",
        "usage",
    ]

    check_count = len(data["doctor_checks"])
    summary_count = (
        data["doctor_summary"]["good"]
        + data["doctor_summary"]["warn"]
        + data["doctor_summary"]["bad"]
    )

    assert summary_count == check_count
    assert 0 <= data["health_score"] <= 100
    assert data["health_status"]
    assert data["health_class"] in {"good", "warn", "bad"}


def test_build_doctor_data_flags_missing_provider():
    dashboard_data = {
        "model": {},
        "provider_label": None,
        "settings": {
            "max_turns": 75,
            "max_live_sessions": 12,
            "context_file_max_chars": None,
            "file_read_max_chars": 120000,
            "protect_last_n": 20,
            "resume_exchanges": 0,
        },
        "session_reset_mode": "none",
        "session_reset_idle": None,
        "avg_cache": 20.0,
        "avg_in": 125000.0,
    }

    cfg = {}

    data = build_doctor_data(dashboard_data, cfg)

    assert data["doctor_summary"]["bad"] >= 1
    assert any(
        check["name"] == "Active Provider" and check["severity"] == "bad"
        for check in data["doctor_checks"]
    )
    assert any(
        item["title"] == "Select an active provider"
        for item in data["recommendations"]
    )


def test_build_doctor_data_checks_ollama_reachability(monkeypatch):
    class FakeResponse:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

    called = {}

    def fake_urlopen(url, timeout):
        called["url"] = url
        called["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("toolkit.doctor.urlopen", fake_urlopen)

    dashboard_data = {
        "model": {
            "provider": "ollama",
            "default": "llama3.1",
            "base_url": "http://127.0.0.1:11434",
        },
        "provider_label": "Ollama",
        "settings": {
            "max_turns": 30,
            "max_live_sessions": 4,
            "context_file_max_chars": 60000,
            "file_read_max_chars": 50000,
            "protect_last_n": 8,
            "resume_exchanges": 6,
        },
        "session_reset_mode": "idle",
        "session_reset_idle": 30,
        "avg_cache": 90.0,
        "avg_in": 25000.0,
    }

    data = build_doctor_data(dashboard_data, {})

    assert called["url"] == "http://127.0.0.1:11434/api/tags"
    assert any(
        check["name"] == "Ollama Reachability"
        and check["status"] == "Reachable"
        and check["severity"] == "good"
        for check in data["doctor_checks"]
    )


def test_build_doctor_data_warns_when_ollama_unreachable(monkeypatch):
    from urllib.error import URLError

    def fake_urlopen(url, timeout):
        raise URLError("connection refused")

    monkeypatch.setattr("toolkit.doctor.urlopen", fake_urlopen)

    dashboard_data = {
        "model": {
            "provider": "ollama",
            "default": "llama3.1",
            "base_url": "http://127.0.0.1:11434/",
        },
        "provider_label": "Ollama",
        "settings": {
            "max_turns": 30,
            "max_live_sessions": 4,
            "context_file_max_chars": 60000,
            "file_read_max_chars": 50000,
            "protect_last_n": 8,
            "resume_exchanges": 6,
        },
        "session_reset_mode": "idle",
        "session_reset_idle": 30,
        "avg_cache": 90.0,
        "avg_in": 25000.0,
    }

    data = build_doctor_data(dashboard_data, {})

    assert any(
        check["name"] == "Ollama Reachability"
        and check["status"] == "Not reachable"
        and check["severity"] == "warn"
        for check in data["doctor_checks"]
    )


def test_provider_connectivity_dispatcher_reports_configured_external_provider():
    from toolkit.doctor import _check_provider_connectivity

    result = _check_provider_connectivity(
        {"provider_label": "OpenRouter"},
        {
            "provider": "openrouter",
            "default_model": "qwen/qwen3-coder",
        },
    )

    assert result == {
        "name": "Provider Config",
        "status": "Configured",
        "value": "OpenRouter / qwen/qwen3-coder",
        "detail": "Provider and default model are configured. Live external API checks are intentionally not performed yet.",
        "severity": "good",
    }


def test_provider_connectivity_dispatcher_reports_incomplete_external_provider():
    from toolkit.doctor import _check_provider_connectivity

    result = _check_provider_connectivity(
        {"provider_label": "OpenRouter"},
        {
            "provider": "openrouter",
            "default_model": None,
        },
    )

    assert result == {
        "name": "Provider Config",
        "status": "Incomplete",
        "value": "OpenRouter / no default model",
        "detail": "Provider is selected, but no default model is configured.",
        "severity": "warn",
    }


def test_provider_connectivity_dispatcher_reports_missing_provider():
    from toolkit.doctor import _check_provider_connectivity

    result = _check_provider_connectivity(
        {"provider_label": None},
        {"provider": None},
    )

    assert result == {
        "name": "Provider Connectivity",
        "status": "Blocked",
        "value": "No provider",
        "detail": "Connectivity cannot be evaluated until a provider is selected.",
        "severity": "bad",
    }
