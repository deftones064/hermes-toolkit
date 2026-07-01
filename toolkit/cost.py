# Estimated public/token pricing for Cost v1.
# Units are dollars per 1M tokens.
# Unknown models intentionally fall back to conservative configurable defaults.
PRICING = {
    "gpt-5.5": {
        "label": "GPT-5.5",
        "input_per_million": 1.25,
        "output_per_million": 10.00,
        "cached_input_per_million": 0.125,
    },
    "gpt-5": {
        "label": "GPT-5",
        "input_per_million": 1.25,
        "output_per_million": 10.00,
        "cached_input_per_million": 0.125,
    },
    "gpt-4.1": {
        "label": "GPT-4.1",
        "input_per_million": 2.00,
        "output_per_million": 8.00,
        "cached_input_per_million": 0.50,
    },
    "gpt-4.1-mini": {
        "label": "GPT-4.1 Mini",
        "input_per_million": 0.40,
        "output_per_million": 1.60,
        "cached_input_per_million": 0.10,
    },
    "default": {
        "label": "Estimated Default",
        "input_per_million": 1.25,
        "output_per_million": 10.00,
        "cached_input_per_million": 0.125,
    },
}


def _pricing_from_config(cfg):
    if not cfg:
        return PRICING

    toolkit_cfg = cfg.get("toolkit") or {}
    overrides = toolkit_cfg.get("estimated_pricing") or {}

    if not isinstance(overrides, dict):
        return PRICING

    pricing = {
        key: dict(value)
        for key, value in PRICING.items()
    }

    for key, value in overrides.items():
        if not isinstance(value, dict):
            continue

        base = dict(pricing.get(key, pricing["default"]))
        base.update(
            {
                field: value[field]
                for field in (
                    "label",
                    "input_per_million",
                    "output_per_million",
                    "cached_input_per_million",
                )
                if field in value
            }
        )
        pricing[str(key).lower()] = base

    return pricing


def price_for_model(model_name, pricing=None):
    pricing = pricing or PRICING

    if not model_name:
        return pricing["default"]

    normalized = str(model_name).lower()

    if normalized in pricing:
        return pricing[normalized]

    for key, value in pricing.items():
        if key != "default" and key in normalized:
            return value

    return pricing["default"]


def estimate_call(call, pricing=None):
    price = price_for_model(call.get("model"), pricing=pricing)

    input_tokens = int(call.get("in") or 0)
    output_tokens = int(call.get("out") or 0)
    cached_tokens = int(call.get("cache") or 0)
    billable_input_tokens = max(0, input_tokens - cached_tokens)

    uncached_input_cost = billable_input_tokens / 1_000_000 * price["input_per_million"]
    cached_input_cost = cached_tokens / 1_000_000 * price["cached_input_per_million"]
    output_cost = output_tokens / 1_000_000 * price["output_per_million"]

    estimated_cost = uncached_input_cost + cached_input_cost + output_cost

    no_cache_input_cost = input_tokens / 1_000_000 * price["input_per_million"]
    no_cache_total_cost = no_cache_input_cost + output_cost
    estimated_savings = max(0, no_cache_total_cost - estimated_cost)

    return {
        **call,
        "price_label": price["label"],
        "billable_input_tokens": billable_input_tokens,
        "cached_tokens": cached_tokens,
        "input_cost": uncached_input_cost + cached_input_cost,
        "output_cost": output_cost,
        "estimated_cost": estimated_cost,
        "estimated_savings": estimated_savings,
    }


def build_cost_data(dashboard_data, recent_calls, cfg=None):
    data = dict(dashboard_data)
    pricing = _pricing_from_config(cfg or {})

    estimated_calls = [
        estimate_call(call, pricing=pricing)
        for call in recent_calls
    ]

    total_input_tokens = sum(call["in"] for call in estimated_calls)
    total_output_tokens = sum(call["out"] for call in estimated_calls)
    total_tokens = sum(call["total"] for call in estimated_calls)
    total_cached_tokens = sum(call["cached_tokens"] for call in estimated_calls)
    total_cost = sum(call["estimated_cost"] for call in estimated_calls)
    total_savings = sum(call["estimated_savings"] for call in estimated_calls)

    avg_cost = total_cost / len(estimated_calls) if estimated_calls else 0
    avg_cache = (
        sum(call["pct"] for call in estimated_calls) / len(estimated_calls)
        if estimated_calls
        else 0
    )

    if total_cost < 0.25:
        cost_status = "Low"
        cost_class = "good"
    elif total_cost < 1.00:
        cost_status = "Moderate"
        cost_class = "warn"
    else:
        cost_status = "Elevated"
        cost_class = "bad"

    if total_savings > 0:
        savings_status = "Cache savings active"
        savings_class = "good"
    else:
        savings_status = "No savings detected"
        savings_class = "warn"

    recent_estimated_calls = list(reversed(estimated_calls[-20:]))

    data["cost"] = {
        "calls": recent_estimated_calls,
        "call_count": len(estimated_calls),
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_tokens": total_tokens,
        "total_cached_tokens": total_cached_tokens,
        "avg_cache": avg_cache,
        "total_cost": total_cost,
        "total_savings": total_savings,
        "avg_cost": avg_cost,
        "cost_status": cost_status,
        "cost_class": cost_class,
        "savings_status": savings_status,
        "savings_class": savings_class,
        "pricing_note": "Estimated from recent Hermes API log entries. This is not a billing statement.",
        "pricing_source": "Config override" if cfg and (cfg.get("toolkit") or {}).get("estimated_pricing") else "Built-in estimate table",
    }

    return data
