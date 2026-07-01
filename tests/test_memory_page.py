from toolkit.memory_page import build_memory_data, build_memory_inventory_items, classify_memory_signal


def _dashboard_data():
    return {
        "settings": {
            "context_file_max_chars": 50000,
            "file_read_max_chars": 80000,
            "protect_last_n": 10,
            "resume_exchanges": 4,
            "max_turns": 30,
            "max_live_sessions": 6,
        },
        "session_reset_mode": "idle",
        "session_reset_idle": 45,
    }


def test_classify_memory_signal():
    assert classify_memory_signal("ERROR context failed") == "bad"
    assert classify_memory_signal("WARNING cache slow") == "warn"
    assert classify_memory_signal("SESSION cache hit") == "good"
    assert classify_memory_signal("memory note") == "neutral"


def test_build_memory_data_shape_and_efficient_status(tmp_path):
    log_path = tmp_path / "hermes.log"
    log_path.write_text(
        "\n".join(
            [
                "INFO cache hit",
                "INFO session resumed",
                "WARNING context growth",
            ]
        )
    )

    calls = [
        {
            "in": 1000,
            "out": 100,
            "total": 1100,
            "cache": 900,
            "pct": 90,
        },
        {
            "in": 2000,
            "out": 200,
            "total": 2200,
            "cache": 1800,
            "pct": 90,
        },
    ]

    data = build_memory_data(_dashboard_data(), calls, log_path)
    memory_page = data["memory_page"]

    assert memory_page["status"] == "Efficient"
    assert memory_page["status_class"] == "good"
    assert memory_page["avg_input"] == 1500
    assert memory_page["avg_cache"] == 90
    assert memory_page["total_cached_tokens"] == 2700
    assert memory_page["signal_count"] == 3
    assert len(memory_page["cards"]) == 3
    assert memory_page["planned_areas"]
    assert memory_page["session_reset_mode"] == "idle"
    assert memory_page["session_reset_idle"] == 45
    assert memory_page["context_file_max_chars"] == 50000
    assert memory_page["file_read_max_chars"] == 80000


def test_build_memory_data_warns_on_high_context_settings(tmp_path):
    log_path = tmp_path / "missing.log"
    dashboard = {
        "settings": {
            "context_file_max_chars": 120000,
            "file_read_max_chars": 200000,
            "protect_last_n": 25,
            "resume_exchanges": 12,
            "max_turns": 80,
            "max_live_sessions": 20,
        },
        "session_reset_mode": "none",
        "session_reset_idle": 0,
    }
    calls = [
        {
            "in": 70000,
            "out": 100,
            "total": 70100,
            "cache": 10000,
            "pct": 40,
        }
    ]

    data = build_memory_data(dashboard, calls, log_path)
    memory_page = data["memory_page"]

    assert memory_page["status"] == "Inefficient"
    assert memory_page["status_class"] == "bad"

    titles = {item["title"] for item in memory_page["recommendations"]}

    assert "Improve context reuse" in titles
    assert "Watch prompt growth" in titles
    assert "Use idle session reset" in titles
    assert "Review protected context depth" in titles
    assert "Reduce resume exchanges" in titles

    card_values = {card["title"]: card["severity"] for card in memory_page["cards"]}

    assert card_values["Protected Context"] == "warn"
    assert card_values["Resume Exchanges"] == "warn"
    assert card_values["Context File Limit"] == "warn"


def test_build_memory_data_handles_no_calls_or_log(tmp_path):
    log_path = tmp_path / "missing.log"

    data = build_memory_data({}, [], log_path)
    memory_page = data["memory_page"]

    assert memory_page["status"] == "Inefficient"
    assert memory_page["status_class"] == "bad"
    assert memory_page["avg_input"] == 0
    assert memory_page["avg_cache"] == 0
    assert memory_page["total_cached_tokens"] == 0
    assert memory_page["signal_lines"] == []
    assert memory_page["signal_count"] == 0
    assert "read-only" in memory_page["note"]

def test_build_memory_inventory_items_marks_available_sources():
    items = build_memory_inventory_items(
        context_file_max_chars=50000,
        file_read_max_chars=80000,
        protect_last_n=10,
        resume_exchanges=4,
        signal_count=3,
        total_calls=2,
    )

    by_name = {item["name"]: item for item in items}

    assert by_name["Configuration Snapshot"]["status"] == "available"
    assert by_name["Cache Signals"]["status"] == "available"
    assert by_name["Context Log Signals"]["status"] == "available"
    assert by_name["Memory Store Inventory"]["status"] == "planned"


def test_build_memory_inventory_items_marks_limited_sources():
    items = build_memory_inventory_items(
        context_file_max_chars=0,
        file_read_max_chars=0,
        protect_last_n=0,
        resume_exchanges=0,
        signal_count=0,
        total_calls=0,
    )

    by_name = {item["name"]: item for item in items}

    assert by_name["Configuration Snapshot"]["status"] == "limited"
    assert by_name["Cache Signals"]["status"] == "limited"
    assert by_name["Context Log Signals"]["status"] == "limited"
    assert by_name["Memory Store Inventory"]["status"] == "planned"


def test_build_memory_data_includes_inventory_foundation(tmp_path):
    log_path = tmp_path / "hermes.log"
    log_path.write_text("INFO memory cache session context")

    calls = [
        {
            "in": 1000,
            "out": 100,
            "total": 1100,
            "cache": 900,
            "pct": 90,
        },
    ]

    data = build_memory_data(_dashboard_data(), calls, log_path)
    memory_page = data["memory_page"]

    assert memory_page["inventory_count"] == 4
    assert memory_page["available_inventory_count"] == 3
    assert memory_page["inventory_items"][0]["name"] == "Configuration Snapshot"

