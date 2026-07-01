VALID_SEVERITIES = {"all", "good", "warn", "bad", "neutral"}


def classify_line(line):
    upper = line.upper()

    if "ERROR" in upper or "TRACEBACK" in upper or "EXCEPTION" in upper:
        return "bad"

    if "WARN" in upper or "WARNING" in upper:
        return "warn"

    if "API CALL" in upper:
        return "good"

    return "neutral"


def build_logs_data(dashboard_data, log_path, calls, severity="all", query=""):
    data = dict(dashboard_data)

    selected_severity = severity if severity in VALID_SEVERITIES else "all"
    search_query = (query or "").strip()

    raw_lines = []
    log_exists = log_path.exists()
    log_size = log_path.stat().st_size if log_exists else 0

    if log_exists:
        raw_lines = log_path.read_text(errors="ignore").splitlines()[-160:]

    all_raw_entries = [
        {
            "line": line,
            "severity": classify_line(line),
        }
        for line in reversed(raw_lines[-80:])
    ]

    raw_entries = all_raw_entries

    if selected_severity != "all":
        raw_entries = [
            item for item in raw_entries
            if item["severity"] == selected_severity
        ]

    if search_query:
        raw_entries = [
            item for item in raw_entries
            if search_query.lower() in item["line"].lower()
        ]

    error_count = sum(1 for item in all_raw_entries if item["severity"] == "bad")
    warning_count = sum(1 for item in all_raw_entries if item["severity"] == "warn")
    api_count = len(calls)

    if not log_exists:
        log_status = "Missing"
        log_class = "bad"
        log_detail = "Hermes log file was not found."
    elif error_count:
        log_status = "Errors Detected"
        log_class = "bad"
        log_detail = f"{error_count} recent error-like log entries found."
    elif warning_count:
        log_status = "Warnings Detected"
        log_class = "warn"
        log_detail = f"{warning_count} recent warning-like log entries found."
    else:
        log_status = "Healthy"
        log_class = "good"
        log_detail = "No recent warning or error entries detected."

    recent_calls = list(reversed(calls[-30:]))

    data["logs_page"] = {
        "log_exists": log_exists,
        "log_path": str(log_path),
        "log_size": log_size,
        "log_size_kb": log_size / 1024 if log_size else 0,
        "log_status": log_status,
        "log_class": log_class,
        "log_detail": log_detail,
        "error_count": error_count,
        "warning_count": warning_count,
        "api_count": api_count,
        "raw_entries": raw_entries,
        "raw_entry_count": len(raw_entries),
        "raw_total_count": len(all_raw_entries),
        "selected_severity": selected_severity,
        "search_query": search_query,
        "recent_calls": recent_calls,
        "note": "Logs v1 is read-only. Filtering, search, and export are local display/export helpers. Live tailing can be added later.",
    }

    return data


def build_logs_export_text(logs_data):
    logs_page = logs_data["logs_page"]

    lines = [
        "Hermes Toolkit log export",
        f"Severity: {logs_page['selected_severity']}",
        f"Search: {logs_page['search_query'] or '(none)'}",
        f"Showing: {logs_page['raw_entry_count']} of {logs_page['raw_total_count']} recent lines",
        "",
    ]

    for entry in logs_page["raw_entries"]:
        lines.append(f"[{entry['severity']}] {entry['line']}")

    return "\n".join(lines) + "\n"
