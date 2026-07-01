MEMORY_KEYWORDS = [
    "cache",
    "context",
    "compression",
    "session",
    "resume",
    "memory",
    "evict",
    "idle",
]


PLANNED_AREAS = [
    {
        "name": "Memory Inventory",
        "status": "Planned",
        "description": "Future read-only view of persistent memories, stores, or vector indexes if Hermes exposes them.",
        "icon": "database",
    },
    {
        "name": "Context Timeline",
        "status": "Planned",
        "description": "Future timeline of session context growth, compression, eviction, and resume activity.",
        "icon": "timeline",
    },
    {
        "name": "Compression Health",
        "status": "Planned",
        "description": "Future diagnostics for compression effectiveness and protected-message behavior.",
        "icon": "archive",
    },
    {
        "name": "Memory Safety",
        "status": "Planned",
        "description": "Future controls for reviewing, exporting, or safely pruning memory data.",
        "icon": "shield",
    },
]


def _safe_int(value, default=0):
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def classify_memory_signal(line):
    upper = line.upper()

    if "ERROR" in upper or "TRACEBACK" in upper or "EXCEPTION" in upper:
        return "bad"

    if "WARN" in upper or "WARNING" in upper:
        return "warn"

    if "EVICT" in upper or "CACHE" in upper or "SESSION" in upper:
        return "good"

    return "neutral"


def _read_memory_signal_lines(log_path):
    raw_lines = []
    if log_path.exists():
        raw_lines = log_path.read_text(errors="ignore").splitlines()[-1000:]

    signal_lines = []

    for line in raw_lines:
        lowered = line.lower()

        if not any(keyword in lowered for keyword in MEMORY_KEYWORDS):
            continue

        signal_lines.append(
            {
                "line": line,
                "severity": classify_memory_signal(line),
            }
        )

    return signal_lines


def _build_cards(protect_last_n, resume_exchanges, context_file_max_chars):
    cards = []

    def add_card(title, value, detail, severity="good", icon="brain"):
        cards.append(
            {
                "title": title,
                "value": value,
                "detail": detail,
                "severity": severity,
                "icon": icon,
            }
        )

    if protect_last_n and protect_last_n <= 15:
        add_card(
            "Protected Context",
            str(protect_last_n),
            "Recent messages are protected during compression.",
            "good",
            "shield-check",
        )
    elif protect_last_n:
        add_card(
            "Protected Context",
            str(protect_last_n),
            "High protection values may retain more context than necessary.",
            "warn",
            "shield-alert",
        )
    else:
        add_card(
            "Protected Context",
            "Unset",
            "Compression protection could not be determined.",
            "warn",
            "shield-alert",
        )

    if resume_exchanges and resume_exchanges <= 8:
        add_card(
            "Resume Exchanges",
            str(resume_exchanges),
            "Resume context depth is controlled.",
            "good",
            "rotate-ccw",
        )
    elif resume_exchanges:
        add_card(
            "Resume Exchanges",
            str(resume_exchanges),
            "Large resume depth can increase prompt size.",
            "warn",
            "rotate-ccw",
        )
    else:
        add_card(
            "Resume Exchanges",
            "Unset",
            "Resume exchange count could not be determined.",
            "warn",
            "rotate-ccw",
        )

    if context_file_max_chars and context_file_max_chars <= 60000:
        add_card(
            "Context File Limit",
            f"{context_file_max_chars:,}",
            "Context file loading is bounded.",
            "good",
            "file-text",
        )
    elif context_file_max_chars:
        add_card(
            "Context File Limit",
            f"{context_file_max_chars:,}",
            "Large context file limits may inflate prompts.",
            "warn",
            "file-warning",
        )
    else:
        add_card(
            "Context File Limit",
            "Unset",
            "No context file limit is configured.",
            "warn",
            "file-warning",
        )

    return cards


