from collections import Counter


PLUGIN_KEYWORDS = [
    "plugin",
    "plugins",
    "adapter",
    "sidecar",
    "photon",
    "tool",
    "skill",
]


PLANNED_SKILLS = [
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


def classify_skill_signal(line):
    upper = line.upper()

    if "ERROR" in upper or "TRACEBACK" in upper or "EXCEPTION" in upper:
        return "bad"

    if "WARN" in upper or "WARNING" in upper:
        return "warn"

    if "CONNECTED" in upper or "STARTED" in upper or "LISTENING" in upper:
        return "good"

    return "neutral"


def _detect_skill_name_counts(lines):
    detected_names = Counter()

    for line in lines:
        lowered = line.lower()

        if "photon" in lowered:
            detected_names["Photon"] += 1
        if "sidecar" in lowered:
            detected_names["Sidecar"] += 1
        if "adapter" in lowered:
            detected_names["Adapter"] += 1
        if "spectrum" in lowered:
            detected_names["Spectrum"] += 1

    return detected_names


def _build_detected_skills(detected_names):
    return [
        {
            "name": name,
            "count": count,
            "status": "Detected",
            "severity": "good",
            "description": "Detected from recent Hermes log signals.",
        }
        for name, count in detected_names.most_common()
    ]


def _build_recommendations(detected_skills):
    recommendations = []

    if detected_skills:
        recommendations.append(
            {
                "severity": "good",
                "title": "Plugin signals are visible",
                "detail": "Hermes Toolkit can detect plugin-like activity from logs. A formal skill registry can build on this later.",
            }
        )
    else:
        recommendations.append(
            {
                "severity": "warn",
                "title": "Add a formal skill registry later",
                "detail": "Skills v1 is read-only and log-derived. A future engine should read installed skills directly.",
            }
        )

    recommendations.append(
        {
            "severity": "neutral",
            "title": "Keep Skills read-only for v0.3 Alpha",
            "detail": "Do not add install, remove, or restart actions until the Hermes skill model is clearly defined.",
        }
    )

    return recommendations


def build_skills_data(dashboard_data, log_path):
    data = dict(dashboard_data)

    raw_lines = []
    if log_path.exists():
        raw_lines = log_path.read_text(errors="ignore").splitlines()[-1000:]

    signal_lines = []

    for line in raw_lines:
        lowered = line.lower()

        if not any(keyword in lowered for keyword in PLUGIN_KEYWORDS):
            continue

        signal_lines.append(
            {
                "line": line,
                "severity": classify_skill_signal(line),
            }
        )

    detected_names = _detect_skill_name_counts(
        entry["line"] for entry in signal_lines
    )
    detected_skills = _build_detected_skills(detected_names)

    if detected_skills:
        skills_status = "Signals Detected"
        skills_class = "good"
        skills_detail = f"{len(detected_skills)} plugin-like signals identified."
    else:
        skills_status = "Inventory Pending"
        skills_class = "warn"
        skills_detail = "No installed skill inventory is available yet."

    data["skills_page"] = {
        "status": skills_status,
        "status_class": skills_class,
        "detail": skills_detail,
        "detected_skills": detected_skills,
        "planned_skills": PLANNED_SKILLS,
        "signal_lines": list(reversed(signal_lines[-40:])),
        "signal_count": len(signal_lines),
        "recommendations": _build_recommendations(detected_skills),
        "note": "Skills v1 is a read-only foundation. It does not install, remove, restart, or modify Hermes plugins.",
    }

    return data
