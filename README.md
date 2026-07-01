# Hermes Toolkit

> Open-source administration dashboard and CLI companion for Hermes Agent.

Hermes Toolkit is an open-source management platform for **Nous Research Hermes Agent**. It provides a unified CLI and web dashboard for monitoring, configuring, diagnosing, and optimizing a local Hermes installation.

Instead of manually editing `~/.hermes/config.yaml`, digging through log files, or remembering CLI commands, Hermes Toolkit gives Hermes operators a clean control surface for day-to-day administration.

---

## Current Version

**v0.4.0-alpha**

Hermes Toolkit v0.4 Alpha builds on the dashboard foundation with extracted page backends, safer provider diagnostics, configurable estimated pricing, and stronger tests.

This release includes:

- Dark/light theme with Auto/System mode
- Persistent theme selection
- Responsive sidebar with independent scrolling
- Hermes branding and logo
- Lucide icon system
- Dashboard
- Analytics
- Cost foundation
- Doctor v1.1
- Configuration editor
- Models foundation
- Sessions foundation
- Logs foundation
- Skills foundation
- Memory foundation
- About page
- Systemd web service
- Install script
- Static assets and CSS architecture

The visual design language is locked for this release track:

- Dark graphite
- Gold accent
- White/light mode equivalent
- Rounded cards
- Engineering / DevOps aesthetic
- Enterprise dashboard feel

---

## Dashboard Pages

### Dashboard

Core operations overview with provider, active model, health score, token usage, cache status, configuration summary, and recent API activity.

### Analytics

Charts and usage visibility for parsed Hermes API activity.

### Cost

Estimated token cost, cache savings, and recent call cost context.

Cost values are estimates derived from recent Hermes logs and an internal pricing table. They are not billing statements.

### Doctor

Doctor v1.1 provides grouped, compact diagnostics across:

- Environment
- Configuration
- Runtime
- Connectivity
- Usage

Doctor also includes intelligent recommendations and a non-destructive **Run Full Diagnostic** action.

### Configuration

Web-based configuration editor for profiles, model selection, conversation limits, performance settings, file limits, compression, and session reset behavior.

### Models

Known-good model presets and safe config-only model switching.

Current presets:

- GPT-5.5 via OpenAI Codex
- Gemini 2.5 Pro via OpenRouter
- Qwen Coder via OpenRouter

### Sessions

Read-only session foundation showing reset behavior, live session limits, max turns, context protection, activity totals, and recent API activity as a temporary session proxy.

### Logs

Read-only log viewer with log health, parsed API calls, warning/error counts, and raw recent log entries.

### Skills

Read-only foundation for Hermes skills, plugins, tools, and adapters.

Skills v1 is log-derived and does not install, remove, restart, or modify plugins.

### Memory

Read-only memory, context, cache, and compression overview.

Memory v1 is config/log-derived and does not inspect, delete, export, or modify memory stores.

### About

Project identity, version, release status, product principles, page coverage, runtime information, and release-prep checklist.

---

## Screenshots

Screenshots are planned as follow-up documentation for the v0.4 Alpha release.

Screenshot assets should live under:

    docs/assets/screenshots/

Recommended screenshots for this release:

- Dashboard
- Doctor
- Cost
- Models
- Sessions
- Logs
- Skills
- Memory
- About

See:

    docs/assets/screenshots/README.md

---

## Installation

Clone the repository:

```bash
git clone https://github.com/deftones064/hermes-toolkit.git
cd hermes-toolkit
```

Install:

```bash
chmod +x install.sh
sudo ./install.sh
```

The installer copies the toolkit to:

```text
/usr/local/lib/hermes-toolkit
```

It also installs the `hermes-toolkit` command and enables the web dashboard service when systemd is available.

Default dashboard URL:

```text
http://<host-ip>:8088
```

---

## CLI Usage

View current status:

```bash
hermes-toolkit status
```

Configuration overview:

```bash
hermes-toolkit show
```

Health check:

```bash
hermes-toolkit doctor
```

View recent API activity:

```bash
hermes-toolkit logs
```

Switch profiles:

```bash
hermes-toolkit profile low-cost
hermes-toolkit profile balanced
hermes-toolkit profile premium
```

Switch models:

```bash
hermes-toolkit model gpt
hermes-toolkit model gemini
hermes-toolkit model qwen
```

Modify a configuration value:

```bash
hermes-toolkit set agent.max_turns 30
```

Show version:

```bash
hermes-toolkit --version
```

---

## Web Dashboard

Launch manually:

```bash
hermes-toolkit web --host 0.0.0.0 --port 8088
```

When installed with `install.sh`, the dashboard runs as:

```text
hermes-toolkit-web.service
```

Useful service commands:

```bash
systemctl status hermes-toolkit-web --no-pager
systemctl restart hermes-toolkit-web
journalctl -u hermes-toolkit-web -n 100 --no-pager
```

---

## Safety Model

Hermes Toolkit v0.4 Alpha is conservative by design.

