"""Read-only Backup / Restore page data builders."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BackupReadinessItem:
    """A read-only readiness item for Backup / Restore planning."""

    name: str
    status: str
    detail: str


@dataclass(frozen=True)
class BackupPlannedArea:
    """A planned read-only Backup / Restore foundation area."""

    name: str
    description: str


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


def build_backup_readiness_items() -> list[BackupReadinessItem]:
    """Return read-only readiness items for Backup / Restore planning."""

    return [
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


def build_backup_page_data() -> dict[str, object]:
    """Build read-only Backup / Restore foundation page data."""

    return {
        "title": "Backup / Restore",
        "summary": (
            "Read-only planning foundation for future backup and restore workflows."
        ),
        "safety_note": SAFETY_NOTE,
        "planned_areas": build_backup_planned_areas(),
        "readiness_items": build_backup_readiness_items(),
    }
