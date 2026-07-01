from toolkit.models import MODELS


PROVIDER_LABELS = {
    "openai-codex": "OpenAI Codex",
    "openrouter": "OpenRouter",
    "anthropic": "Anthropic",
    "ollama": "Ollama",
    "google": "Google AI Studio",
}


MODEL_LABELS = {
    "qwen": {
        "name": "Qwen Coder",
        "description": "Coding-focused OpenRouter preset for software development and agentic engineering work.",
        "tier": "Developer",
        "status": "Available",
    },
    "gemini": {
        "name": "Gemini 2.5 Pro",
        "description": "Large-context OpenRouter preset for analysis, planning, and complex reasoning tasks.",
        "tier": "Reasoning",
        "status": "Available",
    },
    "gpt": {
        "name": "GPT-5.5",
        "description": "Primary OpenAI Codex preset for Hermes Toolkit development and high-quality coding sessions.",
        "tier": "Primary",
        "status": "Available",
    },
}


def _build_presets(active_provider, active_model):
    presets = []

    for key, value in MODELS.items():
        provider, model, base_url = value
        meta = MODEL_LABELS.get(key, {})
        is_active = provider == active_provider and model == active_model

        presets.append(
            {
                "id": key,
                "name": meta.get("name", key),
                "description": meta.get("description", "Configured Hermes model preset."),
                "tier": meta.get("tier", "Preset"),
                "status": "Active" if is_active else meta.get("status", "Available"),
                "provider": provider,
                "provider_label": PROVIDER_LABELS.get(provider, provider),
                "model": model,
                "base_url": base_url,
                "is_active": is_active,
            }
        )

    return presets


def _build_providers(presets, active_provider):
    providers = []
    seen = set()

    for preset in presets:
        provider = preset["provider"]
        if provider in seen:
            continue

        provider_presets = [item for item in presets if item["provider"] == provider]
        seen.add(provider)

        providers.append(
            {
                "id": provider,
                "label": PROVIDER_LABELS.get(provider, provider),
                "preset_count": len(provider_presets),
                "is_active": provider == active_provider,
                "models": [item["model"] for item in provider_presets],
            }
        )

    return providers


def build_models_page_data(dashboard_data):
    data = dict(dashboard_data)

    active_provider = (data.get("model") or {}).get("provider")
    active_model = (data.get("model") or {}).get("default")
    active_base_url = (data.get("model") or {}).get("base_url")

    presets = _build_presets(active_provider, active_model)
    providers = _build_providers(presets, active_provider)

    data["models_page"] = {
        "active_provider": active_provider,
        "active_provider_label": PROVIDER_LABELS.get(active_provider, active_provider),
        "active_model": active_model,
        "active_base_url": active_base_url,
        "presets": presets,
        "providers": providers,
        "preset_count": len(presets),
        "provider_count": len(providers),
        "mode": "Safe model switching",
        "note": "Applying a model updates Hermes configuration only. It does not restart services.",
    }

    return data
