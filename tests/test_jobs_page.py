from toolkit.jobs_page import build_job_readiness_items, build_jobs_data


def _dashboard_data():
    return {
        "health_status": "Excellent",
        "health_class": "good",
    }


def test_build_job_readiness_items_default_shape():
    items = build_job_readiness_items({})

    by_name = {item["name"]: item for item in items}

    assert by_name["Job Registry"]["status"] == "planned"
    assert by_name["Scheduler Settings"]["status"] == "planned"
    assert by_name["Task Activity"]["status"] == "limited"
    assert by_name["Action Safety"]["status"] == "available"


def test_build_job_readiness_items_detects_scheduler_config():
    items = build_job_readiness_items(
        {
            "toolkit": {
                "jobs": {
                    "enabled": True,
                },
            },
        }
    )

    by_name = {item["name"]: item for item in items}

    assert by_name["Scheduler Settings"]["status"] == "available"


def test_build_jobs_data_shape():
    data = build_jobs_data(_dashboard_data(), {})
    jobs_page = data["jobs_page"]

    assert data["health_status"] == "Excellent"
    assert jobs_page["status"] == "Foundation"
    assert jobs_page["status_class"] == "warn"
    assert jobs_page["planned_areas"]
    assert jobs_page["readiness_count"] == 4
    assert jobs_page["available_readiness_count"] == 1
    assert "read-only" in jobs_page["note"]
    assert "without starting" in jobs_page["note"]
    assert "scheduling tasks" in jobs_page["note"]
