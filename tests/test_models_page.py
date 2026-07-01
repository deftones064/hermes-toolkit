from toolkit.models import MODELS
from toolkit.models_page import build_models_page_data


def test_build_models_page_data_shape():
    provider, model, base_url = MODELS["gpt"]

    data = build_models_page_data(
        {
            "model": {
                "provider": provider,
                "default": model,
                "base_url": base_url,
            }
        }
    )

    models_page = data["models_page"]

    assert models_page["active_provider"] == provider
    assert models_page["active_model"] == model
    assert models_page["preset_count"] == len(MODELS)
    assert models_page["provider_count"] >= 1
    assert models_page["mode"] == "Safe model switching"
    assert models_page["note"] == "Applying a model updates Hermes configuration only. It does not restart services."


def test_build_models_page_data_marks_active_preset():
    provider, model, base_url = MODELS["gpt"]

    data = build_models_page_data(
        {
            "model": {
                "provider": provider,
                "default": model,
                "base_url": base_url,
            }
        }
    )

    active_presets = [
        preset for preset in data["models_page"]["presets"]
        if preset["is_active"]
    ]

    assert len(active_presets) == 1
    assert active_presets[0]["id"] == "gpt"
    assert active_presets[0]["status"] == "Active"


def test_build_models_page_data_marks_active_provider():
    provider, model, base_url = MODELS["gpt"]

    data = build_models_page_data(
        {
            "model": {
                "provider": provider,
                "default": model,
                "base_url": base_url,
            }
        }
    )

    active_providers = [
        item for item in data["models_page"]["providers"]
        if item["is_active"]
    ]

    assert len(active_providers) == 1
    assert active_providers[0]["id"] == provider


def test_build_models_page_data_handles_unconfigured_model():
    data = build_models_page_data({})

    models_page = data["models_page"]

    assert models_page["active_provider"] is None
    assert models_page["active_provider_label"] is None
    assert models_page["active_model"] is None
    assert models_page["preset_count"] == len(MODELS)
    assert not any(preset["is_active"] for preset in models_page["presets"])
