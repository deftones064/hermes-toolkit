from toolkit import __version__
from toolkit.about_page import (
    RELEASE_ARTIFACT,
    RELEASE_LABEL,
    RELEASE_PHASE,
    RELEASE_SUMMARY,
)
from toolkit.release_status import build_release_status_data


def test_build_release_status_data_shape():
    data = build_release_status_data()

    assert data["package_version"] == __version__
    assert data["release_label"] == RELEASE_LABEL
    assert data["release_phase"] == RELEASE_PHASE
    assert data["release_artifact"] == RELEASE_ARTIFACT
    assert data["release_summary"] == RELEASE_SUMMARY
    assert data["source"] == "package metadata and About release metadata"


def test_build_release_status_data_is_read_only():
    data = build_release_status_data()
    guardrails = data["guardrails"]

    assert guardrails["git_probing"] == "Disabled"
    assert guardrails["subprocess_execution"] == "Disabled"
    assert guardrails["service_mutation"] == "Disabled"
    assert guardrails["tag_mutation"] == "Disabled"
    assert guardrails["config_mutation"] == "Disabled"


def test_build_release_status_data_has_no_live_probe_claims():
    data = build_release_status_data()

    assert data["repository_branch"] == "Not probed"
    assert data["repository_commit"] == "Not probed"
    assert data["repository_dirty_state"] == "Not probed"
    assert data["service_state"] == "Not probed"


def test_build_release_status_data_includes_display_cards():
    data = build_release_status_data()
    cards = data["cards"]

    assert [card["title"] for card in cards] == [
        "Package Version",
        "Release Artifact",
        "Repository State",
        "Service State",
    ]

    assert cards[0]["value"] == __version__
    assert cards[0]["badge"] == "read-only"
    assert cards[0]["state"] == "available"

    assert cards[1]["value"] == RELEASE_ARTIFACT
    assert cards[1]["badge"] == RELEASE_PHASE
    assert cards[1]["state"] == "available"

    assert cards[2]["value"] == "Not probed / Not probed / Not probed"
    assert cards[2]["badge"] == "planned"
    assert cards[2]["state"] == "planned"

    assert cards[3]["value"] == "Not probed"
    assert cards[3]["badge"] == "read-only"
    assert cards[3]["state"] == "planned"
