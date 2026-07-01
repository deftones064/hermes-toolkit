from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from toolkit.about_page import build_about_data as build_about_report
from toolkit.config import load_config, get_path
from toolkit.logs import parse_recent_api_calls
from toolkit.logs_page import build_logs_data as build_logs_report
from toolkit.logs_page import build_logs_export_text as build_logs_export_report
from toolkit.memory_page import build_memory_data as build_memory_report
from toolkit.models_page import build_models_page_data as build_models_report
from toolkit.cost import build_cost_data as build_cost_report
from toolkit.doctor import doctor, build_doctor_data as build_doctor_report
from toolkit.sessions import build_sessions_data as build_sessions_report
from toolkit.skills_page import build_skills_data as build_skills_report

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
    cfg = load_config()
    calls = parse_recent_api_calls(120)
    return build_cost_report(data, calls, cfg=cfg)

def build_models_data():
    data = build_dashboard_data()
    return build_models_report(data)

def build_sessions_data(provider="all", query=""):
    data = build_dashboard_data()
    cfg = load_config()
    calls = parse_recent_api_calls(120)
    return build_sessions_report(data, cfg, calls, provider=provider, query=query)

def build_logs_data(severity="all", query=""):
    from toolkit.config import LOG

    data = build_dashboard_data()
    calls = parse_recent_api_calls(120)
    return build_logs_report(data, LOG, calls, severity=severity, query=query)


def build_logs_export_text(severity="all", query=""):
    data = build_logs_data(severity=severity, query=query)
    return build_logs_export_report(data)

def build_skills_data():
    from toolkit.config import LOG

    data = build_dashboard_data()
    return build_skills_report(data, LOG)

def build_memory_data():
    from toolkit.config import LOG

    data = build_dashboard_data()
    calls = parse_recent_api_calls(120)
    return build_memory_report(data, calls, LOG)

def build_about_data():
    data = build_dashboard_data()
    return build_about_report(data)


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
async def sessions_page(request: Request, provider: str = "all", q: str = ""):
    return templates.TemplateResponse(
        "sessions.html",
        {
            "request": request,
            "data": build_sessions_data(provider=provider, query=q),
        },
    )



@app.get("/logs", response_class=HTMLResponse)
async def logs_page(request: Request, severity: str = "all", q: str = ""):
    return templates.TemplateResponse(
        "logs.html",
        {
            "request": request,
            "data": build_logs_data(severity=severity, query=q),
        },
    )


@app.get("/logs/export", response_class=PlainTextResponse)
async def logs_export(severity: str = "all", q: str = ""):
    return PlainTextResponse(
        build_logs_export_text(severity=severity, query=q),
        media_type="text/plain",
        headers={"Content-Disposition": "attachment; filename=hermes-toolkit-logs.txt"},
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
