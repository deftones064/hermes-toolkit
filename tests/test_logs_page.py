from toolkit.web import build_logs_data


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
