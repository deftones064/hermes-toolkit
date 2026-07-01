from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from toolkit.config import load_config, get_path
from toolkit.logs import parse_recent_api_calls
from toolkit.doctor import doctor, build_doctor_data as build_doctor_report

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "toolkit" / "templates"))

app = FastAPI(title="Hermes Toolkit")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "toolkit" / "static")), name="static")


def build_dashboard_data():
    cfg = load_config()
    calls = parse_recent_api_calls(80)

    model = cfg.get("model", {})
    avg_in = avg_out = avg_cache = 0
    latest = None

    if calls:
        latest = calls[-1]
        avg_in = sum(c["in"] for c in calls) / len(calls)
        avg_out = sum(c["out"] for c in calls) / len(calls)
        avg_cache = sum(c["pct"] for c in calls) / len(calls)

    if avg_in > 100000:
        prompt_status = "High"
        prompt_class = "bad"
    elif avg_in > 60000:
        prompt_status = "Moderate"
        prompt_class = "warn"
    else:
        prompt_status = "Controlled"
        prompt_class = "good"

    if avg_cache < 50:
        cache_status = "Low"
        cache_class = "bad"
    elif avg_cache < 85:
        cache_status = "Okay"
        cache_class = "warn"
    else:
        cache_status = "Good"
        cache_class = "good"

    provider_labels = {
        "openai-codex": "OpenAI Codex",
        "openrouter": "OpenRouter",
        "anthropic": "Anthropic",
        "ollama": "Ollama",
        "google": "Google AI Studio",
    }

    score = 100
    if avg_in > 100000:
        score -= 30
    elif avg_in > 60000:
        score -= 12

    if avg_cache < 50:
        score -= 30
    elif avg_cache < 85:
        score -= 12

    if get_path(cfg, ("session_reset", "mode")) == "none":
        score -= 10

    if cfg.get("context_file_max_chars") is None:
        score -= 10

    score = max(0, min(100, score))

    if score >= 90:
        health_status = "Excellent"
        health_class = "good"
    elif score >= 75:
        health_status = "Good"
        health_class = "good"
    elif score >= 60:
        health_status = "Needs Attention"
        health_class = "warn"
    else:
        health_status = "Poor"
        health_class = "bad"

    session_reset = cfg.get("session_reset") or {}

    return {
        "model": model,
        "provider_label": provider_labels.get(model.get("provider"), model.get("provider")),
        "calls": calls[-20:],
        "latest": latest,
        "avg_in": avg_in,
        "avg_out": avg_out,
        "avg_cache": avg_cache,
        "prompt_status": prompt_status,
        "prompt_class": prompt_class,
        "prompt_bar": min(100, max(3, avg_in / 100000 * 100)),
        "cache_status": cache_status,
        "cache_class": cache_class,
        "health_score": score,
        "health_status": health_status,
        "health_class": health_class,
        "session_reset_mode": session_reset.get("mode"),
        "session_reset_idle": session_reset.get("idle_minutes"),
        "session_reset_hour": session_reset.get("at_hour"),
        "settings": {
            "max_turns": get_path(cfg, ("agent", "max_turns")),
            "max_live_sessions": cfg.get("max_live_sessions"),
            "context_file_max_chars": cfg.get("context_file_max_chars"),
            "file_read_max_chars": cfg.get("file_read_max_chars"),
            "protect_last_n": get_path(cfg, ("compression", "protect_last_n")),
            "resume_exchanges": get_path(cfg, ("display", "resume_exchanges")),
        },
    }


def build_doctor_data():
    data = build_dashboard_data()
    cfg = load_config()
    return build_doctor_report(data, cfg)

