# Hermes Toolkit Roadmap

## Current: v0.3 Alpha

- CLI settings manager
- Profiles
- Model switching
- Doctor checks
- Status output
- Web dashboard
- Analytics page
- Logo/branding
- Systemd web service

## Priority: Configuration Page

Goal: allow settings changes from the web UI without editing YAML.

Planned:
- View current provider/model
- Switch model/profile
- Edit max turns
- Edit max live sessions
- Edit file/context limits
- Edit session reset settings
- Save changes with automatic backup
- Show restart/reload notice when needed

## Observability

- Token history graphs
- Cache history
- Prompt size trend
- Request latency
- Session length
- Provider/model usage
- Largest prompts
- Compression events

## Cost Analytics

- Today/week/month spend
- Cost by model
- Cost by provider
- OpenRouter cost estimates
- Budget warnings

## Doctor Page

- Health score
- Recommendations
- Config warnings
- Prompt/cache/session checks

## Live Activity

- Live API request feed
- WebSocket updates
- Recent latency
- Recent token usage

## Sessions

- Session viewer
- Current active session
- Message count
- Token estimate
- Session cleanup/reset tools

## Logs

- Web log viewer
- Filtering
- Search
- Download/export

## Skills

- Installed skills list
- Skill docs
- Enable/disable future support

## Memory

- USER.md viewer
- MEMORY.md viewer
- SOUL.md viewer
- Safe edit support

## Branding / UI

- Sidebar navigation
- Logo
- Health cards
- Progress bars
- Provider display names
- Better settings formatting
- Shared layout/templates

## Architecture

- Shared service layer
- Routes split into modules
- Shared UI components
- Tests
- GitHub Actions
- PyPI packaging
