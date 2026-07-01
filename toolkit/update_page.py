"""Read-only Update Manager page data builders."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UpdateReadinessItem:
    """A read-only readiness item for Update Manager planning."""

    name: str
    status: str
    summary: str
    detail: str
    icon: str


@dataclass(frozen=True)
class UpdatePlannedArea:
    """A planned read-only Update Manager foundation area."""

    name: str
    description: str
    status: str
    icon: str


@dataclass(frozen=True)
class UpdatePageSummary:
    """Summary state for the read-only Update Manager foundation page."""

    status: str
    status_class: str
    detail: str
    note: str
    readiness_count: int
    available_readiness_count: int


SAFETY_NOTE = (
    "Read-only foundation only. No packages are installed. No packages are updated. "
    "No packages are removed. No Git fetch, pull, reset, checkout, merge, or tag "
    "operation is executed. No processes are restarted. No services are restarted. "
    "No configuration is modified."
)


def build_update_planned_areas() -> list[UpdatePlannedArea]:
    """Return the planned read-only Update Manager areas."""

    return [
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


def build_update_readiness_items() -> list[UpdateReadinessItem]:
    """Return read-only readiness items for Update Manager planning."""

    return [
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


def build_update_page_summary(
    readiness_items: list[UpdateReadinessItem],
) -> UpdatePageSummary:
    """Return summary state for the read-only Update Manager foundation page."""

    available_count = sum(1 for item in readiness_items if item.status == "available")

    return UpdatePageSummary(
        status="Planned",
        status_class="warning",
        detail="Read-only planning surface",
        note=SAFETY_NOTE,
        readiness_count=len(readiness_items),
        available_readiness_count=available_count,
    )


def build_update_page_data() -> dict[str, object]:
    """Build read-only Update Manager foundation page data."""

    readiness_items = build_update_readiness_items()
    planned_areas = build_update_planned_areas()

    return {
        "title": "Update Manager",
        "summary": "Read-only planning foundation for future update workflows.",
        "safety_note": SAFETY_NOTE,
        "update_page": build_update_page_summary(readiness_items),
        "planned_areas": planned_areas,
        "readiness_items": readiness_items,
    }