def build_cost_data():
    data = build_dashboard_data()
    calls = parse_recent_api_calls(120)

    # Estimated public/token pricing for Cost v1.
    # Units are dollars per 1M tokens.
    # Unknown models intentionally fall back to conservative configurable defaults.
    pricing = {
        "gpt-5.5": {
            "label": "GPT-5.5",
            "input_per_million": 1.25,
            "output_per_million": 10.00,
            "cached_input_per_million": 0.125,
        },
        "gpt-5": {
            "label": "GPT-5",
            "input_per_million": 1.25,
            "output_per_million": 10.00,
            "cached_input_per_million": 0.125,
        },
        "gpt-4.1": {
            "label": "GPT-4.1",
            "input_per_million": 2.00,
            "output_per_million": 8.00,
            "cached_input_per_million": 0.50,
        },
        "gpt-4.1-mini": {
            "label": "GPT-4.1 Mini",
            "input_per_million": 0.40,
            "output_per_million": 1.60,
            "cached_input_per_million": 0.10,
        },
        "default": {
            "label": "Estimated Default",
            "input_per_million": 1.25,
            "output_per_million": 10.00,
            "cached_input_per_million": 0.125,
        },
    }

    def price_for_model(model_name):
        if not model_name:
            return pricing["default"]

        normalized = str(model_name).lower()

        if normalized in pricing:
            return pricing[normalized]

        for key, value in pricing.items():
            if key != "default" and key in normalized:
                return value

        return pricing["default"]

    def estimate_call(call):
        price = price_for_model(call.get("model"))

        input_tokens = int(call.get("in") or 0)
        output_tokens = int(call.get("out") or 0)
        cached_tokens = int(call.get("cache") or 0)
        billable_input_tokens = max(0, input_tokens - cached_tokens)

        uncached_input_cost = billable_input_tokens / 1_000_000 * price["input_per_million"]
        cached_input_cost = cached_tokens / 1_000_000 * price["cached_input_per_million"]
        output_cost = output_tokens / 1_000_000 * price["output_per_million"]

        estimated_cost = uncached_input_cost + cached_input_cost + output_cost

        no_cache_input_cost = input_tokens / 1_000_000 * price["input_per_million"]
        no_cache_total_cost = no_cache_input_cost + output_cost
        estimated_savings = max(0, no_cache_total_cost - estimated_cost)

        return {
            **call,
            "price_label": price["label"],
            "billable_input_tokens": billable_input_tokens,
            "cached_tokens": cached_tokens,
            "input_cost": uncached_input_cost + cached_input_cost,
            "output_cost": output_cost,
            "estimated_cost": estimated_cost,
            "estimated_savings": estimated_savings,
        }

    estimated_calls = [estimate_call(call) for call in calls]

    total_input_tokens = sum(call["in"] for call in estimated_calls)
    total_output_tokens = sum(call["out"] for call in estimated_calls)
    total_tokens = sum(call["total"] for call in estimated_calls)
    total_cached_tokens = sum(call["cached_tokens"] for call in estimated_calls)
    total_cost = sum(call["estimated_cost"] for call in estimated_calls)
    total_savings = sum(call["estimated_savings"] for call in estimated_calls)

    avg_cost = total_cost / len(estimated_calls) if estimated_calls else 0
    avg_cache = (
        sum(call["pct"] for call in estimated_calls) / len(estimated_calls)
        if estimated_calls
        else 0
    )

    if total_cost < 0.25:
        cost_status = "Low"
        cost_class = "good"
    elif total_cost < 1.00:
        cost_status = "Moderate"
        cost_class = "warn"
    else:
        cost_status = "Elevated"
        cost_class = "bad"

    if total_savings > 0:
        savings_status = "Cache savings active"
        savings_class = "good"
    else:
        savings_status = "No savings detected"
        savings_class = "warn"

    recent_calls = list(reversed(estimated_calls[-20:]))

    data["cost"] = {
        "calls": recent_calls,
        "call_count": len(estimated_calls),
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_tokens": total_tokens,
        "total_cached_tokens": total_cached_tokens,
        "avg_cache": avg_cache,
        "total_cost": total_cost,
        "total_savings": total_savings,
        "avg_cost": avg_cost,
        "cost_status": cost_status,
        "cost_class": cost_class,
        "savings_status": savings_status,
        "savings_class": savings_class,
        "pricing_note": "Estimated from recent Hermes API log entries. This is not a billing statement.",
    }

    return data


