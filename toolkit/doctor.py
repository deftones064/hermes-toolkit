from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from .config import get_path
from .status import status


CATEGORY_ORDER = [
    ("environment", "Environment"),
    ("configuration", "Configuration"),
    ("runtime", "Runtime"),
    ("connectivity", "Connectivity"),
    ("usage", "Usage"),
]


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


def _safe_int(value, default=0):
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _add_check(
    checks,
    categories,
    category,
    name,
    status_text,
    value,
    detail,
    severity="good",
    mode="static",
):
    check = {
        "category": category,
        "name": name,
        "status": status_text,
        "value": value,
        "detail": detail,
        "severity": severity,
        "mode": mode,
    }
    checks.append(check)
    categories[category].append(check)


def _doctor_context(data):
    model = data.get("model") or {}
    settings = data.get("settings") or {}

    return {
        "model": model,
        "provider": model.get("provider"),
        "default_model": model.get("default"),
        "settings": settings,
        "max_turns": _safe_int(settings.get("max_turns")),
        "max_live_sessions": _safe_int(settings.get("max_live_sessions")),
        "context_file_max_chars": settings.get("context_file_max_chars"),
        "file_read_max_chars": _safe_int(settings.get("file_read_max_chars")),
        "protect_last_n": _safe_int(settings.get("protect_last_n")),
        "resume_exchanges": _safe_int(settings.get("resume_exchanges")),
        "avg_cache": data.get("avg_cache") or 0,
        "avg_in": data.get("avg_in") or 0,
        "base_url": model.get("base_url"),
    }


def _build_environment_checks(checks, categories):
    _add_check(
        checks,
        categories,
        "environment",
        "Toolkit Runtime",
        "Online",
        "FastAPI",
        "Hermes Toolkit web service is responding.",
        "good",
    )

    _add_check(
        checks,
        categories,
        "environment",
        "Configuration Loader",
        "Available",
        "Loaded",
        "Hermes Toolkit can load the active configuration.",
        "good",
    )

    _add_check(
        checks,
        categories,
        "environment",
        "Diagnostics Mode",
        "Safe",
        "Read-only",
        "Doctor v1.1 diagnostics are non-destructive and do not restart services or modify config.",
        "good",
    )


def _build_configuration_checks(data, context, checks, categories):
    provider = context["provider"]
    default_model = context["default_model"]
    context_file_max_chars = context["context_file_max_chars"]

    if provider:
        _add_check(
            checks,
            categories,
            "configuration",
            "Active Provider",
            "Configured",
            data.get("provider_label") or provider,
            "A model provider is selected.",
            "good",
        )
    else:
        _add_check(
            checks,
            categories,
            "configuration",
            "Active Provider",
            "Missing",
            "Not set",
            "No active provider is configured.",
            "bad",
        )

    if default_model:
        _add_check(
            checks,
            categories,
            "configuration",
            "Default Model",
            "Configured",
            default_model,
            "A default model is configured for Hermes Agent.",
            "good",
        )
    else:
        _add_check(
            checks,
            categories,
            "configuration",
            "Default Model",
            "Review",
            "Not set",
            "Set a default model to avoid provider fallback issues.",
            "warn",
        )

    if data.get("session_reset_mode") == "idle":
        _add_check(
            checks,
            categories,
            "configuration",
            "Session Reset",
            "Enabled",
            f'{data.get("session_reset_idle")} min idle',
            "Idle session reset is enabled.",
            "good",
        )
    else:
        _add_check(
            checks,
            categories,
            "configuration",
            "Session Reset",
            "Disabled",
            "Manual",
            "Sessions will not reset automatically.",
            "warn",
        )

    if context_file_max_chars is None:
        _add_check(
            checks,
            categories,
            "configuration",
            "Context File Limit",
            "Missing",
            "Not set",
            "No context file character limit is configured.",
            "warn",
        )
    else:
        _add_check(
            checks,
            categories,
            "configuration",
            "Context File Limit",
            "Configured",
            f"{_safe_int(context_file_max_chars):,} chars",
            "Context file character limit is configured.",
            "good",
        )


def _build_runtime_checks(context, checks, categories):
    max_live_sessions = context["max_live_sessions"]
    max_turns = context["max_turns"]
    protect_last_n = context["protect_last_n"]

    if max_live_sessions and max_live_sessions <= 8:
        _add_check(
            checks,
            categories,
            "runtime",
            "Live Sessions",
            "Optimized",
            str(max_live_sessions),
            "Max live sessions is within the recommended operating range.",
            "good",
        )
    elif max_live_sessions:
        _add_check(
            checks,
            categories,
            "runtime",
            "Live Sessions",
            "Review",
            str(max_live_sessions),
            "High live session limits may retain extra context.",
            "warn",
        )
    else:
        _add_check(
            checks,
            categories,
            "runtime",
            "Live Sessions",
            "Unknown",
            "Unavailable",
            "Live session limit could not be determined.",
            "warn",
        )

    if max_turns and max_turns <= 40:
        _add_check(
            checks,
            categories,
            "runtime",
            "Max Turns",
            "Controlled",
            str(max_turns),
            "Conversation turn limit is controlled.",
            "good",
        )
    elif max_turns:
        _add_check(
            checks,
            categories,
            "runtime",
            "Max Turns",
            "High",
            str(max_turns),
            "Large turn limits can increase retained context.",
            "warn",
        )
    else:
        _add_check(
            checks,
            categories,
            "runtime",
            "Max Turns",
            "Unknown",
            "Unavailable",
            "Max turn setting could not be determined.",
            "warn",
        )

    if protect_last_n:
        _add_check(
            checks,
            categories,
            "runtime",
            "Protected Context",
            "Configured",
            str(protect_last_n),
            "Recent exchanges are protected during compression.",
            "good",
        )
    else:
        _add_check(
            checks,
            categories,
            "runtime",
            "Protected Context",
            "Review",
            "Not set",
            "Compression protection should be reviewed.",
            "warn",
        )


