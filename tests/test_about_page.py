from pathlib import Path

from toolkit import __version__
from toolkit.about_page import (
    RELEASE_ARTIFACT,
    RELEASE_LABEL,
    RELEASE_PHASE,
    RELEASE_SUMMARY,
    build_about_data,
    build_release_metadata,
)


def test_build_release_metadata_uses_release_constants():
    metadata = build_release_metadata()

    assert metadata == {
        "label": RELEASE_LABEL,
        "phase": RELEASE_PHASE,
        "artifact": RELEASE_ARTIFACT,
        "summary": RELEASE_SUMMARY,
    }


def test_build_about_data_shape():
    data = build_about_data({})
    about_page = data["about_page"]

    assert about_page["version"] == __version__
    assert about_page["release_label"] == RELEASE_LABEL
    assert about_page["project_name"] == "Hermes Toolkit"
    assert about_page["tagline"] == "Control. Optimize. Evolve."
    assert about_page["status"] == "Alpha"
    assert about_page["status_class"] == "good"
    assert about_page["page_count"] == len(about_page["completed_pages"])
    assert about_page["runtime"]["python"]
    assert about_page["runtime"]["system"]
    assert about_page["runtime"]["machine"]


def test_build_about_data_preserves_dashboard_data():
    data = build_about_data({"health_score": 100})

    assert data["health_score"] == 100
    assert "about_page" in data


def test_build_about_data_lists_expected_pages():
    data = build_about_data({})
    page_names = {
        page["name"]
        for page in data["about_page"]["completed_pages"]
    }

    assert "Dashboard" in page_names
    assert "Doctor" in page_names
    assert "Cost" in page_names
    assert "Models" in page_names
    assert "Sessions" in page_names
    assert "Logs" in page_names
    assert "Skills" in page_names
    assert "Memory" in page_names
    assert "System Inventory" in page_names
    assert "Backup / Restore" in page_names
    assert "Updates" in page_names


def test_build_about_data_is_informational_only():
    data = build_about_data({})
    about_page = data["about_page"]

    assert "informational only" in about_page["note"]
    assert "does not modify" in about_page["note"]
    assert any(
        principle["title"] == "Non-destructive by default"
        for principle in about_page["principles"]
    )


def test_build_about_data_next_steps_are_current():
    data = build_about_data({})
    next_steps = data["about_page"]["next_steps"]

    assert any("next alpha release" in step for step in next_steps)
    assert any("backup, restore, and update execution disabled" in step for step in next_steps)
    assert not any("v0.4 Alpha" in step for step in next_steps)


def test_build_about_data_release_status_is_post_release():
    data = build_about_data({})
    about_page = data["about_page"]

    assert about_page["release_label"] == RELEASE_LABEL
    assert about_page["release_phase"] == RELEASE_PHASE
    assert about_page["release_artifact"] == RELEASE_ARTIFACT
    assert about_page["release_summary"] == RELEASE_SUMMARY
    assert "post-release" in about_page["release_summary"].lower()


def test_about_sources_do_not_contain_stale_release_labels():
    stale_terms = [
        "v0.3 Alpha",
        "v0.4 Alpha",
        "v0.5 Alpha",
        "v0.6 Alpha",
        "Pre-release polish",
        "About v1",
        "Before Release",
    ]

    source_paths = [
        Path("toolkit/about_page.py"),
        Path("toolkit/templates/about.html"),
    ]

    for source_path in source_paths:
        source_text = source_path.read_text()
        for stale_term in stale_terms:
            assert stale_term not in source_text


def test_about_template_uses_post_release_wording():
    template = Path("toolkit/templates/about.html").read_text()

    assert "Release Status" in template
    assert "Current phase" in template
    assert "Release artifact" in template
    assert "Next Alpha Prep" in template
    assert "post-release" in template.lower()
    assert "Pre-release polish" not in template
    assert "Before Release" not in template
    assert "after About v1 lands" not in template
