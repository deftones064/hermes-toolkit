from toolkit.backup_page import (
    SAFETY_NOTE,
    BackupPageSummary,
    BackupPlannedArea,
    BackupReadinessItem,
    build_backup_page_data,
    build_backup_page_summary,
    build_backup_planned_areas,
    build_backup_readiness_items,
)


def test_backup_planned_areas_cover_foundation_scope():
    areas = build_backup_planned_areas()

    assert areas == [
        BackupPlannedArea(
            name="Backup Sources",
            description=(
                "Inventory candidate configuration, state, and project paths that may "
                "eventually be eligible for backup planning."
            ),
            status="planned",
            icon="folder-search",
        ),
        BackupPlannedArea(
            name="Backup Destinations",
            description=(
                "Inventory candidate local or remote backup targets without writing, "
                "creating, deleting, or validating backup payloads."
            ),
            status="planned",
            icon="hard-drive",
        ),
        BackupPlannedArea(
            name="Restore Points",
            description=(
                "Inventory future restore point metadata concepts without reading backup "
                "archives or preparing restore execution."
            ),
            status="planned",
            icon="history",
        ),
        BackupPlannedArea(
            name="Restore Guardrails",
            description=(
                "Document safety checks that must exist before any future restore workflow "
                "can modify files, services, or configuration."
            ),
            status="required",
            icon="shield-check",
        ),
    ]


def test_backup_readiness_items_are_read_only():
    items = build_backup_readiness_items()

    assert items == [
        BackupReadinessItem(
            name="Source Inventory",
            status="planned",
            summary="Backup source discovery",
            detail=(
                "A future read-only inventory can describe candidate backup sources before "
                "any backup operation exists."
            ),
            icon="folder-search",
        ),
        BackupReadinessItem(
            name="Destination Inventory",
            status="planned",
            summary="Backup destination discovery",
            detail=(
                "A future read-only inventory can describe candidate destinations without "
                "creating folders, writing files, or checking credentials."
            ),
            icon="hard-drive",
        ),
        BackupReadinessItem(
            name="Restore Point Inventory",
            status="planned",
            summary="Restore metadata discovery",
            detail=(
                "A future read-only inventory can describe restore point metadata without "
                "opening archives or staging restore actions."
            ),
            icon="history",
        ),
        BackupReadinessItem(
            name="Action Safety",
            status="required",
            summary="Mutation guardrails",
            detail=(
                "Backup creation, restore execution, deletion, overwrite behavior, service "
                "restarts, and configuration mutation remain intentionally absent."
            ),
            icon="shield-check",
        ),
    ]


def test_backup_page_summary_counts_available_readiness_items():
    items = [
        BackupReadinessItem(
            name="Available",
            status="available",
            summary="Available summary",
            detail="Available detail",
            icon="check",
        ),
        BackupReadinessItem(
            name="Planned",
            status="planned",
            summary="Planned summary",
            detail="Planned detail",
            icon="clock",
        ),
    ]

    assert build_backup_page_summary(items) == BackupPageSummary(
        status="Planned",
        status_class="warning",
        detail="Read-only planning surface",
        note=SAFETY_NOTE,
        readiness_count=2,
        available_readiness_count=1,
    )


def test_backup_page_data_includes_safety_note_and_sections():
    data = build_backup_page_data()

    assert data["title"] == "Backup / Restore"
    assert data["summary"] == (
        "Read-only planning foundation for future backup and restore workflows."
    )
    assert data["safety_note"] == SAFETY_NOTE
    assert data["backup_page"] == build_backup_page_summary(
        build_backup_readiness_items()
    )
    assert data["planned_areas"] == build_backup_planned_areas()
    assert data["readiness_items"] == build_backup_readiness_items()


def test_safety_note_blocks_mutating_backup_restore_behavior():
    assert "No backups are created." in SAFETY_NOTE
    assert "No restores are executed." in SAFETY_NOTE
    assert "No files are deleted." in SAFETY_NOTE
    assert "No files are overwritten." in SAFETY_NOTE
    assert "No services are restarted." in SAFETY_NOTE
    assert "No configuration is modified." in SAFETY_NOTE
