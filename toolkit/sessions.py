def _safe_int(value, default=0):
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def build_session_activity_rows(calls):
    rows = []

    for call in calls:
        rows.append(
            {
                "call_num": _safe_int(call.get("num")),
                "provider": call.get("provider") or "unknown",
                "model": call.get("model") or "unknown",
                "input_tokens": _safe_int(call.get("in")),
                "output_tokens": _safe_int(call.get("out")),
                "total_tokens": _safe_int(call.get("total")),
                "cache_percent": _safe_int(call.get("pct")),
            }
        )

    return rows


def build_provider_activity_summaries(calls):
    summaries = {}

    for call in calls:
        provider = (call.get("provider") or "unknown").strip() or "unknown"

        if provider not in summaries:
            summaries[provider] = {
                "provider": provider,
                "call_count": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "cache_total": 0,
                "avg_cache": 0,
                "most_recent_model": "unknown",
                "last_call_num": None,
            }

        summary = summaries[provider]
        summary["call_count"] += 1
        summary["input_tokens"] += call.get("in", 0)
        summary["output_tokens"] += call.get("out", 0)
        summary["total_tokens"] += call.get("total", 0)
        summary["cache_total"] += call.get("pct", 0)
        summary["avg_cache"] = summary["cache_total"] / summary["call_count"]
        summary["most_recent_model"] = call.get("model") or "unknown"
        summary["last_call_num"] = call.get("num")

    return sorted(
        summaries.values(),
        key=lambda summary: (-summary["call_count"], summary["provider"]),
    )


