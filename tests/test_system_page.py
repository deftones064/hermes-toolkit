import platform
from toolkit import __version__
from toolkit.config import CONFIG, LOG
from toolkit.system_page import (
    SAFETY_NOTE,
    SystemConfigFact,
    SystemPageSummary,
    SystemPlannedArea,
    SystemReadinessItem,
    SystemRuntimeFact,
    build_system_config_facts,
    build_system_page_data,
    build_system_page_summary,
    build_system_planned_areas,
    build_system_readiness_items,
    build_system_runtime_facts,
)


def test_system_planned_areas_cover_foundation_scope():
    areas = build_system_planned_areas()

    assert areas == [
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


def test_system_readiness_items_are_read_only():
    items = build_system_readiness_items()

    assert items == [
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




def test_system_config_facts_are_module_constant_metadata():
    facts = build_system_config_facts()

    assert facts == [
        SystemConfigFact(
            name="Config Path",
            value=str(CONFIG),
            summary="Configured Hermes Toolkit config path from module constants.",
            icon="file-cog",
        ),
        SystemConfigFact(
            name="Log Path",
            value=str(LOG),
            summary="Configured Hermes Toolkit log path from module constants.",
            icon="scroll-text",
        ),
    ]


def test_system_runtime_facts_are_in_process_metadata():
    facts = build_system_runtime_facts()

    assert facts == [
        SystemRuntimeFact(
            name="Python Version",
            value=platform.python_version(),
            summary="Runtime Python version reported by the current process.",
            icon="code-2",
        ),
        SystemRuntimeFact(
            name="Platform",
            value=platform.platform(),
            summary="Platform string reported by the current process.",
            icon="monitor-cog",
        ),
        SystemRuntimeFact(
            name="System",
            value=platform.system(),
            summary="Operating system family reported by the current process.",
            icon="server",
        ),
        SystemRuntimeFact(
            name="Machine",
            value=platform.machine(),
            summary="Machine architecture reported by the current process.",
            icon="cpu",
        ),
        SystemRuntimeFact(
            name="Package Version",
            value=__version__,
            summary="Hermes Toolkit package version imported in-process.",
            icon="badge-info",
        ),
    ]


def test_system_page_summary_counts_available_readiness_items():
    items = [
        SystemReadinessItem(
            name="Available",
            status="available",
            summary="Available summary",
            detail="Available detail",
            icon="check",
        ),
        SystemReadinessItem(
            name="Planned",
            status="planned",
            summary="Planned summary",
            detail="Planned detail",
            icon="clock",
        ),
    ]

    assert build_system_page_summary(items) == SystemPageSummary(
        status="Foundation",
        status_class="warning",
        detail="Read-only inventory planning",
        note=SAFETY_NOTE,
        readiness_count=2,
        available_readiness_count=1,
    )


def test_system_page_data_includes_safety_note_and_sections():
    data = build_system_page_data()

    assert data["title"] == "System Inventory"
    assert data["summary"] == (
        "Read-only planning foundation for future runtime, repository, "
        "configuration, and service inventory."
    )
    assert data["safety_note"] == SAFETY_NOTE
    assert data["system_page"] == build_system_page_summary(
        build_system_readiness_items()
    )
    assert data["planned_areas"] == build_system_planned_areas()
    assert data["readiness_items"] == build_system_readiness_items()
    assert data["runtime_facts"] == build_system_runtime_facts()
    assert data["config_facts"] == build_system_config_facts()


def test_safety_note_blocks_mutating_system_behavior():
    assert "No subprocess commands are executed." in SAFETY_NOTE
    assert "No service state is queried." in SAFETY_NOTE
    assert "No processes are restarted." in SAFETY_NOTE
    assert "No files are deleted." in SAFETY_NOTE
    assert "No files are overwritten." in SAFETY_NOTE
    assert "No packages are installed, updated, or removed." in SAFETY_NOTE
    assert "No Git operations are executed." in SAFETY_NOTE
    assert "No configuration is modified." in SAFETY_NOTE
