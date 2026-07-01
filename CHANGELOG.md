# Changelog

All notable changes to Hermes Toolkit will be documented in this file.

---

## Unreleased

### Changed

- Extracted Doctor diagnostics into the `toolkit.doctor` backend module.
- Split Doctor diagnostics into focused helper builders for environment, configuration, runtime, connectivity, usage, summary, and recommendations.
- Added provider connectivity dispatcher so future provider checks do not clutter the Doctor page builder.
- Kept the public Doctor web data API stable through `build_doctor_data(dashboard_data, cfg)`.

### Added

- Added safe Ollama reachability diagnostics using the local `/api/tags` endpoint.
- Added config-only validation for external providers without making outbound API calls.
- Added Doctor diagnostic mode labels for static, config, live, and pending checks.
- Added read-only Logs page filtering by severity.
- Added read-only Logs page text search over recent raw log entries.
- Added Logs page tests for filter state and unknown severity fallback.
- Added Doctor backend tests for diagnostic data shape, missing-provider warnings, provider validation, and Ollama reachability behavior.

### Notes

- Ollama reachability diagnostics do not send prompts, start models, install models, restart services, or modify configuration.
- Package version remains `0.3.0-alpha` until the next release is intentionally cut.

---

## v0.3.0-alpha

### Added

- Added complete dashboard surface for the v0.3 Alpha release track.
- Added Cost page foundation with estimated token cost, cache savings, token summaries, and recent estimated calls.
- Added Models page foundation with active model summary, provider context, model presets, and safe config-only model switching.
- Added Sessions page foundation with reset behavior, live session limits, max turns, context protection, activity totals, and recent API activity proxy.
- Added Logs page foundation with log health, log path/size, parsed API calls, recent warning/error counts, and raw recent log viewer.
- Added Skills page foundation with read-only plugin/skill signal detection, planned skill areas, recommendations, and recent plugin log signals.
- Added Memory page foundation with read-only context/cache/compression overview, memory recommendations, planned memory areas, and recent memory/context log signals.
- Added About page with project identity, version information, product principles, page coverage, runtime information, and release-prep checklist.

### Changed

- Upgraded Doctor to v1.1.
- Replaced flat Doctor checks with compact grouped diagnostic rows.
- Added Doctor diagnostic categories:
  - Environment
  - Configuration
  - Runtime
  - Connectivity
  - Usage
- Added intelligent Doctor recommendations derived from diagnostic state.
- Added non-destructive Run Full Diagnostic action.
- Enabled previously disabled sidebar pages:
  - Cost
  - Models
  - Sessions
  - Logs
  - Skills
  - Memory
  - About
- Updated package version to `0.3.0-alpha`.
- Preserved the locked visual design language:
  - Dark graphite
  - Gold accent
  - Rounded cards
  - Lucide icons
  - Engineering / DevOps dashboard aesthetic

### Notes

- Cost values are estimates derived from parsed Hermes logs and an internal pricing table. They are not billing statements.
- Sessions v1 uses recent API calls as a temporary activity proxy. It is not a full session database.
- Skills v1 is log-derived and read-only. It does not install, remove, restart, or modify plugins.
- Memory v1 is config/log-derived and read-only. It does not inspect, delete, export, or modify memory stores.
- Doctor v1.1 diagnostics are non-destructive.

---

## v0.2.0

### Added

- Initial CLI management foundation.
- Basic status output.
- Configuration viewing and editing helpers.
- Profile application.
- Model switching.
- Basic Doctor checks.
- Recent API log parsing.
- Early web dashboard foundation.
