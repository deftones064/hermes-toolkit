from pathlib import Path

from fastapi.testclient import TestClient

from toolkit.logs_page import build_logs_data as build_logs_page_data
from toolkit.logs_page import build_logs_export_text as build_logs_page_export_text
from toolkit.web import app, build_logs_data, build_logs_export_text


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


def test_logs_backend_classifies_filters_and_searches(tmp_path):
    log_path = tmp_path / "hermes.log"
    log_path.write_text(
        "\n".join(
            [
                "INFO startup complete",
                "WARNING provider timeout",
                "ERROR failed request",
                "INFO API CALL provider=openrouter",
            ]
        )
    )

    data = build_logs_page_data({}, log_path, [], severity="warn", query="timeout")
    logs_page = data["logs_page"]

    assert logs_page["log_exists"] is True
    assert logs_page["log_status"] == "Errors Detected"
    assert logs_page["error_count"] == 1
    assert logs_page["warning_count"] == 1
    assert logs_page["raw_entry_count"] == 1
    assert logs_page["raw_entries"][0]["severity"] == "warn"
    assert "timeout" in logs_page["raw_entries"][0]["line"]


def test_logs_backend_handles_missing_log(tmp_path):
    log_path = tmp_path / "missing.log"

    data = build_logs_page_data({}, log_path, [], severity="all", query="")
    logs_page = data["logs_page"]

    assert logs_page["log_exists"] is False
    assert logs_page["log_status"] == "Missing"
    assert logs_page["log_class"] == "bad"
    assert logs_page["raw_entries"] == []


def test_build_logs_export_text_includes_filter_metadata():
    export = build_logs_export_text(severity="warn", query="timeout")

    assert "Hermes Toolkit log export" in export
    assert "Severity: warn" in export
    assert "Search: timeout" in export
    assert "Showing:" in export


def test_logs_backend_export_text_from_data(tmp_path):
    log_path = tmp_path / "hermes.log"
    log_path.write_text("WARNING provider timeout\n")

    data = build_logs_page_data({}, log_path, [], severity="warn", query="timeout")
    export = build_logs_page_export_text(data)

    assert "Hermes Toolkit log export" in export
    assert "Severity: warn" in export
    assert "Search: timeout" in export
    assert "[warn] WARNING provider timeout" in export


def test_logs_export_route_returns_plain_text():
    client = TestClient(app)
    response = client.get("/logs/export?severity=warn&q=timeout")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "Hermes Toolkit log export" in response.text
    assert "Severity: warn" in response.text
    assert "Search: timeout" in response.text
