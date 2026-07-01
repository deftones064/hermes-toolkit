from toolkit.telegram_page import build_telegram_data, build_telegram_readiness_items


def _dashboard_data():
    return {
        "health_status": "Excellent",
        "health_class": "good",
    }


def test_build_telegram_readiness_items_default_shape():
    items = build_telegram_readiness_items({})

    by_name = {item["name"]: item for item in items}

    assert by_name["Bot Token Config"]["status"] == "planned"
    assert by_name["Chat Targets"]["status"] == "planned"
    assert by_name["Notification Routes"]["status"] == "planned"
    assert by_name["Action Safety"]["status"] == "available"


def test_build_telegram_readiness_items_detects_config():
    items = build_telegram_readiness_items(
        {
            "toolkit": {
                "telegram": {
                    "bot_token_env": "TELEGRAM_BOT_TOKEN",
                    "chat_ids": ["123456"],
                    "notification_routes": {
                        "alerts": "123456",
                    },
                },
            },
        }
    )

    by_name = {item["name"]: item for item in items}

    assert by_name["Bot Token Config"]["status"] == "available"
    assert by_name["Chat Targets"]["status"] == "available"
    assert by_name["Notification Routes"]["status"] == "available"
    assert by_name["Action Safety"]["status"] == "available"


def test_build_telegram_data_shape():
    data = build_telegram_data(_dashboard_data(), {})
    telegram_page = data["telegram_page"]

    assert data["health_status"] == "Excellent"
    assert telegram_page["status"] == "Foundation"
    assert telegram_page["status_class"] == "warn"
    assert telegram_page["planned_areas"]
    assert telegram_page["readiness_count"] == 4
    assert telegram_page["available_readiness_count"] == 1
    assert "read-only" in telegram_page["note"]
    assert "without connecting" in telegram_page["note"]
    assert "sending messages" in telegram_page["note"]
