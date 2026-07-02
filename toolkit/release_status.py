from toolkit import __version__
from toolkit.about_page import build_release_metadata


def build_release_status_cards(
    package_version: str,
    release: dict[str, str],
) -> list[dict[str, str]]:
    return [
        {
            "title": "Package Version",
            "description": "In-process package version metadata.",
            "value": package_version,
            "badge": "read-only",
            "state": "available",
            "icon": "badge-info",
        },
        {
            "title": "Release Artifact",
            "description": release["summary"],
            "value": release["artifact"],
            "badge": release["phase"],
            "state": "available",
            "icon": "tag",
        },
        {
            "title": "Repository State",
            "description": "Branch, commit, and dirty-state awareness are intentionally not probed.",
            "value": "Not probed / Not probed / Not probed",
            "badge": "planned",
            "state": "planned",
            "icon": "git-branch",
        },
        {
            "title": "Service State",
            "description": "Service mutation disabled. Service state is intentionally not probed.",
            "value": "Not probed",
            "badge": "read-only",
            "state": "planned",
            "icon": "shield-x",
        },
    ]


def build_release_status_data() -> dict[str, object]:
    release = build_release_metadata()
    cards = build_release_status_cards(__version__, release)

    return {
        "package_version": __version__,
        "release_label": release["label"],
        "release_phase": release["phase"],
        "release_artifact": release["artifact"],
        "release_summary": release["summary"],
        "source": "package metadata and About release metadata",
        "repository_branch": "Not probed",
        "repository_commit": "Not probed",
        "repository_dirty_state": "Not probed",
        "service_state": "Not probed",
        "cards": cards,
        "guardrails": {
            "git_probing": "Disabled",
            "subprocess_execution": "Disabled",
            "service_mutation": "Disabled",
            "tag_mutation": "Disabled",
            "config_mutation": "Disabled",
        },
    }
