# Hermes Toolkit

> Administrative toolkit and web dashboard for Hermes Agent.

Hermes Toolkit is an open-source companion application for **Nous Research Hermes Agent** that makes it easier to manage, monitor, and optimize your local Hermes installation.

Instead of manually editing `~/.hermes/config.yaml`, digging through log files, or remembering CLI commands, Hermes Toolkit provides a unified command-line interface and a growing web dashboard for day-to-day administration.

---

# Current Version

**v0.3.0-alpha**

Current features include:

- Configuration management
- Model switching
- Profile management
- Configuration health checks
- Recent API usage analysis
- Token usage statistics
- Web dashboard
- Installation utility
- GitHub project structure
- Automated configuration backups

---

# Screenshots

> *(Coming soon)*

---

# Installation

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

---

# CLI

View current status

```bash
hermes-toolkit status
```

Configuration overview

```bash
hermes-toolkit show
```

Health check

```bash
hermes-toolkit doctor
```

View recent API activity

```bash
hermes-toolkit logs
```

Switch profiles

```bash
hermes-toolkit profile low-cost
hermes-toolkit profile balanced
hermes-toolkit profile premium
```

Switch models

```bash
hermes-toolkit model gpt
hermes-toolkit model gemini
hermes-toolkit model qwen
```

Modify any configuration value

```bash
hermes-toolkit set agent.max_turns 30
```

---

# Web Dashboard

Launch the built-in dashboard:

```bash
hermes-toolkit web --host 0.0.0.0 --port 8088
```

Current dashboard includes:

- Active provider
- Active model
- Prompt usage summary
- Cache health
- Token statistics
- Configuration overview
- Recent API calls

---

# Roadmap

## v0.3

- Improved dashboard
- Charts
- Cost analytics
- Live API activity
- Configuration editor

## v0.4

- Web-based configuration management
- Interactive model switching
- Profile management
- Health scoring
- Recommendations engine

## v0.5

- Home Assistant integration
- Telegram integration
- Session management
- Backup & restore
- Update manager

## v1.0

Hermes Control Center

A complete administrative interface for Hermes Agent.

---

# Project Goals

Hermes Toolkit aims to become the primary administration utility for Hermes Agent by providing:

- Beautiful CLI output
- Rich web interface
- Easy configuration management
- Usage analytics
- Cost optimization
- Health monitoring
- Automation tools

---

# License

MIT

---

# Contributing

Issues, ideas, and pull requests are welcome.

This project is currently in active alpha development.
