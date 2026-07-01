"""Read-only System Inventory page data builders."""

from __future__ import annotations

from dataclasses import dataclass

from toolkit import __version__


@dataclass(frozen=True)
class SystemReadinessItem:
    """A read-only readiness item for System Inventory planning."""

    name: str
    status: str
    summary: str
    detail: str
    icon: str


@dataclass(frozen=True)
class SystemPlannedArea:
    """A planned read-only System Inventory foundation area."""

    name: str
    description: str
    status: str
    icon: str


@dataclass(frozen=True)
class SystemPageSummary:
    """Summary state for the read-only System Inventory foundation page."""

    status: str
    status_class: str
    detail: str
    note: str
    readiness_count: int
    available_readiness_count: int


SAFETY_NOTE = (
    "Read-only foundation only. No subprocess commands are executed. "
    "No service state is queried. No processes are restarted. No files are deleted. "
    "No files are overwritten. No packages are installed, updated, or removed. "
    "No Git operations are executed. No configuration is modified."
)


def build_system_planned_areas() -> list[SystemPlannedArea]:
    """Return the planned read-only System Inventory areas."""

    return [
        SystemPlannedArea(
            name="Runtime Inventory",
            description=(
                "Describe Python and application runtime facts that are already available "
                "inside the process without executing external commands."
            ),
            status="planned",
            icon="terminal-square",
        ),
        SystemPlannedArea(
            name="Repository Inventory",
            description=(
                "Plan future read-only repository awareness without running Git fetch, "
                "pull, reset, checkout, merge, tag, or status commands."
            ),
            status="planned",
            icon="git-branch",
        ),
        SystemPlannedArea(
            name="Configuration Inventory",
            description=(
                "Describe configuration path awareness and safe metadata without writing "
                "or mutating configuration files."
            ),
            status="planned",
            icon="settings",
        ),
        SystemPlannedArea(
            name="Service Inventory",
            description=(
                "Plan future service visibility without querying service managers, "
                "starting services, stopping services, or restarting processes."
            ),
            status="planned",
            icon="server-cog",
        ),
        SystemPlannedArea(
            name="Action Guardrails",
            description=(
                "Document safety checks required before future system, backup, restore, "
                "or update workflows can perform any mutation."
            ),
            status="required",
            icon="shield-check",
        ),
    ]


def build_system_readiness_items() -> list[SystemReadinessItem]:
    """Return read-only readiness items for System Inventory planning."""

    return [
        SystemReadinessItem(
            name="Python Runtime",
            status="available",
            summary="In-process runtime awareness",
            detail=(
                "Python runtime metadata can be gathered from the running process without "
                "shelling out or changing system state."
            ),
            icon="code-2",
        ),
        SystemReadinessItem(
            name="Package Version",
            status="available",
            summary="Application version awareness",
            detail=(
                f"Hermes Toolkit exposes the package version in-process as {__version__}."
            ),
            icon="badge-info",
        ),
        SystemReadinessItem(
            name="Git State",
            status="planned",
            summary="Repository state awareness",
            detail=(
                "Future repository awareness must remain read-only and avoid fetch, pull, "
                "reset, checkout, merge, tag, or other Git mutation operations."
            ),
            icon="git-branch",
        ),
        SystemReadinessItem(
            name="Config Path Awareness",
            status="planned",
            summary="Configuration metadata awareness",
            detail=(
                "Future configuration inventory can describe paths and presence without "
                "writing, deleting, overwriting, or saving configuration."
            ),
            icon="file-cog",
        ),
        SystemReadinessItem(
            name="Action Safety",
            status="required",
            summary="Mutation guardrails",
            detail=(
                "Subprocess execution, service queries, process restarts, package changes, "
                "Git operations, file mutation, and configuration mutation remain absent."
            ),
            icon="shield-check",
        ),
    ]


def build_system_page_summary(
    readiness_items: list[SystemReadinessItem],
) -> SystemPageSummary:
    """Return summary state for the read-only System Inventory foundation page."""

    available_count = sum(1 for item in readiness_items if item.status == "available")

    return SystemPageSummary(
        status="Foundation",
        status_class="warning",
        detail="Read-only inventory planning",
        note=SAFETY_NOTE,
        readiness_count=len(readiness_items),
        available_readiness_count=available_count,
    )


def build_system_page_data() -> dict[str, object]:
    """Build read-only System Inventory foundation page data."""

    readiness_items = build_system_readiness_items()
    planned_areas = build_system_planned_areas()

    return {
        "title": "System Inventory",
        "summary": (
            "Read-only planning foundation for future runtime, repository, "
            "configuration, and service inventory."
        ),
        "safety_note": SAFETY_NOTE,
        "system_page": build_system_page_summary(readiness_items),
        "planned_areas": planned_areas,
        "readiness_items": readiness_items,
    }
