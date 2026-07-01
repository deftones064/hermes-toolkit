from toolkit.cost import build_cost_data, estimate_call, price_for_model


def test_price_for_model_matches_partial_model_name():
    price = price_for_model("openai/gpt-5.5")

    assert price["label"] == "GPT-5.5"


def test_price_for_model_uses_default_for_unknown_model():
    price = price_for_model("unknown/model")

    assert price["label"] == "Estimated Default"


def test_estimate_call_uses_cached_input_discount():
    call = {
        "num": 1,
        "provider": "openai-codex",
        "model": "gpt-5.5",
        "in": 1000,
        "out": 100,
        "total": 1100,
        "cache": 500,
        "pct": 50,
    }

    estimated = estimate_call(call)

    assert estimated["billable_input_tokens"] == 500
    assert estimated["cached_tokens"] == 500
    assert estimated["estimated_cost"] > 0
    assert estimated["estimated_savings"] > 0


def test_build_cost_data_shape():
    calls = [
        {
            "num": 1,
            "provider": "openai-codex",
            "model": "gpt-5.5",
            "in": 1000,
            "out": 100,
            "total": 1100,
            "cache": 500,
            "pct": 50,
        },
        {
            "num": 2,
            "provider": "openrouter",
            "model": "qwen/qwen3-coder",
            "in": 2000,
            "out": 200,
            "total": 2200,
            "cache": 0,
            "pct": 0,
        },
    ]

    data = build_cost_data({}, calls)
    cost = data["cost"]

    assert cost["calls"]
    assert cost["call_count"] == 2
    assert cost["total_input_tokens"] == 3000
    assert cost["total_output_tokens"] == 300
    assert cost["total_tokens"] == 3300
    assert cost["total_cost"] > 0
    assert cost["avg_cost"] > 0
    assert cost["pricing_note"] == "Estimated from recent Hermes API log entries. This is not a billing statement."


def test_build_cost_data_handles_no_calls():
    data = build_cost_data({}, [])
    cost = data["cost"]

    assert cost["calls"] == []
    assert cost["call_count"] == 0
    assert cost["total_cost"] == 0
    assert cost["avg_cost"] == 0
    assert cost["cost_status"] == "Low"


def test_build_cost_data_uses_configured_pricing_override():
    calls = [
        {
            "num": 1,
            "provider": "openai-codex",
            "model": "gpt-5.5",
            "in": 1_000_000,
            "out": 0,
            "total": 1_000_000,
            "cache": 0,
            "pct": 0,
        },
    ]

    cfg = {
        "toolkit": {
            "estimated_pricing": {
                "gpt-5.5": {
                    "label": "GPT-5.5 Custom",
                    "input_per_million": 2.0,
                    "output_per_million": 10.0,
                    "cached_input_per_million": 0.2,
                }
            }
        }
    }

    data = build_cost_data({}, calls, cfg=cfg)
    cost = data["cost"]

    assert cost["calls"][0]["price_label"] == "GPT-5.5 Custom"
    assert cost["total_cost"] == 2.0
    assert cost["pricing_source"] == "Config override"


def test_build_cost_data_reports_builtin_pricing_source():
    data = build_cost_data({}, [], cfg={})

    assert data["cost"]["pricing_source"] == "Built-in estimate table"
