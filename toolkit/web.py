from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from toolkit.config import load_config, get_path
from toolkit.logs import parse_recent_api_calls
from toolkit.doctor import doctor

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
