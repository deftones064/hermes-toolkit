import platform

from toolkit import __version__


COMPLETED_PAGES = [
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
    {
        "name": "System Inventory",
        "status": "Foundation",
        "description": "Read-only planning surface for runtime, repository, configuration, and service inventory.",
        "icon": "server-cog",
    },
    {
        "name": "Backup / Restore",
        "status": "Foundation",
        "description": "Read-only planning surface for backup sources, destinations, restore points, and restore guardrails.",
        "icon": "archive-restore",
    },
    {
        "name": "Updates",
        "status": "Foundation",
        "description": "Read-only planning surface for version sources, update channels, pending changes, and update guardrails.",
        "icon": "download-cloud",
    },
]


NEXT_STEPS = [
    "Review README and CHANGELOG for the next alpha release.",
    "Capture updated screenshots for Dashboard, Doctor, Backup / Restore, Updates, and other foundation pages.",
    "Verify version references, release notes, and test status before tagging.",
    "Keep backup, restore, and update execution disabled until guarded workflows are intentionally designed.",
]


PRINCIPLES = [
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


def build_about_data(dashboard_data):
    data = dict(dashboard_data)

    data["about_page"] = {
        "version": __version__,
        "release_label": "v0.5 Alpha",
        "project_name": "Hermes Toolkit",
        "tagline": "Control. Optimize. Evolve.",
        "description": "Hermes Toolkit is an open-source administration dashboard and CLI companion for Hermes Agent.",
        "runtime": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "system": platform.system(),
            "machine": platform.machine(),
        },
        "completed_pages": COMPLETED_PAGES,
        "next_steps": NEXT_STEPS,
        "principles": PRINCIPLES,
        "page_count": len(COMPLETED_PAGES),
        "status": "Alpha",
        "status_class": "good",
        "note": "About v1 is informational only. It does not modify Hermes Agent or Hermes Toolkit configuration.",
    }

    return data