def build_models_data():
    from toolkit.models import MODELS

    data = build_dashboard_data()
    active_provider = (data.get("model") or {}).get("provider")
    active_model = (data.get("model") or {}).get("default")
    active_base_url = (data.get("model") or {}).get("base_url")

    provider_labels = {
        "openai-codex": "OpenAI Codex",
        "openrouter": "OpenRouter",
        "anthropic": "Anthropic",
        "ollama": "Ollama",
        "google": "Google AI Studio",
    }

    model_labels = {
        "qwen": {
            "name": "Qwen Coder",
            "description": "Coding-focused OpenRouter preset for software development and agentic engineering work.",
            "tier": "Developer",
            "status": "Available",
        },
        "gemini": {
            "name": "Gemini 2.5 Pro",
            "description": "Large-context OpenRouter preset for analysis, planning, and complex reasoning tasks.",
            "tier": "Reasoning",
            "status": "Available",
        },
        "gpt": {
            "name": "GPT-5.5",
            "description": "Primary OpenAI Codex preset for Hermes Toolkit development and high-quality coding sessions.",
            "tier": "Primary",
            "status": "Available",
        },
    }

    presets = []

    for key, value in MODELS.items():
        provider, model, base_url = value
        meta = model_labels.get(key, {})
        is_active = provider == active_provider and model == active_model

        presets.append({
            "id": key,
            "name": meta.get("name", key),
            "description": meta.get("description", "Configured Hermes model preset."),
            "tier": meta.get("tier", "Preset"),
            "status": "Active" if is_active else meta.get("status", "Available"),
            "provider": provider,
            "provider_label": provider_labels.get(provider, provider),
            "model": model,
            "base_url": base_url,
            "is_active": is_active,
        })

    providers = []
    seen = set()

    for preset in presets:
        provider = preset["provider"]
        if provider in seen:
            continue

        provider_presets = [item for item in presets if item["provider"] == provider]
        seen.add(provider)

        providers.append({
            "id": provider,
            "label": provider_labels.get(provider, provider),
            "preset_count": len(provider_presets),
            "is_active": provider == active_provider,
            "models": [item["model"] for item in provider_presets],
        })

    data["models_page"] = {
        "active_provider": active_provider,
        "active_provider_label": provider_labels.get(active_provider, active_provider),
        "active_model": active_model,
        "active_base_url": active_base_url,
        "presets": presets,
        "providers": providers,
        "preset_count": len(presets),
        "provider_count": len(providers),
        "mode": "Safe model switching",
        "note": "Applying a model updates Hermes configuration only. It does not restart services.",
    }

    return data


def build_sessions_data():
    data = build_dashboard_data()
    calls = parse_recent_api_calls(120)

    settings = data.get("settings") or {}

    def safe_int(value, default=0):
        try:
            if value is None:
                return default
            return int(value)
        except (TypeError, ValueError):
            return default

    max_turns = safe_int(settings.get("max_turns"))
    max_live_sessions = safe_int(settings.get("max_live_sessions"))
    protect_last_n = safe_int(settings.get("protect_last_n"))
    resume_exchanges = safe_int(settings.get("resume_exchanges"))

    session_reset_mode = data.get("session_reset_mode") or "unknown"
    session_reset_idle = safe_int(data.get("session_reset_idle"))
    session_reset_hour = data.get("session_reset_hour")

    total_calls = len(calls)
    total_input = sum(call.get("in", 0) for call in calls)
    total_output = sum(call.get("out", 0) for call in calls)
    total_tokens = sum(call.get("total", 0) for call in calls)
    avg_input = total_input / total_calls if total_calls else 0
    avg_output = total_output / total_calls if total_calls else 0
    avg_total = total_tokens / total_calls if total_calls else 0
    avg_cache = sum(call.get("pct", 0) for call in calls) / total_calls if total_calls else 0

    recent_calls = list(reversed(calls[-12:]))

    cards = []

    def add_card(title, value, detail, severity="good", icon="check-circle"):
        cards.append({
            "title": title,
            "value": value,
            "detail": detail,
            "severity": severity,
            "icon": icon,
        })

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
        recommendations.append({
            "severity": severity,
            "title": title,
            "detail": detail,
        })

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