def _normalize_ollama_base_url(base_url):
    if not base_url:
        return "http://127.0.0.1:11434"

    return str(base_url).rstrip("/")


def _check_ollama_reachability(base_url, timeout=1.5):
    tags_url = f"{_normalize_ollama_base_url(base_url)}/api/tags"

    try:
        with urlopen(tags_url, timeout=timeout) as response:
            status_code = getattr(response, "status", 200)
    except HTTPError as exc:
        return {
            "reachable": False,
            "url": tags_url,
            "status": f"HTTP {exc.code}",
            "detail": "Ollama responded with an HTTP error.",
        }
    except (URLError, TimeoutError, OSError) as exc:
        return {
            "reachable": False,
            "url": tags_url,
            "status": "Unavailable",
            "detail": f"Ollama tags endpoint could not be reached: {exc.__class__.__name__}.",
        }

    return {
        "reachable": 200 <= status_code < 500,
        "url": tags_url,
        "status": f"HTTP {status_code}",
        "detail": "Ollama tags endpoint responded without launching a model.",
    }


def _check_http_endpoint_reachability(url, label, timeout=1.5):
    try:
        with urlopen(url, timeout=timeout) as response:
            status_code = getattr(response, "status", 200)
    except HTTPError as exc:
        return {
            "reachable": False,
            "url": url,
            "status": f"HTTP {exc.code}",
            "detail": f"{label} endpoint responded with an HTTP error.",
        }
    except (URLError, TimeoutError, OSError) as exc:
        return {
            "reachable": False,
            "url": url,
            "status": "Unavailable",
            "detail": f"{label} endpoint could not be reached: {exc.__class__.__name__}.",
        }

    return {
        "reachable": 200 <= status_code < 500,
        "url": url,
        "status": f"HTTP {status_code}",
        "detail": f"{label} endpoint responded without sending a prompt.",
    }


def _check_provider_connectivity(data, context):
    provider = context["provider"]

    if provider == "ollama":
        result = _check_ollama_reachability(context.get("base_url"))

        if result["reachable"]:
            return {
                "name": "Ollama Reachability",
                "status": "Reachable",
                "value": result["status"],
                "detail": result["detail"],
                "severity": "good",
                "mode": "live",
            }

        return {
            "name": "Ollama Reachability",
            "status": "Not reachable",
            "value": result["status"],
            "detail": result["detail"],
            "severity": "warn",
            "mode": "live",
        }

    if provider:
        provider_label = data.get("provider_label") or provider
        default_model = context.get("default_model")

        if not default_model:
            return {
                "name": "Provider Config",
                "status": "Incomplete",
                "value": f"{provider_label} / no default model",
                "detail": "Provider is selected, but no default model is configured.",
                "severity": "warn",
                "mode": "config",
            }

        if provider == "openrouter":
            result = _check_http_endpoint_reachability(
                "https://openrouter.ai/api/v1/models",
                "OpenRouter models",
            )

            if result["reachable"]:
                return {
                    "name": "OpenRouter Reachability",
                    "status": "Reachable",
                    "value": result["status"],
                    "detail": result["detail"],
                    "severity": "good",
                    "mode": "live",
                }

            return {
                "name": "OpenRouter Reachability",
                "status": "Not reachable",
                "value": result["status"],
                "detail": result["detail"],
                "severity": "warn",
                "mode": "live",
            }

        return {
            "name": "Provider Config",
            "status": "Configured",
            "value": f"{provider_label} / {default_model}",
            "detail": "Provider and default model are configured. No safe unauthenticated live check is available for this provider yet.",
            "severity": "good",
            "mode": "config",
        }

    return {
        "name": "Provider Connectivity",
        "status": "Blocked",
        "value": "No provider",
        "detail": "Connectivity cannot be evaluated until a provider is selected.",
        "severity": "bad",
        "mode": "config",
    }


