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