Read-only or non-destructive pages:

- Doctor diagnostics
- Cost estimates
- Sessions
- Logs
- Skills
- Memory
- About

Configuration-changing actions are explicit and limited to:

- Configuration editor saves
- Profile application
- Model preset application
- CLI configuration commands

Hermes Toolkit does not silently restart Hermes Agent, delete logs, remove memories, install plugins, or mutate runtime state from observational pages.

---

## Roadmap

Current release track:

- [x] Doctor
- [x] Cost
- [x] Models
- [x] Sessions
- [x] Logs
- [x] Skills
- [x] Memory
- [x] About

v0.4 Alpha completed:

- [x] Extract Doctor diagnostics into backend module
- [x] Split Doctor diagnostics into helper builders
- [x] Add safe Ollama reachability diagnostics
- [x] Add provider connectivity dispatcher
- [x] Add config-only provider validation
- [x] Add Doctor diagnostic mode labels
- [x] Add broader live provider connectivity checks
- [x] Extract Sessions data builder
- [x] Add Sessions activity filtering
- [x] Add Sessions provider activity summary foundation
- [x] Extract Cost data builder
- [x] Add configurable estimated pricing
- [x] Extract Models page data builder
- [x] Add session browser foundation
- [x] Add log filtering/search
- [x] Add log export
- [x] Extract Logs page data builder
- [x] Extract Skills page data builder
- [x] Add formal skill registry foundation
- [x] Extract Memory page data builder
- [x] Extract About page data builder
- [x] Extract shared Dashboard data builder
- [x] Complete v0.4 page-builder architecture pass
- [x] Add memory inventory foundation
- [x] Add Jobs / Tasks page foundation
- [x] Add Home Assistant integration foundation
- [x] Add Telegram integration foundation
- [x] Add Backup / Restore read-only foundation
- [x] Add Update Manager read-only foundation
- [x] Add System Inventory read-only foundation
- [ ] Add backup and restore
- [ ] Add update manager

### Backup / Restore foundation

The Backup / Restore page is currently a read-only planning surface. It inventories planned areas for backup sources, backup destinations, restore points, and restore guardrails.

Its backend follows the shared foundation-page readiness shape used by the other read-only integration pages, including summary status, readiness counts, item summaries, statuses, and icons.

This foundation is intentionally non-mutating:

- No backups are created.
- No restores are executed.
- No files are deleted.
- No files are overwritten.
- No services are restarted.
- No configuration is modified.

The full backup and restore roadmap item remains open until explicit backup creation and restore workflows are intentionally designed, guarded, tested, and documented.

### Update Manager foundation

The Updates page is currently a read-only planning surface. It inventories planned areas for version sources, update channels, pending changes, and update guardrails.

Its backend follows the shared foundation-page readiness shape used by the other read-only integration pages, including summary status, readiness counts, item summaries, statuses, and icons.

This foundation is intentionally non-mutating:

- No packages are installed.
- No packages are updated.
- No packages are removed.
- No Git fetch, pull, reset, checkout, merge, or tag operation is executed.
- No processes are restarted.
- No services are restarted.
- No configuration is modified.

The full update manager roadmap item remains open until explicit update workflows are intentionally designed, guarded, tested, and documented.

### System Inventory foundation

The System page is currently a read-only planning surface. It inventories planned areas for runtime inventory, repository inventory, configuration inventory, service inventory, and action guardrails.

Its backend follows the shared foundation-page readiness shape used by the other read-only integration pages, including summary status, readiness counts, item summaries, statuses, and icons.

The System page also displays in-process runtime facts for Python version, platform, system, machine architecture, and Hermes Toolkit package version without executing subprocess commands or external probes.

This foundation is intentionally non-mutating:

- No subprocess commands are executed.
- No service state is queried.
- No processes are restarted.
- No files are deleted.
- No files are overwritten.
- No packages are installed, updated, or removed.
- No Git operations are executed.
- No configuration is modified.

The System Inventory foundation is intended to support future Backup / Restore and Update Manager workflows without jumping directly into mutating behavior.

### Optional estimated pricing overrides

The Cost page uses a built-in estimate table by default. You can override estimated pricing under the `toolkit` namespace without changing provider/model configuration.

Example:

```yaml
toolkit:
  estimated_pricing:
    gpt-5.5:
      label: GPT-5.5 Custom
      input_per_million: 1.50
      output_per_million: 12.00
      cached_input_per_million: 0.15
```

Cost values are estimates from recent Hermes API log entries and are not billing statements.


---

## Project Goals

Hermes Toolkit aims to become the primary administration utility for Hermes Agent by providing:

- Beautiful CLI output
- Rich web interface
- Easy configuration management
- Usage analytics
- Cost optimization
- Health monitoring
- Safe diagnostics
- Operational visibility
- Automation tools

---

## License

MIT

---

## Contributing

Issues, ideas, and pull requests are welcome.

This project is currently in active alpha development.