def build_logs_data():
    from toolkit.config import LOG

    data = build_dashboard_data()
    calls = parse_recent_api_calls(120)

    raw_lines = []
    log_exists = LOG.exists()
    log_size = LOG.stat().st_size if log_exists else 0

    if log_exists:
        raw_lines = LOG.read_text(errors="ignore").splitlines()[-160:]

    def classify_line(line):
        upper = line.upper()

        if "ERROR" in upper or "TRACEBACK" in upper or "EXCEPTION" in upper:
            return "bad"

        if "WARN" in upper or "WARNING" in upper:
            return "warn"

        if "API CALL" in upper:
            return "good"

        return "neutral"

    raw_entries = [
        {
            "line": line,
            "severity": classify_line(line),
        }
        for line in reversed(raw_lines[-80:])
    ]

    error_count = sum(1 for item in raw_entries if item["severity"] == "bad")
    warning_count = sum(1 for item in raw_entries if item["severity"] == "warn")
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
        "log_path": str(LOG),
        "log_size": log_size,
        "log_size_kb": log_size / 1024 if log_size else 0,
        "log_status": log_status,
        "log_class": log_class,
        "log_detail": log_detail,
        "error_count": error_count,
        "warning_count": warning_count,
        "api_count": api_count,
        "raw_entries": raw_entries,
        "recent_calls": recent_calls,
        "note": "Logs v1 is read-only. Filtering, search, export, and live tailing can be added later.",
    }

    return data


def build_skills_data():
    from collections import Counter
    from toolkit.config import LOG

    data = build_dashboard_data()

    raw_lines = []
    if LOG.exists():
        raw_lines = LOG.read_text(errors="ignore").splitlines()[-1000:]

    plugin_keywords = [
        "plugin",
        "plugins",
        "adapter",
        "sidecar",
        "photon",
        "tool",
        "skill",
    ]

    signal_lines = []
    detected_names = Counter()

    for line in raw_lines:
        lowered = line.lower()

        if not any(keyword in lowered for keyword in plugin_keywords):
            continue

        severity = "neutral"
        upper = line.upper()

        if "ERROR" in upper or "TRACEBACK" in upper or "EXCEPTION" in upper:
            severity = "bad"
        elif "WARN" in upper or "WARNING" in upper:
            severity = "warn"
        elif "CONNECTED" in upper or "STARTED" in upper or "LISTENING" in upper:
            severity = "good"

        signal_lines.append({
            "line": line,
            "severity": severity,
        })

        if "photon" in lowered:
            detected_names["Photon"] += 1
        if "sidecar" in lowered:
            detected_names["Sidecar"] += 1
        if "adapter" in lowered:
            detected_names["Adapter"] += 1
        if "spectrum" in lowered:
            detected_names["Spectrum"] += 1

    detected_skills = [
        {
            "name": name,
            "count": count,
            "status": "Detected",
            "severity": "good",
            "description": "Detected from recent Hermes log signals.",
        }
        for name, count in detected_names.most_common()
    ]

    planned_skills = [
        {
            "name": "Installed Skills",
            "status": "Planned",
            "severity": "neutral",
            "description": "Future inventory of installed Hermes skills and extensions.",
            "icon": "blocks",
        },
        {
            "name": "Skill Documentation",
            "status": "Planned",
            "severity": "neutral",
            "description": "Future page links for skill docs, capabilities, and configuration notes.",
            "icon": "book-open",
        },
        {
            "name": "Tool Registry",
            "status": "Planned",
            "severity": "neutral",
            "description": "Future read-only registry of available tools exposed to Hermes Agent.",
            "icon": "wrench",
        },
        {
            "name": "Plugin Health",
            "status": "Planned",
            "severity": "neutral",
            "description": "Future diagnostic status for plugins, adapters, and sidecars.",
            "icon": "activity",
        },
    ]

    if detected_skills:
        skills_status = "Signals Detected"
        skills_class = "good"
        skills_detail = f"{len(detected_skills)} plugin-like signals identified."
    else:
        skills_status = "Inventory Pending"
        skills_class = "warn"
        skills_detail = "No installed skill inventory is available yet."

    recommendations = []

    if detected_skills:
        recommendations.append({
            "severity": "good",
            "title": "Plugin signals are visible",
            "detail": "Hermes Toolkit can detect plugin-like activity from logs. A formal skill registry can build on this later.",
        })
    else:
        recommendations.append({
            "severity": "warn",
            "title": "Add a formal skill registry later",
            "detail": "Skills v1 is read-only and log-derived. A future engine should read installed skills directly.",
        })

    recommendations.append({
        "severity": "neutral",
        "title": "Keep Skills read-only for v0.3 Alpha",
        "detail": "Do not add install, remove, or restart actions until the Hermes skill model is clearly defined.",
    })

    data["skills_page"] = {
        "status": skills_status,
        "status_class": skills_class,
        "detail": skills_detail,
        "detected_skills": detected_skills,
        "planned_skills": planned_skills,
        "signal_lines": list(reversed(signal_lines[-40:])),
        "signal_count": len(signal_lines),
        "recommendations": recommendations,
        "note": "Skills v1 is a read-only foundation. It does not install, remove, restart, or modify Hermes plugins.",
    }

    return data


