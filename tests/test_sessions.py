from toolkit.sessions import build_sessions_data


def _dashboard_data():
    return {
        "settings": {
            "max_turns": 30,
            "max_live_sessions": 4,
            "protect_last_n": 8,
            "resume_exchanges": 6,
        },
        "session_reset_mode": "idle",
        "session_reset_idle": 30,
        "session_reset_hour": None,
    }


def test_build_sessions_data_shape():
    calls = [
        {
            "num": 1,
            "provider": "openrouter",
            "model": "qwen/qwen3-coder",
            "in": 1000,
            "out": 200,
            "total": 1200,
            "pct": 90,
        },
        {
            "num": 2,
            "provider": "openrouter",
            "model": "qwen/qwen3-coder",
            "in": 2000,
            "out": 300,
            "total": 2300,
            "pct": 95,
        },
    ]

    data = build_sessions_data(_dashboard_data(), {}, calls)
    sessions_page = data["sessions_page"]

    assert sessions_page["cards"]
    assert sessions_page["recommendations"]
    assert sessions_page["recent_calls"]
    assert sessions_page["activity_status"] == "Healthy"
    assert sessions_page["activity_class"] == "good"
    assert sessions_page["total_calls"] == 2
    assert sessions_page["total_input"] == 3000
    assert sessions_page["total_output"] == 500
    assert sessions_page["total_tokens"] == 3500
    assert sessions_page["avg_cache"] == 92.5


def test_build_sessions_data_warns_on_no_activity():
    data = build_sessions_data(_dashboard_data(), {}, [])
    sessions_page = data["sessions_page"]

    assert sessions_page["activity_status"] == "No recent activity"
    assert sessions_page["activity_class"] == "warn"
    assert sessions_page["total_calls"] == 0
    assert sessions_page["recent_calls"] == []


def test_build_sessions_data_flags_high_limits():
    dashboard_data = {
        "settings": {
            "max_turns": 80,
            "max_live_sessions": 12,
            "protect_last_n": 20,
            "resume_exchanges": 10,
        },
        "session_reset_mode": "none",
        "session_reset_idle": None,
        "session_reset_hour": None,
    }

    data = build_sessions_data(dashboard_data, {}, [])
    sessions_page = data["sessions_page"]

    assert any(card["severity"] == "warn" for card in sessions_page["cards"])
    assert any(
        item["title"] == "Enable idle session reset"
        for item in sessions_page["recommendations"]
    )
    assert any(
        item["title"] == "Reduce max live sessions"
        for item in sessions_page["recommendations"]
    )
    assert any(
        item["title"] == "Review max turns"
        for item in sessions_page["recommendations"]
    )


def test_build_sessions_data_filters_recent_calls_by_provider():
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
            "provider": "openai-codex",
            "model": "gpt-5.5",
            "in": 2000,
            "out": 200,
            "total": 2200,
            "pct": 80,
        },
    ]

    data = build_sessions_data(_dashboard_data(), {}, calls, provider="openrouter")
    sessions_page = data["sessions_page"]

    assert sessions_page["selected_provider"] == "openrouter"
    assert sessions_page["provider_options"] == ["openai-codex", "openrouter"]
    assert sessions_page["recent_call_count"] == 1
    assert sessions_page["recent_calls"][0]["provider"] == "openrouter"


def test_build_sessions_data_filters_recent_calls_by_search_query():
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
            "provider": "openai-codex",
            "model": "gpt-5.5",
            "in": 2000,
            "out": 200,
            "total": 2200,
            "pct": 80,
        },
    ]

    data = build_sessions_data(_dashboard_data(), {}, calls, query="gpt")
    sessions_page = data["sessions_page"]

    assert sessions_page["search_query"] == "gpt"
    assert sessions_page["recent_call_count"] == 1
    assert sessions_page["recent_calls"][0]["model"] == "gpt-5.5"


def test_build_sessions_data_rejects_unknown_provider_filter():
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
    ]

    data = build_sessions_data(_dashboard_data(), {}, calls, provider="missing")
    sessions_page = data["sessions_page"]

    assert sessions_page["selected_provider"] == "all"
    assert sessions_page["recent_call_count"] == 1