def _memory_status(avg_cache):
    if avg_cache >= 85:
        return (
            "Efficient",
            "good",
            "Recent cache behavior suggests efficient context reuse.",
        )

    if avg_cache >= 50:
        return (
            "Review",
            "warn",
            "Cache behavior is acceptable but could be improved.",
        )

    return (
        "Inefficient",
        "bad",
        "Low cache behavior may indicate excess context churn.",
    )


def _build_recommendations(
    avg_cache,
    avg_input,
    session_reset_mode,
    protect_last_n,
    resume_exchanges,
):
    recommendations = []

    def recommend(severity, title, detail):
        recommendations.append(
            {
                "severity": severity,
                "title": title,
                "detail": detail,
            }
        )

    if avg_cache < 85:
        recommend(
            "warn" if avg_cache >= 50 else "bad",
            "Improve context reuse",
            "Review prompt size, session reset behavior, and file/context loading limits.",
        )

    if avg_input > 60000:
        recommend(
            "warn",
            "Watch prompt growth",
            "Recent average input size is elevated. Memory and context settings may need tightening.",
        )

    if session_reset_mode != "idle":
        recommend(
            "warn",
            "Use idle session reset",
            "Idle reset helps reduce long-lived context buildup.",
        )

    if protect_last_n > 15:
        recommend(
            "warn",
            "Review protected context depth",
            "Protecting too many recent messages can reduce compression effectiveness.",
        )

    if resume_exchanges > 8:
        recommend(
            "warn",
            "Reduce resume exchanges",
            "Large resume depth can increase the context sent back into future sessions.",
        )

    if not recommendations:
        recommend(
            "good",
            "Memory configuration looks controlled",
            "No immediate memory or context tuning issues were detected.",
        )

    return recommendations


def build_memory_data(dashboard_data, calls, log_path):
    data = dict(dashboard_data)
    settings = data.get("settings") or {}

    context_file_max_chars = _safe_int(settings.get("context_file_max_chars"))
    file_read_max_chars = _safe_int(settings.get("file_read_max_chars"))
    protect_last_n = _safe_int(settings.get("protect_last_n"))
    resume_exchanges = _safe_int(settings.get("resume_exchanges"))
    max_turns = _safe_int(settings.get("max_turns"))
    max_live_sessions = _safe_int(settings.get("max_live_sessions"))

    session_reset_mode = data.get("session_reset_mode") or "unknown"
    session_reset_idle = _safe_int(data.get("session_reset_idle"))

    total_calls = len(calls)
    avg_input = (
        sum(call.get("in", 0) for call in calls) / total_calls
        if total_calls
        else 0
    )
    avg_cache = (
        sum(call.get("pct", 0) for call in calls) / total_calls
        if total_calls
        else 0
    )
    total_cached_tokens = sum(call.get("cache", 0) for call in calls)

    signal_lines = _read_memory_signal_lines(log_path)
    memory_status, memory_class, memory_detail = _memory_status(avg_cache)

    data["memory_page"] = {
        "status": memory_status,
        "status_class": memory_class,
        "detail": memory_detail,
        "cards": _build_cards(
            protect_last_n,
            resume_exchanges,
            context_file_max_chars,
        ),
        "recommendations": _build_recommendations(
            avg_cache,
            avg_input,
            session_reset_mode,
            protect_last_n,
            resume_exchanges,
        ),
        "planned_areas": PLANNED_AREAS,
        "signal_lines": list(reversed(signal_lines[-50:])),
        "signal_count": len(signal_lines),
        "avg_input": avg_input,
        "avg_cache": avg_cache,
        "total_cached_tokens": total_cached_tokens,
        "context_file_max_chars": context_file_max_chars,
        "file_read_max_chars": file_read_max_chars,
        "protect_last_n": protect_last_n,
        "resume_exchanges": resume_exchanges,
        "max_turns": max_turns,
        "max_live_sessions": max_live_sessions,
        "session_reset_mode": session_reset_mode,
        "session_reset_idle": session_reset_idle,
        "note": "Memory v1 is read-only. It summarizes configuration, cache behavior, and log-derived memory/context signals without inspecting memory contents.",
    }

    return data