def build_memory_data():
    from toolkit.config import LOG

    data = build_dashboard_data()
    calls = parse_recent_api_calls(120)
    settings = data.get("settings") or {}

    def safe_int(value, default=0):
        try:
            if value is None:
                return default
            return int(value)
        except (TypeError, ValueError):
            return default

    context_file_max_chars = safe_int(settings.get("context_file_max_chars"))
    file_read_max_chars = safe_int(settings.get("file_read_max_chars"))
    protect_last_n = safe_int(settings.get("protect_last_n"))
    resume_exchanges = safe_int(settings.get("resume_exchanges"))
    max_turns = safe_int(settings.get("max_turns"))
    max_live_sessions = safe_int(settings.get("max_live_sessions"))

    session_reset_mode = data.get("session_reset_mode") or "unknown"
    session_reset_idle = safe_int(data.get("session_reset_idle"))

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

    raw_lines = []
    if LOG.exists():
        raw_lines = LOG.read_text(errors="ignore").splitlines()[-1000:]

    memory_keywords = [
        "cache",
        "context",
        "compression",
        "session",
        "resume",
        "memory",
        "evict",
        "idle",
    ]

    signal_lines = []

    for line in raw_lines:
        lowered = line.lower()

        if not any(keyword in lowered for keyword in memory_keywords):
            continue

        severity = "neutral"
        upper = line.upper()

        if "ERROR" in upper or "TRACEBACK" in upper or "EXCEPTION" in upper:
            severity = "bad"
        elif "WARN" in upper or "WARNING" in upper:
            severity = "warn"
        elif "EVICT" in upper or "CACHE" in upper or "SESSION" in upper:
            severity = "good"

        signal_lines.append({
            "line": line,
            "severity": severity,
        })

    cards = []

    def add_card(title, value, detail, severity="good", icon="brain"):
        cards.append({
            "title": title,
            "value": value,
            "detail": detail,
            "severity": severity,
            "icon": icon,
        })

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

    if avg_cache >= 85:
        memory_status = "Efficient"
        memory_class = "good"
        memory_detail = "Recent cache behavior suggests efficient context reuse."
    elif avg_cache >= 50:
        memory_status = "Review"
        memory_class = "warn"
        memory_detail = "Cache behavior is acceptable but could be improved."
    else:
        memory_status = "Inefficient"
        memory_class = "bad"
        memory_detail = "Low cache behavior may indicate excess context churn."

    recommendations = []

    def recommend(severity, title, detail):
        recommendations.append({
            "severity": severity,
            "title": title,
            "detail": detail,
        })

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

    planned_areas = [
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

    data["memory_page"] = {
        "status": memory_status,
        "status_class": memory_class,
        "detail": memory_detail,
        "cards": cards,
        "recommendations": recommendations,
        "planned_areas": planned_areas,
        "signal_lines": list(reversed(signal_lines[-50:])),
        "signal_count": len(signal_lines),
        "avg_cache": avg_cache,
        "avg_input": avg_input,
        "total_cached_tokens": total_cached_tokens,
        "total_calls": total_calls,
        "context_file_max_chars": context_file_max_chars,
        "file_read_max_chars": file_read_max_chars,
        "protect_last_n": protect_last_n,
        "resume_exchanges": resume_exchanges,
        "max_turns": max_turns,
        "max_live_sessions": max_live_sessions,
        "session_reset_mode": session_reset_mode,
        "session_reset_idle": session_reset_idle,
        "note": "Memory v1 is read-only and config/log-derived. It does not inspect, delete, export, or modify memory stores.",
    }

    return data


def build_about_data():
    import platform
    from toolkit import __version__

    data = build_dashboard_data()

    completed_pages = [
        {
            "name": "Dashboard",
            "status": "Complete",
            "description": "Core operations overview with health, usage, provider, and recent activity.",
            "icon": "layout-dashboard",
        },
        {
            "name": "Analytics",
            "status": "Complete",
            "description": "Charts and usage visibility for parsed Hermes API activity.",
            "icon": "chart-line",
        },
        {
            "name": "Cost",
            "status": "Foundation",
            "description": "Estimated token cost, cache savings, and recent call cost context.",
            "icon": "circle-dollar-sign",
        },
        {
            "name": "Doctor",
            "status": "v1.1",
            "description": "Grouped diagnostics, recommendations, and non-destructive diagnostic action.",
            "icon": "stethoscope",
        },
        {
            "name": "Configuration",
            "status": "Complete",
            "description": "Profile, model, and core configuration editor.",
            "icon": "settings",
        },
        {
            "name": "Models",
            "status": "Foundation",
            "description": "Known-good model presets and safe config-only model switching.",
            "icon": "bot",
        },
        {
            "name": "Sessions",
            "status": "Foundation",
            "description": "Session limits, reset behavior, and recent activity proxy.",
            "icon": "messages-square",
        },
        {
            "name": "Logs",
            "status": "Foundation",
            "description": "Read-only raw logs, parsed API calls, warning counts, and error counts.",
            "icon": "scroll-text",
        },
        {
            "name": "Skills",
            "status": "Foundation",
            "description": "Read-only foundation for skills, plugins, tools, and adapters.",
            "icon": "blocks",
        },
        {
            "name": "Memory",
            "status": "Foundation",
            "description": "Read-only memory, context, cache, and compression overview.",
            "icon": "brain",
        },
    ]

    next_steps = [
        "Update README with the completed v0.3 Alpha dashboard pages.",
        "Capture updated screenshots for Dashboard, Doctor, Cost, Models, Sessions, Logs, Skills, and Memory.",
        "Update changelog and version references.",
        "Review estimated pricing language before public release.",
        "Tag Hermes Toolkit v0.3 Alpha.",
    ]

    principles = [
        {
            "title": "Non-destructive by default",
            "description": "Diagnostic and observability pages avoid restarts, deletes, installs, or hidden mutations.",
            "icon": "shield-check",
        },
        {
            "title": "Operational honesty",
            "description": "Foundation pages clearly identify log-derived or estimated data instead of pretending full engines exist.",
            "icon": "badge-check",
        },
        {
            "title": "Frozen visual language",
            "description": "Graphite, gold accent, rounded cards, Lucide icons, and engineering dashboard style remain consistent.",
            "icon": "palette",
        },
        {
            "title": "Open-source architecture",
            "description": "Hermes Toolkit is being structured as a real public management product, not a one-off local script.",
            "icon": "git-branch",
        },
    ]

    data["about_page"] = {
        "version": __version__,
        "release_label": "v0.3 Alpha",
        "project_name": "Hermes Toolkit",
        "tagline": "Control. Optimize. Evolve.",
        "description": "Hermes Toolkit is an open-source administration dashboard and CLI companion for Hermes Agent.",
        "runtime": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "system": platform.system(),
            "machine": platform.machine(),
        },
        "completed_pages": completed_pages,
        "next_steps": next_steps,
        "principles": principles,
        "page_count": len(completed_pages),
        "status": "Alpha",
        "status_class": "good",
        "note": "About v1 is informational only. It does not modify Hermes Agent or Hermes Toolkit configuration.",
    }

    return data