def _build_connectivity_checks(data, context, checks, categories):
    provider_check = _check_provider_connectivity(data, context)

    _add_check(
        checks,
        categories,
        "connectivity",
        provider_check["name"],
        provider_check["status"],
        provider_check["value"],
        provider_check["detail"],
        provider_check["severity"],
        provider_check.get("mode", "static"),
    )

    _add_check(
        checks,
        categories,
        "connectivity",
        "Network Diagnostics",
        "Partial",
        "Provider-specific checks active",
        "Ollama/OpenRouter endpoint checks are available when configured. Broader DNS and authenticated provider checks remain intentionally conservative.",
        "warn",
        "static",
    )


def _build_usage_checks(context, checks, categories):
    avg_cache = context["avg_cache"]
    avg_in = context["avg_in"]
    file_read_max_chars = context["file_read_max_chars"]
    resume_exchanges = context["resume_exchanges"]

    if avg_cache >= 85:
        _add_check(
            checks,
            categories,
            "usage",
            "Cache Efficiency",
            "Healthy",
            f"{avg_cache:.1f}%",
            "Average cache hit rate is strong.",
            "good",
        )
    elif avg_cache >= 50:
        _add_check(
            checks,
            categories,
            "usage",
            "Cache Efficiency",
            "Needs Attention",
            f"{avg_cache:.1f}%",
            "Average cache hit rate could be improved.",
            "warn",
        )
    else:
        _add_check(
            checks,
            categories,
            "usage",
            "Cache Efficiency",
            "Poor",
            f"{avg_cache:.1f}%",
            "Low cache efficiency may increase cost and latency.",
            "bad",
        )

    if avg_in <= 60000:
        _add_check(
            checks,
            categories,
            "usage",
            "Prompt Size",
            "Controlled",
            f"{avg_in:,.0f} tokens",
            "Average input size is within the preferred range.",
            "good",
        )
    elif avg_in <= 100000:
        _add_check(
            checks,
            categories,
            "usage",
            "Prompt Size",
            "Moderate",
            f"{avg_in:,.0f} tokens",
            "Average input size is elevated.",
            "warn",
        )
    else:
        _add_check(
            checks,
            categories,
            "usage",
            "Prompt Size",
            "High",
            f"{avg_in:,.0f} tokens",
            "Average input size is high and may impact performance.",
            "bad",
        )

    if file_read_max_chars and file_read_max_chars <= 60000:
        _add_check(
            checks,
            categories,
            "usage",
            "File Read Limit",
            "Controlled",
            f"{file_read_max_chars:,} chars",
            "File read limit is controlled.",
            "good",
        )
    elif file_read_max_chars:
        _add_check(
            checks,
            categories,
            "usage",
            "File Read Limit",
            "High",
            f"{file_read_max_chars:,} chars",
            "Large file reads may increase prompt size.",
            "warn",
        )
    else:
        _add_check(
            checks,
            categories,
            "usage",
            "File Read Limit",
            "Unknown",
            "Unavailable",
            "File read limit could not be determined.",
            "warn",
        )

    if resume_exchanges:
        _add_check(
            checks,
            categories,
            "usage",
            "Resume Exchanges",
            "Configured",
            str(resume_exchanges),
            "Resume display depth is configured.",
            "good",
        )
    else:
        _add_check(
            checks,
            categories,
            "usage",
            "Resume Exchanges",
            "Review",
            "Not set",
            "Resume exchange display depth should be reviewed.",
            "warn",
        )


def _build_doctor_summary(checks):
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

    return {
        "summary": summary,
        "health_score": health_score,
        "health_status": health_status,
        "health_class": health_class,
    }


def _build_doctor_recommendations(data, context):
    recommendations = []

    def recommend(severity, title, detail, source):
        recommendations.append(
            {
                "severity": severity,
                "title": title,
                "detail": detail,
                "source": source,
            }
        )

    provider = context["provider"]
    default_model = context["default_model"]
    avg_cache = context["avg_cache"]
    avg_in = context["avg_in"]
    max_live_sessions = context["max_live_sessions"]
    file_read_max_chars = context["file_read_max_chars"]

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

    return recommendations


def build_doctor_data(dashboard_data, cfg):
    # cfg is accepted for the public backend API and future live diagnostics.
    # The current v0.4 cleanup preserves the existing dashboard-derived behavior.
    _ = cfg

    data = dict(dashboard_data)
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    categories = {key: [] for key, _ in CATEGORY_ORDER}
    checks = []
    context = _doctor_context(data)

    _build_environment_checks(checks, categories)
    _build_configuration_checks(data, context, checks, categories)
    _build_runtime_checks(context, checks, categories)
    _build_connectivity_checks(data, context, checks, categories)
    _build_usage_checks(context, checks, categories)

    summary_data = _build_doctor_summary(checks)
    recommendations = _build_doctor_recommendations(data, context)

    data["health_score"] = summary_data["health_score"]
    data["health_status"] = summary_data["health_status"]
    data["health_class"] = summary_data["health_class"]
    data["doctor_checks"] = checks
    data["doctor_categories"] = [
        {
            "id": key,
            "title": label,
            "checks": categories[key],
        }
        for key, label in CATEGORY_ORDER
    ]
    data["doctor_summary"] = summary_data["summary"]
    data["recommendations"] = recommendations
    data["diagnostic_generated_at"] = generated_at

    return data
