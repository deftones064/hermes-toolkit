from toolkit.update_page import (
    SAFETY_NOTE,
    UpdatePageSummary,
    UpdatePlannedArea,
    UpdateReadinessItem,
    build_update_page_data,
    build_update_page_summary,
    build_update_planned_areas,
    build_update_readiness_items,
)


def test_update_planned_areas_cover_foundation_scope():
    areas = build_update_planned_areas()

    assert areas == [
        UpdatePlannedArea(
            name="Version Sources",
            description=(
                "Inventory candidate version sources such as package metadata, release "
                "metadata, and repository state without querying or changing them."
            ),
            status="planned",
            icon="tags",
        ),
        UpdatePlannedArea(
            name="Update Channels",
            description=(
                "Describe future stable, alpha, prerelease, or local channels without "
                "switching channels or changing installed code."
            ),
            status="planned",
            icon="radio",
        ),
        UpdatePlannedArea(
            name="Pending Changes",
            description=(
                "Plan future read-only update previews that summarize possible changes "
                "without fetching, pulling, installing, or restarting anything."
            ),
            status="planned",
            icon="list-checks",
        ),
        UpdatePlannedArea(
            name="Update Guardrails",
            description=(
                "Document safety checks required before any future update workflow can "
                "touch packages, Git state, services, processes, or configuration."
            ),
            status="required",
            icon="shield-check",
        ),
    ]


def test_update_readiness_items_are_read_only():
    items = build_update_readiness_items()

    assert items == [
        UpdateReadinessItem(
            name="Current Version Inventory",
            status="planned",
            summary="Installed version discovery",
            detail=(
                "A future read-only inventory can describe the current package and "
                "application version before any update operation exists."
            ),
            icon="badge-info",
        ),
        UpdateReadinessItem(
            name="Release Metadata Inventory",
            status="planned",
            summary="Release metadata discovery",
            detail=(
                "A future read-only inventory can describe release metadata without "
                "downloading artifacts, changing channels, or touching Git state."
            ),
            icon="tags",
        ),
        UpdateReadinessItem(
            name="Update Plan Preview",
            status="planned",
            summary="Dry-run update planning",
            detail=(
                "A future preview can explain intended update steps before any package, "
                "process, service, Git, or configuration mutation is allowed."
            ),
            icon="clipboard-list",
        ),
        UpdateReadinessItem(
            name="Action Safety",
            status="required",
            summary="Mutation guardrails",
            detail=(
                "Package install/update/remove behavior, Git mutations, process restarts, "
                "service restarts, and configuration mutation remain intentionally absent."
            ),
            icon="shield-check",
        ),
    ]


def test_update_page_summary_counts_available_readiness_items():
    items = [
        UpdateReadinessItem(
            name="Available",
            status="available",
            summary="Available summary",
            detail="Available detail",
            icon="check",
        ),
        UpdateReadinessItem(
            name="Planned",
            status="planned",
            summary="Planned summary",
            detail="Planned detail",
            icon="clock",
        ),
    ]

    assert build_update_page_summary(items) == UpdatePageSummary(
        status="Planned",
        status_class="warning",
        detail="Read-only planning surface",
        note=SAFETY_NOTE,
        readiness_count=2,
        available_readiness_count=1,
    )


def test_update_page_data_includes_safety_note_and_sections():
    data = build_update_page_data()

    assert data["title"] == "Update Manager"
    assert data["summary"] == "Read-only planning foundation for future update workflows."
    assert data["safety_note"] == SAFETY_NOTE
    assert data["update_page"] == build_update_page_summary(
        build_update_readiness_items()
    )
    assert data["planned_areas"] == build_update_planned_areas()
    assert data["readiness_items"] == build_update_readiness_items()


def test_safety_note_blocks_mutating_update_behavior():
    assert "No packages are installed." in SAFETY_NOTE
    assert "No packages are updated." in SAFETY_NOTE
    assert "No packages are removed." in SAFETY_NOTE
    assert "No Git fetch, pull, reset, checkout, merge, or tag operation is executed." in SAFETY_NOTE
    assert "No processes are restarted." in SAFETY_NOTE
    assert "No services are restarted." in SAFETY_NOTE
    assert "No configuration is modified." in SAFETY_NOTE