@app.get("/analytics", response_class=HTMLResponse)
async def analytics(request: Request):
    data = build_dashboard_data()
    return templates.TemplateResponse(
        "analytics.html",
        {
            "request": request,
            "data": data,
        },
    )


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "data": build_dashboard_data(),
        },
    )

from fastapi import Form
from fastapi.responses import RedirectResponse
from toolkit.config import save_config, set_path
from toolkit.profiles import apply_profile
from toolkit.models import apply_model



@app.get("/cost", response_class=HTMLResponse)
async def cost_page(request: Request):
    return templates.TemplateResponse(
        "cost.html",
        {
            "request": request,
            "data": build_cost_data(),
        },
    )



@app.get("/models", response_class=HTMLResponse)
async def models_page(request: Request):
    return templates.TemplateResponse(
        "models.html",
        {
            "request": request,
            "data": build_models_data(),
        },
    )


@app.post("/models/apply")
async def models_apply(model: str = Form(...)):
    cfg = load_config()
    apply_model(cfg, model, set_path)
    save_config(cfg)
    return RedirectResponse("/models?saved=1", status_code=303)



@app.get("/sessions", response_class=HTMLResponse)
async def sessions_page(request: Request):
    return templates.TemplateResponse(
        "sessions.html",
        {
            "request": request,
            "data": build_sessions_data(),
        },
    )



