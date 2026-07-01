# Changelog

All notable changes to Hermes Toolkit will be documented in this file.

---

## Unreleased

### Added

- Added Sessions provider activity summaries as a backend foundation for the future full session browser.
- Added a read-only Sessions provider activity summary table using the existing dashboard table style.


## v0.4.0-alpha

### Changed

- Extracted Doctor diagnostics into the `toolkit.doctor` backend module.
- Split Doctor diagnostics into focused helper builders for environment, configuration, runtime, connectivity, usage, summary, and recommendations.
- Added provider connectivity dispatcher so future provider checks do not clutter the Doctor page builder.
- Extracted Sessions page data building into the `toolkit.sessions` backend module.
- Extracted Cost page estimation logic into the `toolkit.cost` backend module.
- Extracted Models page display logic into the `toolkit.models_page` backend module.
- Extracted Logs page filtering, search, status, and export logic into the `toolkit.logs_page` backend module.
- Extracted Skills page log-signal and read-only inventory logic into the `toolkit.skills_page` backend module.
- Extracted Memory page context, cache, recommendation, and log-signal logic into the `toolkit.memory_page` backend module.
- Extracted About page informational release/status logic into the `toolkit.about_page` backend module.
- Completed the v0.4 page-builder architecture pass so `web.py` is primarily route wrappers plus shared dashboard context.
- Cleaned `web.py` import layout after backend extraction work.
- Kept the public Doctor web data API stable through `build_doctor_data(dashboard_data, cfg)`.
- Added a Sessions backend API through `build_sessions_data(dashboard_data, cfg, calls)`.
- Added a Cost backend API through `build_cost_data(dashboard_data, recent_calls)`.
- Added a Models page backend API through `build_models_page_data(dashboard_data)`.
- Added Logs backend APIs through `build_logs_data(dashboard_data, log_path, calls, severity, query)` and `build_logs_export_text(logs_data)`.
- Added a Skills page backend API through `build_skills_data(dashboard_data, log_path)`.
- Added a Memory page backend API through `build_memory_data(dashboard_data, calls, log_path)`.
- Added an About page backend API through `build_about_data(dashboard_data)`.

### Added

- Added safe Ollama reachability diagnostics using the local `/api/tags` endpoint.
- Added config-only validation for external providers without making outbound API calls.
- Added Doctor diagnostic mode labels for static, config, live, and pending checks.
- Added read-only Logs page filtering by severity.
- Added read-only Logs page text search over recent raw log entries.
- Added read-only Logs export route for currently filtered raw log entries.
- Added read-only Sessions activity filtering by provider.
- Added read-only Sessions activity search over provider and model names.
- Added optional `toolkit.estimated_pricing` config overrides for Cost estimates.
- Added Cost page pricing-source display so built-in estimates and config overrides are visible.
- Added safe OpenRouter provider reachability checks through the public models endpoint.
- Clarified Doctor Network Diagnostics status now that provider-specific live checks exist.
- Kept external provider diagnostics non-destructive by avoiding prompts, model launches, and token-spending inference calls.
- Added Logs page tests for filter state, unknown severity fallback, and plain-text export.
- Added Sessions backend tests for data shape, tuning recommendations, provider filtering, query filtering, and unknown provider fallback.
- Added Doctor backend tests for diagnostic data shape, missing-provider warnings, provider validation, and Ollama reachability behavior.

### Notes

- Ollama reachability diagnostics do not send prompts, start models, install models, restart services, or modify configuration.
- Package version updated to `0.4.0-alpha`.

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
