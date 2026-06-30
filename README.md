# Hermes Toolkit

A utility for managing Hermes Agent settings without manually editing ~/.hermes/config.yaml.

## Features

- Show current configuration
- Switch between model providers
- Apply configuration profiles
- View recent API usage
- Run configuration health checks
- Modify individual settings

## Commands
```
hermes-settings show
hermes-settings status
hermes-settings logs
hermes-settings doctor

hermes-settings profile low-cost
hermes-settings profile balanced
hermes-settings profile premium

hermes-settings model qwen
hermes-settings model gemini
hermes-settings model gpt

hermes-settings set agent.max_turns 30
```

## Installation
```
cp hermes-settings /usr/local/bin/hermes-settings
chmod +x /usr/local/bin/hermes-settings
```
