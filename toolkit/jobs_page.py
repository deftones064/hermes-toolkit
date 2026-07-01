PLANNED_JOB_AREAS = [
    {
        "name": "Scheduled Jobs",
        "status": "Planned",
        "description": "Future read-only view of configured recurring jobs, scheduled checks, and maintenance windows.",
        "icon": "calendar-clock",
    },
    {
        "name": "Background Tasks",
        "status": "Planned",
        "description": "Future read-only view of active or recently completed background task activity.",
        "icon": "list-checks",
    },
    {
        "name": "Maintenance Actions",
        "status": "Planned",
        "description": "Future explicit maintenance actions such as safe cleanup, diagnostics, or refresh workflows.",
        "icon": "wrench",
    },
    {
        "name": "Automation Hooks",
        "status": "Planned",
        "description": "Future integration points for external schedulers, Home Assistant, or notification workflows.",
        "icon": "workflow",
    },
]


def build_job_readiness_items(cfg):
    toolkit_cfg = cfg.get("toolkit") or {}

    return [
        {
            "name": "Job Registry",
            "status": "planned",
            "summary": "No job registry is configured yet.",
            "detail": "A future backend registry can expose known jobs without executing them from the page.",
            "icon": "database",
        },
        {
            "name": "Scheduler Settings",
            "status": "available" if toolkit_cfg.get("jobs") else "planned",
            "summary": "Scheduler configuration is not active yet." if not toolkit_cfg.get("jobs") else "Scheduler configuration detected.",
            "detail": "Future read-only scheduler settings can be surfaced here when configuration exists.",
            "icon": "settings",
        },
        {
            "name": "Task Activity",
            "status": "limited",
            "summary": "No task activity parser is connected yet.",
            "detail": "Future task activity can be derived from logs without mutating runtime state.",
            "icon": "activity",
        },
        {
            "name": "Action Safety",
            "status": "available",
            "summary": "Jobs page foundation is read-only.",
            "detail": "No jobs are started, stopped, retried, deleted, or scheduled by this foundation.",
            "icon": "shield-check",
        },
    ]


def build_jobs_data(dashboard_data, cfg):
    data = dict(dashboard_data)
    readiness_items = build_job_readiness_items(cfg)

    data["jobs_page"] = {
        "status": "Foundation",
        "status_class": "warn",
        "detail": "Jobs / Tasks foundation is read-only and does not execute or schedule work.",
        "planned_areas": PLANNED_JOB_AREAS,
        "readiness_items": readiness_items,
        "readiness_count": len(readiness_items),
        "available_readiness_count": sum(
            1 for item in readiness_items
            if item["status"] == "available"
        ),
        "note": "Jobs v1 foundation is read-only. It provides planning and readiness structure without starting, stopping, retrying, deleting, or scheduling tasks.",
    }

    return data