@app.get("/logs", response_class=HTMLResponse)
async def logs_page(request: Request):
    return templates.TemplateResponse(
        "logs.html",
        {
            "request": request,
            "data": build_logs_data(),
        },
    )



@app.get("/skills", response_class=HTMLResponse)
async def skills_page(request: Request):
    return templates.TemplateResponse(
        "skills.html",
        {
            "request": request,
            "data": build_skills_data(),
        },
    )



@app.get("/memory", response_class=HTMLResponse)
async def memory_page(request: Request):
    return templates.TemplateResponse(
        "memory.html",
        {
            "request": request,
            "data": build_memory_data(),
        },
    )



@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    return templates.TemplateResponse(
        "about.html",
        {
            "request": request,
            "data": build_about_data(),
        },
    )


@app.get("/doctor", response_class=HTMLResponse)
async def doctor_page(request: Request):
    return templates.TemplateResponse(
        "doctor.html",
        {
            "request": request,
            "data": build_doctor_data(),
        },
    )



@app.post("/doctor/run")
async def doctor_run():
    # Doctor v1.1 full diagnostic action is intentionally non-destructive.
    # It refreshes the generated diagnostic data by redirecting back to the page.
    return RedirectResponse("/doctor?ran=1", status_code=303)


@app.get("/configuration", response_class=HTMLResponse)
async def configuration(request: Request):
    return templates.TemplateResponse(
        "configuration.html",
        {
            "request": request,
            "data": build_dashboard_data(),
        },
    )


@app.post("/configuration/profile")
async def configuration_profile(profile: str = Form(...)):
    cfg = load_config()
    apply_profile(cfg, profile, set_path)
    save_config(cfg)
    return RedirectResponse("/configuration?saved=1", status_code=303)


@app.post("/configuration/model")
async def configuration_model(model: str = Form(...)):
    cfg = load_config()
    apply_model(cfg, model, set_path)
    save_config(cfg)
    return RedirectResponse("/configuration?saved=1", status_code=303)


@app.post("/configuration/settings")
async def configuration_settings(
    max_turns: int = Form(...),
    max_live_sessions: int = Form(...),
    context_file_max_chars: int = Form(...),
    file_read_max_chars: int = Form(...),
    protect_last_n: int = Form(...),
    resume_exchanges: int = Form(...),
    session_reset_mode: str = Form(...),
    session_reset_idle_minutes: int = Form(...),
    session_reset_at_hour: int = Form(...),
):
    cfg = load_config()

    set_path(cfg, ("agent", "max_turns"), max_turns)
    set_path(cfg, ("max_live_sessions",), max_live_sessions)
    set_path(cfg, ("context_file_max_chars",), context_file_max_chars)
    set_path(cfg, ("file_read_max_chars",), file_read_max_chars)
    set_path(cfg, ("compression", "protect_last_n"), protect_last_n)
    set_path(cfg, ("display", "resume_exchanges"), resume_exchanges)
    set_path(cfg, ("session_reset", "mode"), session_reset_mode)
    set_path(cfg, ("session_reset", "idle_minutes"), session_reset_idle_minutes)
    set_path(cfg, ("session_reset", "at_hour"), session_reset_at_hour)

    save_config(cfg)
    return RedirectResponse("/configuration?saved=1", status_code=303)
