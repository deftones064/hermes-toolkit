from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from toolkit.about_page import build_about_data as build_about_report
from toolkit.backup_page import build_backup_page_data as build_backup_report
from toolkit.config import load_config, save_config, set_path
from toolkit.logs import parse_recent_api_calls
from toolkit.logs_page import build_logs_data as build_logs_report
from toolkit.logs_page import build_logs_export_text as build_logs_export_report
from toolkit.memory_page import build_memory_data as build_memory_report
from toolkit.models import apply_model
from toolkit.models_page import build_models_page_data as build_models_report
from toolkit.profiles import apply_profile
from toolkit.cost import build_cost_data as build_cost_report
from toolkit.dashboard import build_dashboard_data as build_dashboard_report
from toolkit.doctor import doctor, build_doctor_data as build_doctor_report
from toolkit.home_assistant_page import build_home_assistant_data as build_home_assistant_report
from toolkit.jobs_page import build_jobs_data as build_jobs_report
from toolkit.sessions import build_sessions_data as build_sessions_report
from toolkit.skills_page import build_skills_data as build_skills_report
from toolkit.telegram_page import build_telegram_data as build_telegram_report

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "toolkit" / "templates"))

app = FastAPI(title="Hermes Toolkit")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "toolkit" / "static")), name="static")


def build_dashboard_data():
    return build_dashboard_report()


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

def build_telegram_data():
    data = build_dashboard_data()
    cfg = load_config()
    return build_telegram_report(data, cfg)


def build_home_assistant_data():
    data = build_dashboard_data()
    cfg = load_config()
    return build_home_assistant_report(data, cfg)


def build_jobs_data():
    data = build_dashboard_data()
    cfg = load_config()
    return build_jobs_report(data, cfg)



def build_backup_data():
    return build_backup_report()

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



@app.get("/telegram", response_class=HTMLResponse)
async def telegram_page(request: Request):
    return templates.TemplateResponse(
        "telegram.html",
        {
            "request": request,
            "data": build_telegram_data(),
        },
    )



@app.get("/home-assistant", response_class=HTMLResponse)
async def home_assistant_page(request: Request):
    return templates.TemplateResponse(
        "home_assistant.html",
        {
            "request": request,
            "data": build_home_assistant_data(),
        },
    )



@app.get("/jobs", response_class=HTMLResponse)
async def jobs_page(request: Request):
    return templates.TemplateResponse(
        "jobs.html",
        {
            "request": request,
            "data": build_jobs_data(),
        },
    )




@app.get("/backup", response_class=HTMLResponse)
async def backup_page(request: Request):
    return templates.TemplateResponse(
        "backup.html",
        {
            "request": request,
            "data": build_backup_data(),
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