def build_sessions_data(dashboard_data, cfg, calls, provider="all", query=""):
    # cfg is accepted for the public backend API and future session-browser work.
    # Current Sessions v1 behavior is dashboard/log-derived.
    _ = cfg

    selected_provider = (provider or "all").strip() or "all"
    search_query = (query or "").strip()

    data = dict(dashboard_data)
    settings = data.get("settings") or {}

    max_turns = _safe_int(settings.get("max_turns"))
    max_live_sessions = _safe_int(settings.get("max_live_sessions"))
    protect_last_n = _safe_int(settings.get("protect_last_n"))
    resume_exchanges = _safe_int(settings.get("resume_exchanges"))

    session_reset_mode = data.get("session_reset_mode") or "unknown"
    session_reset_idle = _safe_int(data.get("session_reset_idle"))
    session_reset_hour = data.get("session_reset_hour")

    total_calls = len(calls)
    total_input = sum(call.get("in", 0) for call in calls)
    total_output = sum(call.get("out", 0) for call in calls)
    total_tokens = sum(call.get("total", 0) for call in calls)
    avg_input = total_input / total_calls if total_calls else 0
    avg_output = total_output / total_calls if total_calls else 0
    avg_total = total_tokens / total_calls if total_calls else 0
    avg_cache = sum(call.get("pct", 0) for call in calls) / total_calls if total_calls else 0

    provider_options = sorted(
        {
            call.get("provider")
            for call in calls
            if call.get("provider")
        }
    )

    if selected_provider != "all" and selected_provider not in provider_options:
        selected_provider = "all"

    filtered_calls = calls

    if selected_provider != "all":
        filtered_calls = [
            call for call in filtered_calls
            if call.get("provider") == selected_provider
        ]

    if search_query:
        lowered_query = search_query.lower()
        filtered_calls = [
            call for call in filtered_calls
            if lowered_query in str(call.get("model", "")).lower()
            or lowered_query in str(call.get("provider", "")).lower()
        ]

    recent_calls = list(reversed(filtered_calls[-12:]))
    activity_rows = list(reversed(build_session_activity_rows(filtered_calls)[-12:]))
    provider_summaries = build_provider_activity_summaries(filtered_calls)

    cards = []

    def add_card(title, value, detail, severity="good", icon="check-circle"):
        cards.append(
            {
                "title": title,
                "value": value,
                "detail": detail,
                "severity": severity,
                "icon": icon,
            }
        )

    if session_reset_mode == "idle":
        add_card(
            "Session Reset",
            "Enabled",
            f"Idle reset after {session_reset_idle} minutes.",
            "good",
            "timer-reset",
        )
    elif session_reset_mode == "none":
        add_card(
            "Session Reset",
            "Disabled",
            "Sessions will not reset automatically.",
            "warn",
            "timer-off",
        )
    else:
        add_card(
            "Session Reset",
            "Unknown",
            "Session reset mode could not be determined.",
            "warn",
            "circle-help",
        )

    if max_live_sessions and max_live_sessions <= 8:
        add_card(
            "Live Sessions",
            str(max_live_sessions),
            "Live session limit is within the recommended range.",
            "good",
            "messages-square",
        )
    elif max_live_sessions:
        add_card(
            "Live Sessions",
            str(max_live_sessions),
            "High live session limits may retain extra context.",
            "warn",
            "messages-square",
        )
    else:
        add_card(
            "Live Sessions",
            "Unknown",
            "Live session limit could not be determined.",
            "warn",
            "messages-square",
        )

    if max_turns and max_turns <= 40:
        add_card(
            "Max Turns",
            str(max_turns),
            "Conversation turn limit is controlled.",
            "good",
            "repeat",
        )
    elif max_turns:
        add_card(
            "Max Turns",
            str(max_turns),
            "Large turn limits can increase retained context.",
            "warn",
            "repeat",
        )
    else:
        add_card(
            "Max Turns",
            "Unknown",
            "Max turn limit could not be determined.",
            "warn",
            "repeat",
        )

    recommendations = []

    def recommend(severity, title, detail):
        recommendations.append(
            {
                "severity": severity,
                "title": title,
                "detail": detail,
            }
        )

    if session_reset_mode != "idle":
        recommend(
            "warn",
            "Enable idle session reset",
            "Idle reset helps prevent long-running sessions from accumulating excessive context.",
        )

    if max_live_sessions and max_live_sessions > 8:
        recommend(
            "warn",
            "Reduce max live sessions",
            "A smaller live-session window can lower memory pressure and context retention.",
        )

    if max_turns and max_turns > 40:
        recommend(
            "warn",
            "Review max turns",
            "High turn limits can increase tool usage, prompt size, and session drift.",
        )

    if avg_input > 60000:
        recommend(
            "warn",
            "Watch average session prompt size",
            "Recent activity shows elevated input token usage. Consider tighter session reset behavior.",
        )

    if not recommendations:
        recommend(
            "good",
            "Session configuration looks controlled",
            "No immediate session tuning issues were detected from configuration and recent activity.",
        )

    if total_calls == 0:
        activity_status = "No recent activity"
        activity_class = "warn"
    elif avg_input <= 60000 and avg_cache >= 85:
        activity_status = "Healthy"
        activity_class = "good"
    elif avg_input <= 100000:
        activity_status = "Moderate"
        activity_class = "warn"
    else:
        activity_status = "Heavy"
        activity_class = "bad"

    data["sessions_page"] = {
        "cards": cards,
        "recommendations": recommendations,
        "recent_calls": recent_calls,
        "recent_call_count": len(recent_calls),
        "recent_total_count": len(calls),
        "activity_rows": activity_rows,
        "activity_row_count": len(activity_rows),
        "provider_summaries": provider_summaries,
        "provider_summary_count": len(provider_summaries),
        "provider_options": provider_options,
        "selected_provider": selected_provider,
        "search_query": search_query,
        "activity_status": activity_status,
        "activity_class": activity_class,
        "total_calls": total_calls,
        "total_input": total_input,
        "total_output": total_output,
        "total_tokens": total_tokens,
        "avg_input": avg_input,
        "avg_output": avg_output,
        "avg_total": avg_total,
        "avg_cache": avg_cache,
        "max_turns": max_turns,
        "max_live_sessions": max_live_sessions,
        "protect_last_n": protect_last_n,
        "resume_exchanges": resume_exchanges,
        "session_reset_mode": session_reset_mode,
        "session_reset_idle": session_reset_idle,
        "session_reset_hour": session_reset_hour,
        "note": "Sessions v1 uses configuration and recent API calls as a session activity proxy. A full session browser can be added later.",
    }

    return data
