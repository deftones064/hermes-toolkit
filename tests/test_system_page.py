from pathlib import Path
import platform
from toolkit import __version__
from toolkit.config import CONFIG, LOG
from toolkit.release_status import build_release_status_data
from toolkit.system_page import (
    SAFETY_NOTE,
    SystemConfigFact,
    SystemGuardrailFact,
    SystemPageSummary,
    SystemPlannedArea,
    SystemReadinessItem,
    SystemRepositoryFact,
    SystemRuntimeFact,
    SystemServiceFact,
    build_system_config_facts,
    build_system_guardrail_facts,
    build_system_page_data,
    build_system_page_summary,
    build_system_planned_areas,
    build_system_readiness_items,
    build_system_repository_facts,
    build_system_runtime_facts,
    build_system_service_facts,
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







def test_system_guardrail_facts_are_static_enforced_boundaries():
    facts = build_system_guardrail_facts()

    assert facts == [
        SystemGuardrailFact(
            name="Read-only Mode",
            value="enforced",
            summary="System Inventory is a read-only planning surface in this foundation slice.",
            status="ready",
            icon="shield-check",
        ),
        SystemGuardrailFact(
            name="No Subprocess Execution",
            value="enforced",
            summary="System Inventory does not execute shell commands or spawn subprocesses.",
            status="ready",
            icon="terminal-x",
        ),
        SystemGuardrailFact(
            name="No Service Mutation",
            value="enforced",
            summary="System Inventory does not start, stop, restart, enable, disable, or reload services.",
            status="ready",
            icon="shield-x",
        ),
        SystemGuardrailFact(
            name="No Config Mutation",
            value="enforced",
            summary="System Inventory does not load, save, overwrite, or modify configuration files.",
            status="ready",
            icon="file-lock-2",
        ),
    ]


def test_system_service_facts_are_static_placeholders():
    facts = build_system_service_facts()

    assert facts == [
        SystemServiceFact(
            name="Web App Process",
            value="planned",
            summary="Web application process inventory is planned but no process list is queried.",
            status="planned",
            icon="panel-top",
        ),
        SystemServiceFact(
            name="Scheduler / Future Worker",
            value="planned",
            summary="Scheduler or worker inventory is planned but no service manager is queried.",
            status="planned",
            icon="calendar-clock",
        ),
        SystemServiceFact(
            name="Local Model Runtime",
            value="planned",
            summary="Local model runtime inventory is planned but no runtime endpoint is probed.",
            status="planned",
            icon="brain-circuit",
        ),
        SystemServiceFact(
            name="Notification Channel",
            value="planned",
            summary="Notification channel inventory is planned but no delivery channel is contacted.",
            status="planned",
            icon="send",
        ),
    ]


def test_system_repository_facts_are_static_placeholders():
    facts = build_system_repository_facts()

    assert facts == [
        SystemRepositoryFact(
            name="Repository Path",
            value="planned",
            summary="Repository path inventory is planned but not queried by this foundation slice.",
            status="planned",
            icon="folder-git-2",
        ),
        SystemRepositoryFact(
            name="Branch",
            value="planned",
            summary="Git branch inventory is planned but no Git command is executed.",
            status="planned",
            icon="git-branch",
        ),
        SystemRepositoryFact(
            name="Commit",
            value="planned",
            summary="Git commit inventory is planned but no repository metadata is read.",
            status="planned",
            icon="git-commit",
        ),
        SystemRepositoryFact(
            name="Dirty State",
            value="planned",
            summary="Working tree status inventory is planned but not evaluated.",
            status="planned",
            icon="git-compare",
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
    assert data["repository_facts"] == build_system_repository_facts()
    assert data["service_facts"] == build_system_service_facts()
    assert data["guardrail_facts"] == build_system_guardrail_facts()
    assert data["release_status"] == build_release_status_data()


def test_system_page_release_status_keeps_no_probe_guardrails():
    data = build_system_page_data()
    release_status = data["release_status"]

    assert release_status["repository_branch"] == "Not probed"
    assert release_status["repository_commit"] == "Not probed"
    assert release_status["repository_dirty_state"] == "Not probed"
    assert release_status["service_state"] == "Not probed"

    guardrails = release_status["guardrails"]
    assert guardrails["git_probing"] == "Disabled"
    assert guardrails["subprocess_execution"] == "Disabled"
    assert guardrails["service_mutation"] == "Disabled"
    assert guardrails["tag_mutation"] == "Disabled"
    assert guardrails["config_mutation"] == "Disabled"


def test_system_template_includes_release_status_section():
    template = Path("toolkit/templates/system.html").read_text()

    assert "Release Status" in template
    assert "Package Version" in template
    assert "Release Artifact" in template
    assert "Repository State" in template
    assert "Service State" in template
    assert "Git probing disabled" in template
    assert "Service mutation disabled" in template


def test_safety_note_blocks_mutating_system_behavior():
    assert "No subprocess commands are executed." in SAFETY_NOTE
    assert "No service state is queried." in SAFETY_NOTE
    assert "No processes are restarted." in SAFETY_NOTE
    assert "No files are deleted." in SAFETY_NOTE
    assert "No files are overwritten." in SAFETY_NOTE
    assert "No packages are installed, updated, or removed." in SAFETY_NOTE
    assert "No Git operations are executed." in SAFETY_NOTE
    assert "No configuration is modified." in SAFETY_NOTE
