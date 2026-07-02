from toolkit import __version__
from toolkit.about_page import build_release_metadata


def build_release_status_data() -> dict[str, object]:
    release = build_release_metadata()

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
        "guardrails": {
            "git_probing": "Disabled",
            "subprocess_execution": "Disabled",
            "service_mutation": "Disabled",
            "tag_mutation": "Disabled",
            "config_mutation": "Disabled",
        },
    }
