from toolkit.home_assistant_page import (
    build_home_assistant_data,
    build_home_assistant_readiness_items,
)


def _dashboard_data():
    return {
        "health_status": "Excellent",
        "health_class": "good",
    }


def test_build_home_assistant_readiness_items_default_shape():
    items = build_home_assistant_readiness_items({})

    by_name = {item["name"]: item for item in items}

    assert by_name["Connection Config"]["status"] == "planned"
    assert by_name["Auth Readiness"]["status"] == "planned"
    assert by_name["Webhook Readiness"]["status"] == "planned"
    assert by_name["Action Safety"]["status"] == "available"


def test_build_home_assistant_readiness_items_detects_config():
    items = build_home_assistant_readiness_items(
        {
            "toolkit": {
                "home_assistant": {
                    "url": "http://homeassistant.local:8123",
                    "token_env": "HA_TOKEN",
                    "webhook_id": "hermes",
                },
            },
        }
    )

    by_name = {item["name"]: item for item in items}

    assert by_name["Connection Config"]["status"] == "available"
    assert by_name["Auth Readiness"]["status"] == "available"
    assert by_name["Webhook Readiness"]["status"] == "available"
    assert by_name["Action Safety"]["status"] == "available"


def test_build_home_assistant_data_shape():
    data = build_home_assistant_data(_dashboard_data(), {})
    ha_page = data["home_assistant_page"]

    assert data["health_status"] == "Excellent"
    assert ha_page["status"] == "Foundation"
    assert ha_page["status_class"] == "warn"
    assert ha_page["planned_areas"]
    assert ha_page["readiness_count"] == 4
    assert ha_page["available_readiness_count"] == 1
    assert "read-only" in ha_page["note"]
    assert "without connecting" in ha_page["note"]
    assert "controlling anything" in ha_page["note"]
