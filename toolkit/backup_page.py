"""Read-only Backup / Restore page data builders."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BackupReadinessItem:
    """A read-only readiness item for Backup / Restore planning."""

    name: str
    status: str
    summary: str
    detail: str
    icon: str


@dataclass(frozen=True)
class BackupPlannedArea:
    """A planned read-only Backup / Restore foundation area."""

    name: str
    description: str
    status: str
    icon: str


@dataclass(frozen=True)
class BackupPageSummary:
    """Summary state for the read-only Backup / Restore foundation page."""

    status: str
    status_class: str
    detail: str
    note: str
    readiness_count: int
    available_readiness_count: int


SAFETY_NOTE = (
    "Read-only foundation only. No backups are created. No restores are executed. "
    "No files are deleted. No files are overwritten. No services are restarted. "
    "No configuration is modified."
)


def build_backup_planned_areas() -> list[BackupPlannedArea]:
    """Return the planned read-only Backup / Restore areas."""

    return [
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


def build_backup_readiness_items() -> list[BackupReadinessItem]:
    """Return read-only readiness items for Backup / Restore planning."""

    return [
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


def build_backup_page_summary(
    readiness_items: list[BackupReadinessItem],
) -> BackupPageSummary:
    """Return summary state for the read-only Backup / Restore foundation page."""

    available_count = sum(1 for item in readiness_items if item.status == "available")

    return BackupPageSummary(
        status="Planned",
        status_class="warning",
        detail="Read-only planning surface",
        note=SAFETY_NOTE,
        readiness_count=len(readiness_items),
        available_readiness_count=available_count,
    )


def build_backup_page_data() -> dict[str, object]:
    """Build read-only Backup / Restore foundation page data."""

    readiness_items = build_backup_readiness_items()
    planned_areas = build_backup_planned_areas()

    return {
        "title": "Backup / Restore",
        "summary": (
            "Read-only planning foundation for future backup and restore workflows."
        ),
        "safety_note": SAFETY_NOTE,
        "backup_page": build_backup_page_summary(readiness_items),
        "planned_areas": planned_areas,
        "readiness_items": readiness_items,
    }
