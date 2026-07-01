from toolkit.web import build_logs_data, build_logs_export_text


def test_build_logs_data_filter_shape():
    data = build_logs_data(severity="warn", query="timeout")

    logs_page = data["logs_page"]

    assert logs_page["selected_severity"] == "warn"
    assert logs_page["search_query"] == "timeout"
    assert "raw_entries" in logs_page
    assert "raw_entry_count" in logs_page
    assert "raw_total_count" in logs_page
    assert logs_page["raw_entry_count"] <= logs_page["raw_total_count"]


def test_build_logs_data_rejects_unknown_severity():
    data = build_logs_data(severity="weird", query="")

    assert data["logs_page"]["selected_severity"] == "all"

def test_build_logs_export_text_includes_filter_metadata():
    export = build_logs_export_text(severity="warn", query="timeout")

    assert "Hermes Toolkit log export" in export
    assert "Severity: warn" in export
    assert "Search: timeout" in export
    assert "Showing:" in export


def test_logs_export_route_returns_plain_text():
    from fastapi.testclient import TestClient
    from toolkit.web import app

    client = TestClient(app)
    response = client.get("/logs/export?severity=warn&q=timeout")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "Hermes Toolkit log export" in response.text
    assert "Severity: warn" in response.text
    assert "Search: timeout" in response.text

