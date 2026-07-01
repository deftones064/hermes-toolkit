from toolkit.backup_page import (
    SAFETY_NOTE,
    BackupPlannedArea,
    BackupReadinessItem,
    build_backup_page_data,
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
        ),
        BackupPlannedArea(
            name="Backup Destinations",
            description=(
                "Inventory candidate local or remote backup targets without writing, "
                "creating, deleting, or validating backup payloads."
            ),
        ),
        BackupPlannedArea(
            name="Restore Points",
            description=(
                "Inventory future restore point metadata concepts without reading backup "
                "archives or preparing restore execution."
            ),
        ),
        BackupPlannedArea(
            name="Restore Guardrails",
            description=(
                "Document safety checks that must exist before any future restore workflow "
                "can modify files, services, or configuration."
            ),
        ),
    ]


def test_backup_readiness_items_are_read_only():
    items = build_backup_readiness_items()

    assert items == [
        BackupReadinessItem(
            name="Source Inventory",
            status="planned",
            detail=(
                "A future read-only inventory can describe candidate backup sources before "
                "any backup operation exists."
            ),
        ),
        BackupReadinessItem(
            name="Destination Inventory",
            status="planned",
            detail=(
                "A future read-only inventory can describe candidate destinations without "
                "creating folders, writing files, or checking credentials."
            ),
        ),
        BackupReadinessItem(
            name="Restore Point Inventory",
            status="planned",
            detail=(
                "A future read-only inventory can describe restore point metadata without "
                "opening archives or staging restore actions."
            ),
        ),
        BackupReadinessItem(
            name="Action Safety",
            status="required",
            detail=(
                "Backup creation, restore execution, deletion, overwrite behavior, service "
                "restarts, and configuration mutation remain intentionally absent."
            ),
        ),
    ]


def test_backup_page_data_includes_safety_note_and_sections():
    data = build_backup_page_data()

    assert data["title"] == "Backup / Restore"
    assert data["summary"] == (
        "Read-only planning foundation for future backup and restore workflows."
    )
    assert data["safety_note"] == SAFETY_NOTE
    assert data["planned_areas"] == build_backup_planned_areas()
    assert data["readiness_items"] == build_backup_readiness_items()


def test_safety_note_blocks_mutating_backup_restore_behavior():
    assert "No backups are created." in SAFETY_NOTE
    assert "No restores are executed." in SAFETY_NOTE
    assert "No files are deleted." in SAFETY_NOTE
    assert "No files are overwritten." in SAFETY_NOTE
    assert "No services are restarted." in SAFETY_NOTE
    assert "No configuration is modified." in SAFETY_NOTE
