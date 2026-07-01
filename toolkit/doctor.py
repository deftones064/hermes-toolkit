from .config import get_path
from .status import status

def doctor(cfg):
    issues = []

    if get_path(cfg, ("agent", "max_turns"), 999) > 50:
        issues.append("agent.max_turns is high")
    if cfg.get("context_file_max_chars") is None:
        issues.append("context_file_max_chars is unlimited")
    if cfg.get("file_read_max_chars", 999999) > 60000:
        issues.append("file_read_max_chars is high")
    if get_path(cfg, ("compression", "protect_last_n"), 999) > 15:
        issues.append("compression.protect_last_n is high")
    if get_path(cfg, ("session_reset", "mode")) == "none":
        issues.append("session_reset is disabled")
    if "idle" in cfg.get("session_reset", {}):
        issues.append("stray session_reset.idle key exists")

    if not issues:
        print("Hermes settings look good.")
    else:
        print("Potential issues:")
        for i in issues:
            print(f"  - {i}")

    print()
    status(cfg)


def build_doctor_data(dashboard_data, cfg):
    from datetime import datetime, timezone

    data = dict(dashboard_data)
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    category_order = [
        ("environment", "Environment"),
        ("configuration", "Configuration"),
        ("runtime", "Runtime"),
        ("connectivity", "Connectivity"),
        ("usage", "Usage"),
    ]

    categories = {key: [] for key, _ in category_order}
    checks = []

    def safe_int(value, default=0):
        try:
            if value is None:
                return default
            return int(value)
        except (TypeError, ValueError):
            return default

    def add_check(category, name, status, value, detail, severity="good"):
        check = {
            "category": category,
            "name": name,
            "status": status,
            "value": value,
            "detail": detail,
            "severity": severity,
        }
        checks.append(check)
        categories[category].append(check)

    model = data.get("model") or {}
    provider = model.get("provider")
    default_model = model.get("default")
    settings = data.get("settings") or {}

    max_turns = safe_int(settings.get("max_turns"))
    max_live_sessions = safe_int(settings.get("max_live_sessions"))
    context_file_max_chars = settings.get("context_file_max_chars")
    file_read_max_chars = safe_int(settings.get("file_read_max_chars"))
    protect_last_n = safe_int(settings.get("protect_last_n"))
    resume_exchanges = safe_int(settings.get("resume_exchanges"))

    # Environment
    add_check(
        "environment",
        "Toolkit Runtime",
        "Online",
        "FastAPI",
        "Hermes Toolkit web service is responding.",
        "good",
    )

    add_check(
        "environment",
        "Configuration Loader",
        "Available",
        "Loaded",
        "Hermes Toolkit can load the active configuration.",
        "good",
    )

    add_check(
        "environment",
        "Diagnostics Mode",
        "Safe",
        "Read-only",
        "Doctor v1.1 diagnostics are non-destructive and do not restart services or modify config.",
        "good",
    )

    # Configuration
    if provider:
        add_check(
            "configuration",
            "Active Provider",
            "Configured",
            data.get("provider_label") or provider,
            "A model provider is selected.",
            "good",
        )
    else:
        add_check(
            "configuration",
            "Active Provider",
            "Missing",
            "Not set",
            "No active provider is configured.",
            "bad",
        )

    if default_model:
        add_check(
            "configuration",
            "Default Model",
            "Configured",
            default_model,
            "A default model is configured for Hermes Agent.",
            "good",
        )
    else:
        add_check(
            "configuration",
            "Default Model",
            "Review",
            "Not set",
            "Set a default model to avoid provider fallback issues.",
            "warn",
        )

    if data.get("session_reset_mode") == "idle":
        add_check(
            "configuration",
            "Session Reset",
            "Enabled",
            f'{data.get("session_reset_idle")} min idle',
            "Idle session reset is enabled.",
            "good",
        )
    else:
        add_check(
            "configuration",
            "Session Reset",
            "Disabled",
            "Manual",
            "Sessions will not reset automatically.",
            "warn",
        )

    if context_file_max_chars is None:
        add_check(
            "configuration",
            "Context File Limit",
            "Missing",
            "Not set",
            "No context file character limit is configured.",
            "warn",
        )
    else:
        add_check(
            "configuration",
            "Context File Limit",
            "Configured",
            f"{safe_int(context_file_max_chars):,} chars",
            "Context file character limit is configured.",
            "good",
        )

    # Runtime
    if max_live_sessions and max_live_sessions <= 8:
        add_check(
            "runtime",
            "Live Sessions",
            "Optimized",
            str(max_live_sessions),
            "Max live sessions is within the recommended operating range.",
            "good",
        )
    elif max_live_sessions:
        add_check(
            "runtime",
            "Live Sessions",
            "Review",
            str(max_live_sessions),
            "High live session limits may retain extra context.",
            "warn",
        )
    else:
        add_check(
            "runtime",
            "Live Sessions",
            "Unknown",
            "Unavailable",
            "Live session limit could not be determined.",
            "warn",
        )

    if max_turns and max_turns <= 40:
        add_check(
            "runtime",
            "Max Turns",
            "Controlled",
            str(max_turns),
            "Conversation turn limit is controlled.",
            "good",
        )
    elif max_turns:
        add_check(
            "runtime",
            "Max Turns",
            "High",
            str(max_turns),
            "Large turn limits can increase retained context.",
            "warn",
        )
    else:
        add_check(
            "runtime",
            "Max Turns",
            "Unknown",
            "Unavailable",
            "Max turn setting could not be determined.",
            "warn",
        )

    if protect_last_n:
        add_check(
            "runtime",
            "Protected Context",
            "Configured",
            str(protect_last_n),
            "Recent exchanges are protected during compression.",
            "good",
        )
    else:
        add_check(
            "runtime",
            "Protected Context",
            "Review",
            "Not set",
            "Compression protection should be reviewed.",
            "warn",
        )

    # Connectivity
    if provider == "ollama":
        add_check(
            "connectivity",
            "Ollama Provider",
            "Configured",
            "Local",
            "Ollama is selected. Live reachability checks will be added in a later diagnostic engine pass.",
            "warn",
        )
    elif provider:
        add_check(
            "connectivity",
            "Provider Connectivity",
            "Configured",
            data.get("provider_label") or provider,
            "Provider configuration exists. Live API checks are intentionally not performed yet.",
            "good",
        )
    else:
        add_check(
            "connectivity",
            "Provider Connectivity",
            "Blocked",
            "No provider",
            "Connectivity cannot be evaluated until a provider is selected.",
            "bad",
        )

    add_check(
        "connectivity",
        "Network Diagnostics",
        "Pending",
        "Not checked",
        "DNS and endpoint checks are reserved for the future diagnostic engine.",
        "warn",
    )

    # Usage
    avg_cache = data.get("avg_cache") or 0
    avg_in = data.get("avg_in") or 0

    if avg_cache >= 85:
        add_check(
            "usage",
            "Cache Efficiency",
            "Healthy",
            f"{avg_cache:.1f}%",
            "Average cache hit rate is strong.",
            "good",
        )
    elif avg_cache >= 50:
        add_check(
            "usage",
            "Cache Efficiency",
            "Needs Attention",
            f"{avg_cache:.1f}%",
            "Average cache hit rate could be improved.",
            "warn",
        )
    else:
        add_check(
            "usage",
            "Cache Efficiency",
            "Poor",
            f"{avg_cache:.1f}%",
            "Low cache efficiency may increase cost and latency.",
            "bad",
        )

    if avg_in <= 60000:
        add_check(
            "usage",
            "Prompt Size",
            "Controlled",
            f"{avg_in:,.0f} tokens",
            "Average input size is within the preferred range.",
            "good",
        )
    elif avg_in <= 100000:
        add_check(
            "usage",
            "Prompt Size",
            "Moderate",
            f"{avg_in:,.0f} tokens",
            "Average input size is elevated.",
            "warn",
        )
    else:
        add_check(
            "usage",
            "Prompt Size",
            "High",
            f"{avg_in:,.0f} tokens",
            "Average input size is high and may impact performance.",
            "bad",
        )

    if file_read_max_chars and file_read_max_chars <= 60000:
        add_check(
            "usage",
            "File Read Limit",
            "Controlled",
            f"{file_read_max_chars:,} chars",
            "File read limit is controlled.",
            "good",
        )
    elif file_read_max_chars:
        add_check(
            "usage",
            "File Read Limit",
            "High",
            f"{file_read_max_chars:,} chars",
            "Large file reads may increase prompt size.",
            "warn",
        )
    else:
        add_check(
            "usage",
            "File Read Limit",
            "Unknown",
            "Unavailable",
            "File read limit could not be determined.",
            "warn",
        )

    if resume_exchanges:
        add_check(
            "usage",
            "Resume Exchanges",
            "Configured",
            str(resume_exchanges),
            "Resume display depth is configured.",
            "good",
        )
    else:
        add_check(
            "usage",
            "Resume Exchanges",
            "Review",
            "Not set",
            "Resume exchange display depth should be reviewed.",
            "warn",
        )

    summary = {
        "good": sum(1 for check in checks if check["severity"] == "good"),
        "warn": sum(1 for check in checks if check["severity"] == "warn"),
        "bad": sum(1 for check in checks if check["severity"] == "bad"),
    }

    total = len(checks)
    if total:
        health_score = round(
            (
                summary["good"] * 100
                + summary["warn"] * 65
                + summary["bad"] * 0
            )
            / total
        )
    else:
        health_score = 0

    if health_score >= 90:
        health_status = "Excellent"
        health_class = "good"
    elif health_score >= 75:
        health_status = "Good"
        health_class = "good"
    elif health_score >= 60:
        health_status = "Needs Attention"
        health_class = "warn"
    else:
        health_status = "Poor"
        health_class = "bad"

    recommendations = []

    def recommend(severity, title, detail, source):
        recommendations.append({
            "severity": severity,
            "title": title,
            "detail": detail,
            "source": source,
        })

    if not provider:
        recommend(
            "bad",
            "Select an active provider",
            "Hermes needs an active provider before runtime connectivity can be trusted.",
            "Active Provider",
        )

    if not default_model:
        recommend(
            "warn",
            "Set a default model",
            "A default model helps prevent fallback errors during agent startup.",
            "Default Model",
        )

    if avg_cache < 85:
        recommend(
            "warn" if avg_cache >= 50 else "bad",
            "Improve cache efficiency",
            "Review prompt size, session reset behavior, and context retention settings.",
            "Cache Efficiency",
        )

    if avg_in > 60000:
        recommend(
            "warn" if avg_in <= 100000 else "bad",
            "Reduce average prompt size",
            "Large prompts can slow responses and increase model usage cost.",
            "Prompt Size",
        )

    if data.get("session_reset_mode") != "idle":
        recommend(
            "warn",
            "Enable idle session reset",
            "Idle session reset helps keep long-running sessions from accumulating excessive context.",
            "Session Reset",
        )

    if max_live_sessions and max_live_sessions > 8:
        recommend(
            "warn",
            "Review live session limit",
            "A lower live session limit may reduce retained context and memory pressure.",
            "Live Sessions",
        )

    if file_read_max_chars and file_read_max_chars > 60000:
        recommend(
            "warn",
            "Lower file read limit",
            "Large file reads can inflate prompts and reduce cache effectiveness.",
            "File Read Limit",
        )

    if not recommendations:
        recommend(
            "good",
            "No critical issues detected",
            "Doctor did not find any immediate problems. Continue monitoring runtime and usage data.",
            "Doctor",
        )

    data["health_score"] = health_score
    data["health_status"] = health_status
    data["health_class"] = health_class
    data["doctor_checks"] = checks
    data["doctor_categories"] = [
        {
            "id": key,
            "title": label,
            "checks": categories[key],
        }
        for key, label in category_order
    ]
    data["doctor_summary"] = summary
    data["recommendations"] = recommendations
    data["diagnostic_generated_at"] = generated_at

    return data
