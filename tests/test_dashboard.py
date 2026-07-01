from toolkit.dashboard import build_dashboard_data


def _config():
    return {
        "model": {
            "provider": "openrouter",
            "name": "qwen/qwen3-coder",
        },
        "agent": {
            "max_turns": 30,
        },
        "max_live_sessions": 4,
        "context_file_max_chars": 50000,
        "file_read_max_chars": 80000,
        "compression": {
            "protect_last_n": 8,
        },
        "display": {
            "resume_exchanges": 6,
        },
        "session_reset": {
            "mode": "idle",
            "idle_minutes": 30,
            "at_hour": None,
        },
    }


def test_build_dashboard_data_shape():
    calls = [
        {
            "num": 1,
            "provider": "openrouter",
            "model": "qwen/qwen3-coder",
            "in": 1000,
            "out": 100,
            "total": 1100,
            "pct": 90,
        },
        {
            "num": 2,
            "provider": "openrouter",
            "model": "qwen/qwen3-coder",
            "in": 3000,
            "out": 300,
            "total": 3300,
            "pct": 95,
        },
    ]

    data = build_dashboard_data(_config(), calls)

    assert data["model"]["provider"] == "openrouter"
    assert data["provider_label"] == "OpenRouter"
    assert data["calls"] == calls
    assert data["latest"] == calls[-1]
    assert data["avg_in"] == 2000
    assert data["avg_out"] == 200
    assert data["avg_cache"] == 92.5
    assert data["prompt_status"] == "Controlled"
    assert data["prompt_class"] == "good"
    assert data["cache_status"] == "Good"
    assert data["cache_class"] == "good"
    assert data["health_status"] == "Excellent"
    assert data["health_class"] == "good"
    assert data["settings"]["max_turns"] == 30
    assert data["settings"]["protect_last_n"] == 8
    assert data["settings"]["resume_exchanges"] == 6


def test_build_dashboard_data_flags_heavy_usage_and_missing_limits():
    cfg = _config()
    cfg["session_reset"]["mode"] = "none"
    cfg["context_file_max_chars"] = None

    calls = [
        {
            "num": 1,
            "provider": "openrouter",
            "model": "heavy/model",
            "in": 120000,
            "out": 1000,
            "total": 121000,
            "pct": 40,
        },
    ]

    data = build_dashboard_data(cfg, calls)

    assert data["prompt_status"] == "High"
    assert data["prompt_class"] == "bad"
    assert data["cache_status"] == "Low"
    assert data["cache_class"] == "bad"
    assert data["health_score"] == 20
    assert data["health_status"] == "Poor"
    assert data["health_class"] == "bad"


def test_build_dashboard_data_handles_no_calls():
    data = build_dashboard_data(_config(), [])

    assert data["calls"] == []
    assert data["latest"] is None
    assert data["avg_in"] == 0
    assert data["avg_out"] == 0
    assert data["avg_cache"] == 0
    assert data["prompt_status"] == "Controlled"
    assert data["cache_status"] == "Low"
