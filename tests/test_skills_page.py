from toolkit.skills_page import build_skill_registry_items, build_skills_data, classify_skill_signal


def test_classify_skill_signal():
    assert classify_skill_signal("ERROR plugin crashed") == "bad"
    assert classify_skill_signal("WARNING adapter slow") == "warn"
    assert classify_skill_signal("Photon plugin STARTED") == "good"
    assert classify_skill_signal("plugin heartbeat") == "neutral"


def test_build_skills_data_detects_plugin_signals(tmp_path):
    log_path = tmp_path / "hermes.log"
    log_path.write_text(
        "\n".join(
            [
                "INFO startup complete",
                "INFO Photon plugin STARTED",
                "WARNING sidecar adapter degraded",
                "ERROR spectrum tool failed",
            ]
        )
    )

    data = build_skills_data({}, log_path)
    skills_page = data["skills_page"]

    assert skills_page["status"] == "Signals Detected"
    assert skills_page["status_class"] == "good"
    assert skills_page["signal_count"] == 3
    assert len(skills_page["signal_lines"]) == 3

    names = {
        skill["name"]: skill["count"]
        for skill in skills_page["detected_skills"]
    }

    assert names["Photon"] == 1
    assert names["Sidecar"] == 1
    assert names["Adapter"] == 1
    assert names["Spectrum"] == 1

    severities = {
        entry["severity"]
        for entry in skills_page["signal_lines"]
    }

    assert {"good", "warn", "bad"} <= severities


def test_build_skills_data_handles_missing_log(tmp_path):
    log_path = tmp_path / "missing.log"

    data = build_skills_data({}, log_path)
    skills_page = data["skills_page"]

    assert skills_page["status"] == "Inventory Pending"
    assert skills_page["status_class"] == "warn"
    assert skills_page["detected_skills"] == []
    assert skills_page["signal_lines"] == []
    assert skills_page["signal_count"] == 0
    assert skills_page["planned_skills"]


def test_build_skills_data_recommendations_are_read_only(tmp_path):
    log_path = tmp_path / "missing.log"

    data = build_skills_data({}, log_path)
    recommendations = data["skills_page"]["recommendations"]

    assert any(
        item["title"] == "Keep Skills read-only for v0.3 Alpha"
        for item in recommendations
    )
    assert "does not install, remove, restart, or modify" in data["skills_page"]["note"]


def test_build_skill_registry_items_default_shape():
    items = build_skill_registry_items({})

    by_name = {item["name"]: item for item in items}

    assert by_name["Registry Source"]["status"] == "planned"
    assert by_name["Skill Directories"]["status"] == "planned"
    assert by_name["Skill Manifest"]["status"] == "planned"
    assert by_name["Action Safety"]["status"] == "available"


def test_build_skill_registry_items_detects_config():
    items = build_skill_registry_items(
        {
            "toolkit": {
                "skills": {
                    "registry_path": "/opt/hermes/skills/registry.json",
                    "skill_dirs": ["/opt/hermes/skills"],
                    "manifest_file": "skills.yaml",
                },
            },
        }
    )

    by_name = {item["name"]: item for item in items}

    assert by_name["Registry Source"]["status"] == "available"
    assert by_name["Skill Directories"]["status"] == "available"
    assert by_name["Skill Manifest"]["status"] == "available"
    assert by_name["Action Safety"]["status"] == "available"


def test_build_skills_data_includes_registry_foundation(tmp_path):
    log_path = tmp_path / "missing.log"

    data = build_skills_data({}, log_path)
    skills_page = data["skills_page"]

    assert skills_page["skill_registry_count"] == 4
    assert skills_page["available_skill_registry_count"] == 1
    assert skills_page["skill_registry_items"]
    assert skills_page["skill_registry_items"][-1]["name"] == "Action Safety"
